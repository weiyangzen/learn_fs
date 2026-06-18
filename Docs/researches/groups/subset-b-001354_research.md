# subset-b-001354 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v3_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v3_0.c

## Purpose
Implements the AMDGPU SDMA v3.0/v3.1 IP block for VI-era ASICs. It loads SDMA firmware, applies per-ASIC golden registers, initializes SDMA gfx rings, exposes SDMA packet emitters for IBs, fences, VM page table updates, HDP/VM flushes, and buffer copy/fill, and plugs the block into the AMDGPU IP lifecycle.

## APIs, Types, And Functions
The exported objects are `sdma_v3_0_ip_block` and `sdma_v3_1_ip_block`. Important internal tables include `sdma_v3_0_ip_funcs`, `sdma_v3_0_ring_funcs`, `sdma_v3_0_vm_pte_funcs`, `sdma_v3_0_buffer_funcs`, and IRQ handler tables. Key functions are firmware loading/freeing, `sdma_v3_0_gfx_resume()`, `sdma_v3_0_start()`, ring pointer helpers, packet emitters, `sdma_v3_0_ring_test_ring()`, `sdma_v3_0_ring_test_ib()`, lifecycle callbacks, soft-reset callbacks, clock-gating helpers, and trap/illegal-instruction interrupt handlers.

## Control Flow
`early_init` chooses one or two SDMA instances, requests chip-specific firmware, installs ring/buffer/VM/IRQ function tables, and records firmware versions and burst-NOP capability. `sw_init` registers legacy interrupt IDs and creates one gfx SDMA ring per instance, using doorbells on bare metal and pollmem for SR-IOV VF. `hw_init` programs golden registers and starts the block. Start disables context switching and halts SDMA, programs each gfx ring base, rptr/wptr writeback, doorbell or polling, enables RB/IB, unhalts engines, enables context switching, then tests every ring. Suspend/fini paths disable context switching and halt the engines.

## State And Persistence
Runtime state lives in `adev->sdma`: instance count, firmware pointers/versions, ring structs, `burst_nop`, and `srbm_soft_reset`. Ring state persists in GPU-visible ring buffers and writeback slots for rptr/wptr; firmware blobs are retained in memory until `sw_fini`. There is no filesystem persistence beyond kernel firmware loading. Soft reset caches the SRBM reset mask in `adev->sdma.srbm_soft_reset`; post reset reinitializes gfx rings. Compute/RLC queue state is not implemented in this file.

## Dependencies And Integration
This file depends on AMDGPU core ring, IB, VM, fence, IRQ, firmware, and TTM buffer movement helpers, plus VI/GMC/GFX/BIF register definitions and `tonga_sdma_pkt_open.h` packet macros. It integrates with `amdgpu_sdma_set_vm_pte_scheds()` for VM updates, `adev->mman.buffer_funcs` for DMA copy/fill, `amdgpu_irq_add_id()` for trap and illegal instruction events, `amdgpu_gmc_emit_flush_gpu_tlb()` for VM flushes, and `amdgpu_ring_test_helper()` for bring-up validation.

## Risks And Test Signals
Important risks are ASIC-specific firmware name selection, one-instance Stoney behavior, doorbell versus pollmem write-pointer paths, alignment requirements for IBs and fences, incomplete RLC compute queue support, and soft-reset recovery that only restores gfx rings. Big-endian swapping paths are conditional and likely low-coverage. Test signals include successful firmware load, ring tests writing `0xDEADBEEF`, IB fence completion, VM PTE update stress, trap IRQ fence processing, illegal instruction scheduler faults, suspend/resume, SR-IOV VF pollmem behavior, and clock-gating flag checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v3_0.h

## Purpose
Declares the public SDMA v3 IP block descriptors used by the AMDGPU device discovery and IP block registration code. It is the header-level handoff for SDMA v3.0 and v3.1 support implemented in `sdma_v3_0.c`.

## APIs, Types, And Functions
The header exports `extern const struct amdgpu_ip_block_version sdma_v3_0_ip_block;` and `sdma_v3_1_ip_block;`. It introduces no new types, inline helpers, macros, or functions beyond the include guard.

## Control Flow
There is no runtime control flow in the header. Consumers include it so platform/IP discovery code can reference the correct `amdgpu_ip_block_version` object and therefore bind the SDMA v3 lifecycle callbacks.

## State And Persistence
The declarations themselves are stateless. The actual persistent driver state is in the `amdgpu_device` SDMA fields initialized by the implementation file.

