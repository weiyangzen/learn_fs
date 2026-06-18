# subset-b-001334 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c

## Purpose
`gfx_v12_1.c` is the AMDGPU GFX 12.1 IP block implementation for GC 12.1.0 hardware. It wires the GFX block into the common AMDGPU IP lifecycle, initializes RLC/MEC/compute queue state, loads firmware through PSP, direct, or RLC backdoor autoload paths, emits PM4 packets for compute/KIQ rings, handles GFX interrupts and RAS poison events, and exposes XCP suspend/resume hooks for partitioned devices.

The file is compute-heavy rather than graphics-ring-heavy: early init can disable kernel queues based on `amdgpu_user_queue`, compute rings are allocated per XCC, KIQ/MES paths are supported, and most PM4 emission helpers target compute and KIQ rings.

## Important APIs, types, and functions
Key exported objects are `gfx_v12_1_ip_block`, which registers `gfx_v12_1_ip_funcs` under `AMD_IP_BLOCK_TYPE_GFX`, and `gfx_v12_1_xcp_funcs`, which exposes per-partition suspend/resume callbacks. Internal dispatch tables include `gfx_v12_1_gfx_funcs`, `gfx_v12_1_rlc_funcs`, `gfx_v12_1_ring_funcs_compute`, `gfx_v12_1_ring_funcs_kiq`, IRQ source function tables, and `gfx_v12_1_kiq_pm4_funcs`.

Lifecycle functions are the central API surface:

- `gfx_v12_1_early_init()` chooses queue mode, installs GFX/RLC/ring/IRQ/MQD/IMU function tables, initializes RLCG register access metadata, and requests firmware.
- `gfx_v12_1_sw_init()` registers IRQ IDs, initializes RLC clear-state BOs, MEC HPD/EOP BOs, compute rings, KIQ/MQD software state, firmware staging BOs, GPU config, and sysfs.
- `gfx_v12_1_hw_init()` performs firmware autoload/direct preparation, waits for RLC autoload when needed, enables GFXHUB/GART, programs golden registers and constants, resumes RLC and CP, then tests compute rings.
- `gfx_v12_1_hw_fini()`, `gfx_v12_1_suspend()`, `gfx_v12_1_resume()`, and `gfx_v12_1_sw_fini()` undo hardware/software state.

Firmware/RLC functions include `gfx_v12_1_init_microcode()`, `gfx_v12_1_init_toc_microcode()`, `gfx_v12_1_rlc_autoload_buffer_init()`, `gfx_v12_1_parse_rlc_toc()`, `gfx_v12_1_rlc_backdoor_autoload_copy_*()`, `gfx_v12_1_rlc_backdoor_autoload_enable()`, `gfx_v12_1_xcc_rlc_load_microcode()`, `gfx_v12_1_xcc_rlc_resume()`, and `gfx_v12_1_wait_for_rlc_autoload_complete()`. MEC/CP setup is handled by `gfx_v12_1_init_cp_compute_microcode_bo()`, `gfx_v12_1_xcc_cp_compute_load_microcode_rs64()`, `gfx_v12_1_xcc_cp_set_doorbell_range()`, `gfx_v12_1_compute_mqd_init()`, `gfx_v12_1_xcc_kiq_resume()`, `gfx_v12_1_xcc_kcq_resume()`, and `gfx_v12_1_cp_resume()`.

PM4/ring helpers include KIQ queue resource/map/unmap/query/TLB-invalidate helpers, `gfx_v12_1_wait_reg_mem()`, `gfx_v12_1_ring_test_ring()`, `gfx_v12_1_ring_test_ib()`, read/write pointer accessors, `gfx_v12_1_ring_emit_ib_compute()`, fence emission for compute and KIQ, VM flush, register read/write/wait packet emitters, and `gfx_v12_1_emit_mem_sync()`.