## Dependencies And Integration
It relies on the including translation unit already knowing `struct amdgpu_ip_block_version`. Integration is intentionally narrow: it exposes only the block descriptors, keeping all register and packet details private to the implementation.

## Risks And Test Signals
Risk is limited to declaration/definition drift or missing inclusion where IP discovery expects these symbols. Build/link success is the main test signal; runtime validation comes from the v3.0/v3.1 IP block registration and ring bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v3_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c

## Purpose
Implements the AMDGPU SDMA v4.0 family IP block for Vega/Raven/Arcturus/Aldebaran-era devices. It manages firmware, SoC15 register programming, gfx and optional page SDMA rings, VM PTE emitters, buffer copy/fill, interrupts, RAS, power/clock gating, and debug register dumps.

## APIs, Types, And Functions
The primary exported objects are `sdma_v4_0_ip_funcs` and `sdma_v4_0_ip_block`. Internal function tables include `sdma_v4_0_ring_funcs`, `sdma_v4_0_page_ring_funcs`, `sdma_v4_0_vm_pte_funcs`, `sdma_v4_0_buffer_funcs`, `sdma_v4_4_buffer_funcs`, IRQ source handlers, and `sdma_v4_0_ras`. Major functions cover register offset mapping, firmware init/load, golden register programming, ULV setup, ring pointer access, gfx/page resume, microcode loading, IP lifecycle, trap/ECC/VM-hole/doorbell/poll-timeout/SRBM-write interrupt handling, clock/power gating, RAS count/reset, and IP state dump/print.

## Control Flow
`early_init` loads firmware through shared SDMA helpers, decides whether firmware supports a page queue, then installs ring, buffer, VM, IRQ, and RAS hooks. `sw_init` registers per-instance trap and ECC IRQs, optionally registers extra fault/debug IRQs for five/eight-instance devices, initializes gfx rings and optional page rings with 64-bit doorbells, assigns VM hubs, initializes RAS, and allocates an IP dump buffer. `hw_init` disables APU SDMA power gating, programs golden registers outside SR-IOV, and calls `sdma_v4_0_start()`. Start loads microcode directly unless PSP loading is active, unhalts engines, enables context switching, programs gfx/page rings, enables UTC L1, resumes RLC/power-gating support, and tests all active rings.

## State And Persistence
State is kept in `adev->sdma.instance[]`, per-ring writeback and doorbell fields, `adev->sdma.has_page_queue`, firmware instance contexts, RAS registration, and `adev->sdma.ip_dump`. Firmware context may be shared for Arcturus/Aldebaran. Page queue support is a persistent runtime capability selected from IP version and firmware version. RAS counters are hardware EDC counters read or read-cleared by the driver. IP dump state is an in-memory snapshot buffer allocated at `sw_init` and populated by `dump_ip_state`.

## Dependencies And Integration
The file depends on SoC15 register-offset macros, SDMA packet macros, AMDGPU firmware and ring infrastructure, NBIO HDP flush offsets, GMC VM flush helpers, DPM/SMU power-gating hooks, RAS helpers, and the v4.4 RAS helper exported by `sdma_v4_4.c`. It integrates with TTM through `adev->mman.buffer_funcs`, VM page-table scheduling through `amdgpu_sdma_set_vm_pte_scheds()`, scheduler fault handling through illegal-instruction IRQs, and RAS through `amdgpu_sdma_ras_sw_init()` and per-IP callbacks.

## Risks And Test Signals
Risks include numerous ASIC-specific golden setting paths, firmware-version gating for page queues, SR-IOV differences, page-queue doorbell offset differences between Vega10 and newer parts, Arcturus MMHUB1 routing for instances 5-7, unimplemented `soft_reset`, and subtle count-minus-one packet length encoding. Useful tests include firmware load on each supported IP version, gfx/page ring tests, IB scheduling, VM update workloads, TMZ copy paths, interrupt injection or fault logging for VM holes and bad doorbells, RAS EDC counter query/reset, suspend/resume including S0ix paths, power/clock gating toggles, and IP dump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.h

## Purpose
Declares the SDMA v4.0 IP function table and IP block descriptor for use by AMDGPU IP discovery and registration code.

## APIs, Types, And Functions
The header exports `extern const struct amd_ip_funcs sdma_v4_0_ip_funcs;` and `extern const struct amdgpu_ip_block_version sdma_v4_0_ip_block;`. It adds no local types, packet helpers, register definitions, or inline logic.

## Control Flow
No control flow exists in the header. Runtime behavior is selected when other code binds `sdma_v4_0_ip_block` or directly refers to `sdma_v4_0_ip_funcs`.