Hardware topology helpers include `gfx_v12_1_get_cu_info()`, `gfx_v12_1_get_sa_active_bitmap()`, `gfx_v12_1_get_rb_active_bitmap()`, `gfx_v12_1_setup_rb()`, `gfx_v12_1_constants_init()`, `gfx_v12_1_xcc_select_se_sh()`, and `gfx_v12_1_ih_to_xcc_inst()`.

## Control flow
The normal bring-up path is `early_init -> sw_init -> hw_init -> late_init`. `early_init` establishes function-pointer contracts before firmware is loaded. `sw_init` computes the MEC topology for GC 12.1.0 as one MEC, four pipes, eight queues per pipe, caps requested compute rings, allocates persistent BOs, initializes KIQ if MES KIQ is not used, and prepares either an RLC autoload BO or direct MEC firmware BOs depending on `adev->firmware.load_type`.

`hw_init` branches by firmware load mode. RLC backdoor autoload copies SDMA/GFX/MES/TOC firmware into a VRAM autoload buffer and enables RLC bootload. Direct loading loads IMU firmware and disables GPA mode on each XCC before later direct RLC/MEC programming. PSP and backdoor modes wait for RLC autoload completion. After that, the function enables GFXHUB/GART, initializes golden registers and constants, initializes doorbells, resumes RLC, reapplies TCP harvest hooks, resumes CP queues, and ring-tests every compute ring.

CP resume first reconciles XCP partition mode. SR-IOV VFs query the active partition mode and initialize XCP manager state; non-VF devices may switch to `amdgpu_user_partt_mode` if no mode exists. `gfx_v12_1_xcc_cp_resume()` then optionally direct-loads MEC firmware, enables GUI idle interrupts for PSP loading, programs doorbell ranges, enables compute, initializes MES KIQ or legacy KIQ, resumes all KCQ rings, and runs `amdgpu_ring_test_helper()` for each ring.

Suspend/fini flow disables queue interrupts, tears down each XCC with `gfx_v12_1_xcc_fini()`, disables GART, marks `is_poweron` false, and later frees rings, KIQ/MQD state, RLC/MEC BOs, firmware, autoload buffers, and sysfs state. XCP suspend/resume run the same per-XCC pieces on a caller-provided instance mask.

IRQ flow is table driven. EOP IRQs either route MES user queue doorbell fences to `amdgpu_userq_process_fence_irq()` or decode ME/pipe/queue/XCC from the IV and call `amdgpu_fence_process()` on matching compute rings. Privileged register/instruction faults log an error and fault the matching DRM scheduler. RLC poison IRQs aggregate FED status across XCCs, classify SDMA-related errors when present, and dispatch a RAS manager interrupt requesting mode2 reset.

## State and persistence behavior
Persistent driver state is stored primarily under `adev->gfx`, `adev->gfx.rlc`, `adev->gfx.mec`, `adev->gfx.kiq[]`, `adev->mqds[]`, `adev->psp.toc`, and `adev->gfxhub`. The file allocates kernel BOs for RLC clear state and jump tables, MEC HPD/EOP storage, direct MEC instruction/data firmware, and RLC autoload firmware. Queue state persists through ring objects, MQD objects, doorbell indices, writeback addresses, scheduler readiness, and MQD backups used across reset/suspend.

Register programming is XCC-aware. Most hardware writes use `GET_INST(GC, xcc_id)` and loop over `NUM_XCC(adev->gfx.xcc_mask)`. GRBM/SRBM selection is protected by `srbm_mutex` or `grbm_idx_mutex` when changing selected ME/pipe/queue/VMID or SE/SA/instance. RLCG register access control caches per-GC-instance register offsets and marks RLCG access supported.

`rlc_autoload_info` is a static table populated from the PSP TOC and reused by the backdoor autoload copy path. Because it is file-static and indexed by firmware ID, stale content would matter if the TOC parse ever failed partway or if multiple devices with different TOCs shared the same module lifetime; current code overwrites entries for IDs present in the parsed TOC and computes total size from the table.