## State And Persistence
The header is stateless. Persistent SDMA state is owned by `struct amdgpu_device` and initialized by `sdma_v4_0.c`.

## Dependencies And Integration
It assumes declarations for `struct amd_ip_funcs` and `struct amdgpu_ip_block_version` are visible to the includer. It serves as the public C interface between IP discovery code and the SDMA v4.0 implementation.

## Risks And Test Signals
Risk is limited to missing symbol definitions or ABI drift with the implementation. Build/link coverage and successful SDMA v4.0 IP registration are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c

## Purpose
Provides a focused SDMA v4.4 RAS implementation shared by the broader SDMA v4.0 driver for IP version 4.4.0-class hardware. It maps SDMA instance register offsets, decodes EDC counter fields, reports RAS error counts, and clears hardware counters.

## APIs, Types, And Functions
The exported object is `struct amdgpu_sdma_ras sdma_v4_4_ras`. Internal data includes `sdma_v4_4_ras_fields`, a table of named single-error-detection fields across `regSDMA0_EDC_COUNTER` and `regSDMA0_EDC_COUNTER2`. Key helpers are `sdma_v4_4_get_reg_offset()`, `sdma_v4_4_get_ras_error_count()`, per-instance query/reset functions, aggregate query/reset functions, and `sdma_v4_4_ras_hw_ops`.

## Control Flow
RAS query iterates every SDMA instance, reads the two EDC counter registers through a helper that converts instance number to the correct register base, decodes nonzero field counts, logs detected fields, and accumulates counts into `ras_err_data`. Reset checks SDMA RAS support and writes zero to both EDC counter registers for each instance. The exported RAS block supplies these operations to the common AMDGPU SDMA RAS layer.

## State And Persistence
The file does not own long-lived software state beyond static tables and the exported `sdma_v4_4_ras` descriptor. Hardware EDC counters are the persistent state being queried and reset. Counts are folded into caller-provided `ras_err_data`; the file sets CE count to zero and accumulates SDMA single-error-detection counts as UE count according to the implementation comments.

## Dependencies And Integration
Depends on AMDGPU core definitions, SoC15 register access, SDMA 4.4.0 register masks, and AMDGPU RAS types. It is selected by `sdma_v4_0_set_ras_funcs()` for IP version 4.4.0, which makes this file an extension of the v4.0 SDMA implementation rather than a standalone IP block.

## Risks And Test Signals
Risks include hard-coded register offsets for up to five instances, any mismatch between field table masks and actual IP revision, and the unusual classification of single-error-detection counts into UE rather than CE. The field named for `SDMA_MC_RDRET_BUF_SED` uses the `SDMA_MC_WR_ADDR_FIFO_SED` field macro, which is worth auditing against hardware headers. Test signals include injected or harvested EDC counter values, correct per-instance logging, successful zeroing of counters, and no register-offset failures on all supported instance counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.h

## Purpose
Declares the SDMA v4.4 RAS descriptor so other SDMA implementation files can attach the correct RAS operations for v4.4 hardware.

## APIs, Types, And Functions
The sole exported symbol is `extern struct amdgpu_sdma_ras sdma_v4_4_ras;`. The header defines no functions or additional types.

## Control Flow
There is no local control flow. The declaration is consumed by `sdma_v4_0.c`, which assigns `adev->sdma.ras` to this descriptor for matching IP versions.

## State And Persistence
The header is stateless. Runtime RAS state and hardware counter interaction live in `sdma_v4_4.c` and the common AMDGPU RAS core.

## Dependencies And Integration
It assumes `struct amdgpu_sdma_ras` is already declared by included AMDGPU headers. Its integration point is deliberately narrow: expose only the RAS block descriptor, not the counter decoding helpers.

## Risks And Test Signals
Risk is declaration/definition mismatch or missing inclusion when v4.4 RAS is selected. Build/link success and SDMA RAS initialization on v4.4 hardware are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.c

## Purpose
Implements the AMDGPU SDMA v4.4.2-family IP block for newer multi-AID/XCP-capable GPUs. It manages shared firmware, per-instance register mapping, gfx and optional page rings, queue stop/restore and per-queue reset support, XCP suspend/resume, VM and buffer packet emitters, interrupts, clock gating, debug dumps, and newer RAS/ACA integration.