Hardware-facing state includes CP/MEC/RLC enable bits, RLC safe mode, clock-gating override registers, GFXOFF control, VMID SH_MEM apertures, trap enablement for KFD VMIDs, CU/RB active masks, GFXHUB TLB state, doorbell ranges, and per-ring read/write pointers. The write pointer path requires doorbells and BUGs if doorbells are unavailable.

## Dependencies and integration points
The file depends on AMDGPU core device, ring, IB, fence, IRQ, GFX, PSP, SMU, GFXHUB/GMC, NBIO, MES, RAS, XCP, IMU, and user queue fence infrastructure. Hardware definitions come from generated GC 12.1 offset/mask headers, SOC24 firmware IDs, IRQ source IDs, clear-state data, and `v12_structs.h` for `struct v12_1_compute_mqd`.

Firmware dependencies include `amdgpu/gc_12_1_0_mec.bin`, `amdgpu/gc_12_1_0_rlc.bin`, the decoded TOC firmware for backdoor autoload, optional IMU firmware, MES firmware for both pipes, and SDMA firmware copied into the RLC autoload buffer. Firmware header parsing uses AMDGPU common header structures and little-endian conversion helpers.

Runtime integration points include `amdgpu_irq_add_id/get/put`, `amdgpu_ring_init/fini/alloc/commit/write`, `amdgpu_ib_get/schedule/free`, `dma_fence_wait_timeout`, `amdgpu_gfx_*` helpers for KIQ/KCQ/MQD/CU parsing/RLC CSB, `amdgpu_mes_*` helpers for MES KIQ and legacy queue unmap, `amdgpu_xcp_*` partition helpers, `amdgpu_gmc_emit_flush_gpu_tlb`, `amdgpu_ras_mgr_dispatch_interrupt`, and power management through `amdgpu_gfx_off_ctrl`.

## Risks and edge cases
The firmware paths are tightly ordered and mode-sensitive. Direct, PSP, and RLC backdoor autoload share later RLC/CP resume code but require different staging and register programming. A missed wait, stale TOC entry, wrong firmware header version, or wrong XCC replication count can leave RLC/MEC partially initialized.

Several failure paths rely on timeouts against hardware status (`adev->usec_timeout`, 50 ms MEC cache invalidation waits, RLC autoload completion). These are good failure signals but can be sensitive to emulation mode and slow hardware. `gfx_v12_1_wait_for_rlc_autoload_complete()` calls the per-XCC wait in a loop but does not propagate its return value, so a timeout inside an XCC helper is currently ignored by the aggregate function.

The code assumes GC 12.1.0 topology limits in multiple places. `gfx_v12_1_get_cu_info()` rejects more than two shader engines or two shader arrays per SE. `gfx_v12_1_get_xccs_per_xcp()` is a placeholder returning 1, so partition behavior may be incomplete for future multi-XCC-per-XCP configurations. Some functions are stubs or TODOs (`tcp_harvest`, `get_tcc_info`, power-gating helpers, XCP golden register init).

Queue and ring code depends on doorbells, MQD layout, XCC doorbell range math, and correct ME/pipe/queue mappings. `gfx_v12_1_ring_set_wptr_compute()` BUGs on non-doorbell rings. The ring IB path has a documented workaround for GDS wave ID mismatch and hardware deadlock risk. KIQ unmap has a special MES fallback when MES is enabled and the legacy KIQ scheduler is not ready.

Synchronization risk is concentrated around GRBM/SRBM selection and register shadowing. Most selection sequences take the expected mutexes, but any future register programming added outside those regions could race with queue or VMID selection. Endianness comments indicate unresolved checks for read/write pointers on big-endian systems.

## Test signals
Built-in runtime tests are `gfx_v12_1_ring_test_ring()` and `gfx_v12_1_ring_test_ib()`. The ring test writes `SCRATCH_REG0` through KIQ or compute PM4 and polls for `0xDEADBEEF`; the IB test schedules a `WRITE_DATA` IB to writeback memory and waits on a fence. CP resume calls `amdgpu_ring_test_helper()` for each compute ring.

Additional signals are RLC autoload timeout logs, MEC cache invalidation error logs, firmware request failures, `get_gb_addr_config()` warnings, GFX idle polling via `gfx_v12_1_wait_for_idle()`, scheduler faults on privileged access IRQs, RAS dispatch on RLC poison IRQs, and IRQ enable/disable return values in late init and hw fini. Effective validation should exercise PSP, direct, and RLC backdoor firmware modes; SR-IOV VF and bare-metal paths; MES KIQ and legacy KIQ; user queues with `disable_kq`; suspend/resume and GPU reset; XCP partition switch/resume; TLB flush and fence emission; and error injection for illegal packets and RLC poison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.h

## Purpose
`gfx_v12_1.h` is the public local header for the GFX 12.1 AMDGPU IP implementation. It does not define hardware logic itself; it declares the two cross-file symbols that other AMDGPU initialization code needs in order to register the GFX 12.1 IP block and invoke XCP partition callbacks.

## Important APIs and types
The header exports `extern const struct amdgpu_ip_block_version gfx_v12_1_ip_block;`, implemented in `gfx_v12_1.c` with type `AMD_IP_BLOCK_TYPE_GFX`, version 12.1.0, and the `gfx_v12_1_ip_funcs` lifecycle table.

It also exports `extern struct amdgpu_xcp_ip_funcs gfx_v12_1_xcp_funcs;`, implemented in `gfx_v12_1.c` with `.suspend` and `.resume` hooks for XCP instance masks. Consumers use this to coordinate per-partition GFX suspend/resume without knowing the internal per-XCC sequence.

## Control flow and integration
The include guard `__GFX_V12_1_H__` prevents duplicate declarations. Driver discovery or IP-version selection code can include this header, then reference `gfx_v12_1_ip_block` when building the AMDGPU IP block list for GC 12.1 devices. XCP management code can reference `gfx_v12_1_xcp_funcs` to suspend or resume selected XCC instances during partition transitions.

## State and persistence behavior
The header owns no state. It provides external linkage to stateful implementations in `gfx_v12_1.c`; all persistent device state remains in `struct amdgpu_device`, IP block registration tables, and XCP callback consumers.

## Dependencies
The declarations require that included translation units already know `struct amdgpu_ip_block_version` and `struct amdgpu_xcp_ip_funcs`, normally through AMDGPU core headers. This header intentionally avoids including those definitions itself, matching a lightweight internal-declaration pattern.

## Risks and test signals
The main risk is declaration drift: if `gfx_v12_1.c` changes the exported symbol names, constness, or linkage, consumers including this header will fail to build. Because the header is minimal, compile/link coverage is the primary test signal. Runtime coverage comes indirectly from successful GC 12.1 IP registration and XCP suspend/resume callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1_pkt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1_pkt.h

## Purpose
`gfx_v12_1_pkt.h` defines PM4 packet constructors, packet decoders, opcode constants, and bitfield helper macros for GFX 12.1 command processor packets. `gfx_v12_1.c` uses these macros when emitting KIQ, compute, synchronization, fence, TLB invalidate, queue map/unmap, query status, register access, and memory coherency packets.

## Important APIs and macro groups
The base packet constructors are `PACKET0(reg, n)`, `PACKET2(v)`, `PACKET3(op, n)`, and `PACKET3_COMPUTE(op, n)`. Decode helpers are `CP_PACKET_GET_TYPE()`, `CP_PACKET_GET_COUNT()`, `CP_PACKET0_GET_REG()`, and `CP_PACKET3_GET_OPCODE()`.