## APIs, Types, And Functions
Exports `sdma_v4_4_2_ip_funcs`, `sdma_v4_4_2_ip_block`, and `sdma_v4_4_2_xcp_funcs`. Internal tables include `sdma_reg_list_4_4_2`, `sdma_v4_4_2_ring_funcs`, `sdma_v4_4_2_page_ring_funcs`, `sdma_v4_4_2_vm_pte_funcs`, `sdma_v4_4_2_buffer_funcs`, `sdma_v4_4_2_sdma_funcs`, IRQ source tables, RAS register/memory lists, and ACA bank ops. Key routines handle firmware init/load, instance-masked start/stop, ring pointer access through writeback offsets, ring/page resume with restore semantics, queue reset, trap/ECC/fault IRQ processing, reset mask updates, XCP callbacks, and RAS query/reset/late-init.

## Control Flow
`early_init` loads one shared firmware image for v4.4.2/4.4.4/4.4.5, disables page queues because firmware support currently returns false, and installs callbacks. `sw_init` registers IRQs for the number of SDMA instances per AID, initializes each SDMA instance with doorbells, AID-derived MMHUB routing, reset mutexes, guilty flags, ring names, and optional page rings, initializes RAS and sysfs reset-mask state, and allocates IP dump memory. `hw_init` builds a full instance mask, programs golden GB address registers outside SR-IOV, then starts all instances. Instance start optionally loads microcode, enables engines/context switch, programs rings, enables UTC L1 and context-empty interrupts for older v4.4.x revisions, runs RLC resume, and tests rings.

## State And Persistence
State is richer than earlier SDMA versions: each instance stores `aid_id`, reset mutex, guilty queue flags, function hooks, cached read pointers, firmware context, and ring/page structs. Queue stop caches rptr values before reset because registers are cleared; restore can skip bad commands for a guilty queue by setting rptr to current wptr or continue from cached rptr for non-guilty queues. Reset capabilities are accumulated in `adev->sdma.supported_reset` after checking GC IP, MEC firmware version, DPM support, and debug disable flags. RAS state is held in common RAS data structures; ACA binding adds cached bank-error reporting. IP dumps are in-memory snapshots.

## Dependencies And Integration
Depends on AMDGPU core, XCP, reset, firmware, ring, KFD suspend/resume, DPM SDMA reset, SoC15 register access, SDMA packet macros, NBIO HDP flush offsets, GMC VM flush helpers, RAS, SMUIO MCM topology, and ACA error-bank infrastructure. It integrates with `amdgpu_sdma_reset_engine()`, per-ring `.reset`, `amdgpu_sdma_sysfs_reset_mask_init()`, `amdgpu_xcp_ip_funcs`, `amdgpu_sdma_ras_late_init()`, and `amdgpu_ras_bind_aca()`.

## Risks And Test Signals
High-risk areas are logical-to-physical SDMA instance mapping via `GET_INST`, AID/node mapping in trap IRQ handling, SR-IOV client-ID remapping, restore behavior after queue reset, guilty queue detection via context status, firmware/PMFW/MEC gating for per-queue reset, and `soft_reset` still being a TODO at the IP-block level. `BUG_ON` in fence alignment is harsher than v4.0's warning. Test signals include firmware load, full and XCP instance-mask start/stop, ring/IB tests, queue reset under timeout with KFD suspend/resume, sysfs reset-mask exposure, trap IRQ routing for multi-AID nodes, VM-hole/doorbell/poll/SRBM/context-empty debug IRQ logs, RAS UE query/reset, ACA bank parsing, clock-gating toggles, and IP dump coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.h

## Purpose
Declares the SDMA v4.4.2 IP function table, IP block descriptor, and XCP callback table for newer AMDGPU SDMA hardware.

## APIs, Types, And Functions
The header exports `extern const struct amd_ip_funcs sdma_v4_4_2_ip_funcs;`, `extern const struct amdgpu_ip_block_version sdma_v4_4_2_ip_block;`, and `extern struct amdgpu_xcp_ip_funcs sdma_v4_4_2_xcp_funcs;`. It defines no local helpers or structs.

## Control Flow
No executable flow is present. Consumers use these declarations to register the normal SDMA IP lifecycle and to attach XCP partition suspend/resume callbacks implemented in `sdma_v4_4_2.c`.

## State And Persistence
The declarations are stateless. Persistent runtime state belongs to `adev->sdma` instances, ring structures, XCP partition state, reset-mask state, and RAS structures in the implementation.

## Dependencies And Integration
The includer must have declarations for `struct amd_ip_funcs`, `struct amdgpu_ip_block_version`, and `struct amdgpu_xcp_ip_funcs`. The header is the public interface between IP discovery/XCP code and the v4.4.2 implementation.

## Risks And Test Signals
Risk is limited to stale extern declarations or missing symbol definitions. Build/link success, normal SDMA v4.4.2 IP registration, and XCP suspend/resume callback binding validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v4_4_2.h -->