The opcode list covers common graphics and compute packet 3 commands, including dispatch/draw, `PACKET3_WRITE_DATA`, `PACKET3_WAIT_REG_MEM`, `PACKET3_INDIRECT_BUFFER`, `PACKET3_COPY_DATA`, `PACKET3_EVENT_WRITE`, `PACKET3_RELEASE_MEM`, `PACKET3_DMA_DATA`, `PACKET3_ACQUIRE_MEM`, register load/set packets, `PACKET3_INVALIDATE_TLBS`, `PACKET3_SET_RESOURCES`, `PACKET3_MAP_QUEUES`, `PACKET3_UNMAP_QUEUES`, and `PACKET3_QUERY_STATUS`.

Bitfield helpers are grouped by packet. Examples include `WRITE_DATA_DST_SEL`, `WR_CONFIRM`, XCD/MID scope and temporal fields; `WAIT_REG_MEM_FUNCTION`, memory/register space, operation, die ID, and temporal fields; `COPY_DATA_SRC_SEL` and destination/scope/temporal fields; release/acquire memory GCR controls; DMA data source/destination controls; queue resource, map, unmap, and query status controls; and TLB invalidate destination/PASID/flush fields.

## Control flow and integration
This header has no runtime control flow. It is included by `gfx_v12_1.c`, where packet macros become the low-level vocabulary for `amdgpu_ring_write()` sequences. The macros encode hardware ABI details directly into emitted command streams, so their consumers are sensitive to exact bit positions, packet lengths, and packet-specific comments.

KIQ queue management in `gfx_v12_1.c` uses `PACKET3_SET_RESOURCES`, `PACKET3_MAP_QUEUES`, `PACKET3_UNMAP_QUEUES`, and `PACKET3_QUERY_STATUS`. Ring tests and register access use `WRITE_DATA`, `COPY_DATA`, and `WAIT_REG_MEM`. Fence and cache synchronization use `RELEASE_MEM` and `ACQUIRE_MEM`. TLB invalidation uses `PACKET3_INVALIDATE_TLBS`.

## State and persistence behavior
The header owns no persistent state. Its macros produce immediate integer values embedded into ring buffers and indirect buffers. Once emitted, those values persist in GPU-visible command memory until consumed by the command processor or overwritten by ring reuse.

## Dependencies
The header depends on common AMDGPU register helper macro `REG_SET()` for `PACKET2(v)` and on consumers providing standard integer expressions. It shares opcode/bitfield contracts with GC 12.1 command processor firmware and hardware. Any mismatch between these definitions and firmware expectations directly affects command submission correctness.

## Risks and edge cases
Because these are preprocessor macros, type checking is minimal and argument side effects can be evaluated inside shifts. Field helpers generally mask inputs only when explicitly written to do so; several helpers shift raw values. Incorrect packet count arguments can desynchronize the command stream.

There are apparent macro-quality risks worth compile-testing carefully. `INDIRECT_BUFFER_TEMPORAL(x)` is written with mismatched parentheses, and `COPY_DATA_SRC_DST_REMOTE_MODE(x)` has precedence that may not match the intended `(((x) & 0x1) << 16)` shape. These may be unused today, but use by future code could cause compile failures or wrong packet fields. The header also contains typo/comment issues such as `DOOREBLL` in `PACKET3_RELEASE_MEM_ADD_DOOREBLL_OFFSET`, which is harmless if consumers use the exact macro name but can mislead readers.

The packet definitions are a hardware ABI surface. Reusing macros from another GFX generation, changing bit positions, or using graphics-only packet assumptions on compute/KIQ rings can lead to hangs, missed fences, failed TLB invalidation, or queue-management failures.

## Test signals
Primary validation is compile coverage of all used macros and runtime ring validation from `gfx_v12_1_ring_test_ring()` and `gfx_v12_1_ring_test_ib()`. Additional signals include successful KIQ map/unmap/query, fence completion, VM flush/TLB invalidation correctness, release/acquire memory coherency behavior, MES user queue fence IRQ handling, and lack of command processor hangs under suspend/resume and reset. Static analysis or targeted build tests should cover currently unused macros before they are adopted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v12_1_pkt.h -->
