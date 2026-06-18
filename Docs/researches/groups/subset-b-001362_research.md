# subset-b-001362 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c

## Purpose

`soc15.c` is the AMDGPU common IP implementation for GFX9/SOC15-era devices including Vega, Raven/Raven2/Picasso/Renoir, Arcturus, Aldebaran, and Aqua Vanjaram-class derivatives. It wires the `AMD_IP_BLOCK_TYPE_COMMON` block into the AMDGPU IP lifecycle and installs ASIC-level callbacks used by higher-level device code for BIOS reads, whitelisted register reads, resets, clocks, PCIe counters, doorbells, video codec capability queries, and clock/power gating. The file is not a standalone device driver; it is selected by AMDGPU's ASIC discovery and IP block setup.

## Important APIs, Types, And Functions

Key exported objects are `vega10_common_ip_block`, `soc15_grbm_select()`, `soc15_set_virt_ops()`, and `soc15_program_register_sequence()`. The file defines `soc15_asic_funcs`, `vega20_asic_funcs`, and `aqua_vanjaram_asic_funcs`, selecting doorbell setup and PCIe/statistics behavior by chip family. Indirect register helpers cover UVD context, DIDT, GC CAC, and SE CAC with per-register spinlocks. `soc15_query_video_codecs()` maps VCE/UVD/VCN IP versions to codec arrays. Reset helpers select PCI, BACO, Mode1, Mode2, or link reset depending on module parameters, MP1 IP version, RAS state, XGMI CPU attachment, BACO capability, and suspend/resume state.

## Control Flow

`soc15_common_early_init()` sets NBIO remapping, installs indirect register callbacks, records revision IDs, chooses ASIC functions and CG/PG flags from GC IP version, and initializes SR-IOV mailbox support when running as a VF. `sw_init()` delegates DF initialization and VF mailbox IRQ registration. `hw_init()` programs ASPM, initializes NBIO, optionally remaps HDP registers, enables doorbell apertures, and initializes SDMA doorbell ranges before CP rings use doorbells. Late init enables VF mailbox IRQs and the selfring aperture. Fini/suspend paths reverse doorbell and IRQ state; resume can force an ASIC reset for aborted S3 cases.

## State And Persistence Behavior

Persistent software state is stored in `adev`: `asic_funcs`, register access function tables, `cg_flags`, `pg_flags`, `external_rev_id`, doorbell index/range state, VF mailbox settings, and RAS/NBIO IRQ ownership. Hardware state is written through NBIO/HDP/DF/SMUIO registers, doorbell aperture controls, GRBM selection, PCIe counters, and golden register programming. Several helpers intentionally cache hardware-derived values such as `gb_addr_config` instead of always reading registers.

## Dependencies And Integration Points

The implementation depends on SOC15 register offset tables, NBIO variants, GFX/GMC/MMHUB/GFXHUB/DF/HDP/SMUIO blocks, PSP/DPM reset services, SR-IOV mailbox code, RAS, XGMI, PCIe helpers, and codec capability definitions exposed to userspace through DRM info queries. `soc15_program_register_sequence()` is consumed by per-IP golden-register setup code.

## Risks And Test Signals

Reset selection is the highest-risk logic because it varies by MP1 version, BACO support, RAS firmware version, APU flags, XGMI attachment, and suspend-abort state. CG/PG flag tables are maintenance-sensitive because a wrong bit enables unsupported clock or power gating. Doorbell range ordering affects SDMA, IH, and CP routing. Useful tests are boot/resume/reset on each supported ASIC, SR-IOV VF initialization, RAS recovery with BACO, `debugfs`/ioctl whitelisted register reads, `clk`/power gating state queries, PCIe replay/usage sysfs, video capability queries, and ring tests after doorbell setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.h

## Purpose

`soc15.h` is the public AMDGPU SOC15 common header. It defines small register-description structures and macros used by SOC15-era C files to express register offsets, golden-register programming, whitelisted register reads, and RAS error counter extraction. It also declares exported common IP blocks, register-base initialization entry points, SOC-specific doorbell initialization helpers, virtual operation setup, and Aqua Vanjaram configuration/state helpers.

## Important APIs, Types, And Functions

`struct soc15_reg_golden` carries a hardware IP, instance, segment, register offset, AND mask, and OR mask for golden-register programming. `struct soc15_allowed_register_entry` describes registers that may be exposed through debug/user read paths and includes a `grbm_indexed` flag for SE/SH-indexed reads. `struct soc15_ras_field_entry` describes RAS correctable/uncorrectable counter fields. Macros such as `SOC15_REG_ENTRY`, `SOC15_REG_GOLDEN_VALUE`, `SOC15_REG_FIELD`, and `SOC15_REG_ENTRY_OFFSET` standardize offset construction from generated register headers and `adev->reg_offset`.

## Control Flow

The header has no runtime control flow. It shapes call sites in files such as `soc15.c` and per-IP golden-register code: callers build static arrays of these structures, then pass them to routines like `soc15_program_register_sequence()` or compare requested register offsets against allow lists.

## State And Persistence Behavior

The structures are usually static metadata, but their offsets are interpreted against runtime `adev->reg_offset` tables initialized by `vega10_reg_base_init()`, `vega20_reg_base_init()`, `arct_reg_base_init()`, `aldebaran_reg_base_init()`, or Aqua Vanjaram setup. Incorrect metadata persists as hardware programming mistakes because it directly drives MMIO writes.

## Dependencies, Risks, And Test Signals

The header depends on NBIO variant declarations and `amdgpu_reg_state.h`. Its macros assume an in-scope `adev` variable, so misuse outside normal AMDGPU helper style is fragile. Risks are off-by-instance/segment errors, stale generated register names, and exposing the wrong register through an allow list. Compile coverage across SOC15 ASICs, golden-register table execution, RAS field parsing, and debug register read tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15_common.h

## Purpose

`soc15_common.h` centralizes SOC15-style MMIO, RLC-mediated register access, logical-to-physical IP instance mapping, wait helpers, extended SMN access, and MCA 64-bit register access macros. It is a low-level integration header used by many AMDGPU IP blocks to avoid open-coding register base arithmetic and SR-IOV/RLCG access rules.

## Important APIs, Types, And Functions

`GET_INST()` and `GET_MASK()` consult `adev->ip_map` when logical device instances differ from hardware instances. `SOC15_REG_OFFSET()` and related offset macros compute MMIO offsets from generated register base indices. `RREG32_SOC15*` and `WREG32_SOC15*` variants perform reads/writes through `__RREG32_SOC15_RLC__` and `__WREG32_SOC15_RLC__`, which route through SR-IOV RLCG access when available. RLC-specific macros include `WREG32_RLC`, `WREG32_RLC_EX`, `WREG32_SOC15_RLC_SHADOW`, and `WREG32_SOC15_RLC_SHADOW_EX`. `SOC15_WAIT_ON_RREG*` wraps polling, while `RREG32_SOC15_EXT()`, `WREG32_SOC15_EXT()`, `RREG64_MCA()`, and `WREG64_MCA()` target extended SMN/MCA spaces.

## Control Flow

Most logic is macro-expanded at call sites. In SR-IOV VF mode with RLCG support, reads and writes are redirected to `amdgpu_sriov_rreg()`/`amdgpu_sriov_wreg()` with access flags; otherwise they become direct `RREG32()`/`WREG32()` operations. Full-access RLC writes can use scratch registers and a spare interrupt, polling for completion with a fixed retry loop.

## State And Persistence Behavior

The macros mutate hardware registers and sometimes RLC scratch state. They rely on stable `adev->reg_offset`, IP mapping callbacks, SR-IOV state, and RLC capability flags. No independent state is defined by the header, but every write changes persistent device register state until reset or later programming.

## Dependencies, Risks, And Test Signals

The header assumes AMDGPU core register macros, `adev` scope, generated register base symbols, and SR-IOV/RLC helpers. Risks include evaluating macro arguments with side effects, using direct access where KIQ/RLC access is required, wrong instance mapping, and timeout paths in `WREG32_RLC_EX`. Test signals include PF and VF register programming, KIQ/no-KIQ paths, RLC shadowed GRBM writes, wait helper timeout behavior, extended SMN access on multi-die hardware, and MCA register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15d.h

## Purpose

`soc15d.h` is a command packet definition header for GFX9/SOC15 command submission and multimedia engines. It defines ring counts, PM4 packet type encoders/decoders, PACKET3 opcodes, bitfield helpers, compute queue management packet fields, cache/memory synchronization fields, TLB invalidation fields, and VCE/HEVC command identifiers.

## Important APIs, Types, And Functions

The core packet builders are `PACKET0()`, `PACKET2()`, `PACKET3()`, `PACKET3_COMPUTE()`, and `PACKETJ()`. Decoder helpers include `CP_PACKET_GET_TYPE()`, `CP_PACKET_GET_COUNT()`, `CP_PACKET0_GET_REG()`, `CP_PACKET3_GET_OPCODE()`, and PACKETJ field extractors. The long PACKET3 section enumerates opcodes such as `WRITE_DATA`, `WAIT_REG_MEM`, `INDIRECT_BUFFER`, `COPY_DATA`, `EVENT_WRITE`, `RELEASE_MEM`, `ACQUIRE_MEM`, register load/set packets, `INVALIDATE_TLBS`, `SET_RESOURCES`, `MAP_QUEUES`, `UNMAP_QUEUES`, and `QUERY_STATUS`. Multimedia command constants cover VCE and HEVC encoder ring packets.

## Control Flow

There is no executable code. Runtime behavior is created by other modules composing command buffers with these macros. Those command buffers are consumed by GPU command processors, SDMA-related synchronization paths, compute queue management, graphics rings, KFD queue setup, or multimedia engines depending on packet type and opcode.

## State And Persistence Behavior

The header does not store state, but packet encodings built from it can program registers, update memory, emit fences, flush/invalidate caches and TLBs, map or unmap queues, and signal interrupts. Incorrect constants can corrupt command streams or persistent GPU context state.

## Dependencies, Risks, And Test Signals

The header depends on generic bit helpers such as `REG_SET()`/field-style shifts used throughout AMDGPU. It is tightly coupled to hardware packet ABI, so risks are silent command misencoding, wrong register aperture ranges, invalid cache policy bits, or queue management fields that break KFD. Tests include command submission on graphics/compute rings, IB chaining, fence signaling, cache flush and TLB invalidation validation, KFD queue map/unmap/preemption, VCE/HEVC ring tests, and parser tests that decode generated packet headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c

## Purpose

`soc21.c` implements the common AMDGPU IP block for SOC21/RDNA3-class devices. It installs ASIC callbacks, register access helpers, codec capability tables, reset policy, doorbell assignments, revision-dependent CG/PG flags, SR-IOV mailbox integration, RAS IRQ handling, and common lifecycle hooks for hardware initialization, suspend, resume, and gating.

## Important APIs, Types, And Functions

The exported object is `soc21_common_ip_block`; `soc21_grbm_select()` updates `GRBM_GFX_CNTL`. `soc21_query_video_codecs()` selects VCN 4.0.x and 5.3.0 codec capabilities, with mutable SR-IOV codec arrays that can be updated from the host. `soc21_didt_rreg()`/`soc21_didt_wreg()` protect indirect DIDT access with `adev->reg.didt.lock`. `soc21_read_register()` exposes a whitelist of GC and SDMA status registers. `soc21_asic_reset_method()` chooses Mode1, Mode2, BACO, or user override by MP1 IP version. `soc21_init_doorbell_index()` assigns KIQ, MEC, user queues, GFX, MES, SDMA, IH, VCN, VPE, and non-CP doorbell ranges.

## Control Flow

`soc21_common_early_init()` sets NBIO remapping, PCIe indirect/port accessors, DIDT accessors, ASIC functions, revision IDs, and GC-version-specific CG/PG flags; it also enables SR-IOV VF settings. Late init obtains VF mailbox IRQs and patches SR-IOV video codecs or enables NBIO ATHUB RAS error IRQs for PF. Hardware init programs ASPM, initializes NBIO registers, optionally remaps HDP, and enables the doorbell aperture. Fini disables apertures and releases mailbox/RAS IRQs. Resume can detect dGPU S3 abort by sampling the MP0 sign-of-life register and reset before reinitialization.

## State And Persistence Behavior

State is split between `adev` callback tables/flags and persistent hardware registers. The file updates doorbell mappings, mailbox IRQ ownership, RAS IRQ references, NBIO/HDP clock gating state, LSDMA memory power gating, and VCN codec capability data. SR-IOV codec arrays are intentionally non-const because host-provided capability updates persist in the guest driver's data.

## Dependencies And Integration Points

SOC21 depends on GC 11 register headers, MP 13 offsets, SOC15 common register macros, NBIO/HDP/LSDMA function tables, PSP/DPM reset services, SMU/VCN data, SR-IOV `mxgpu_nv`, and KFD-facing stable-pstate behavior through RLC safe mode and perfmon MCGC updates.

## Risks And Test Signals

Version tables are the main maintenance risk: wrong GC/MP/UVD matching changes reset behavior, codec exposure, or gating support. SR-IOV paths must coordinate mailbox IRQs and host codec overrides. Doorbell constants are shared with rings and KFD. Tests should cover probe on each GC 11.x/11.5.x variant, VF/PF boot, video capability queries with harvested VCNs and AV1 support changes, GPU reset modes, S3 abort recovery, NBIO/HDP clock gating, LSDMA memory PG, RAS ATHUB interrupt enable/disable, and ring/doorbell tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.h

## Purpose

`soc21.h` is the narrow public header for the SOC21 common block. It declares the `soc21_common_ip_block` exported by `soc21.c` and the `soc21_grbm_select()` helper used by graphics code to select ME, pipe, queue, and VMID context through GRBM.

## Important APIs, Types, And Functions

`soc21_common_ip_block` plugs SOC21 common behavior into AMDGPU's IP block list. `soc21_grbm_select(struct amdgpu_device *adev, u32 me, u32 pipe, u32 queue, u32 vmid)` writes the GRBM graphics control register using SOC21 register naming and does not expose an XCC parameter, unlike some multi-XCC SOC15/SOC v1 helpers.

## Control Flow And State

The header has no runtime behavior. Its declarations are used during IP block assembly and by code that needs GRBM queue selection. The actual state changes occur in `soc21.c`, where GRBM writes affect hardware register state and the common IP block mutates `adev` lifecycle state.

## Dependencies, Risks, And Test Signals

Consumers must include AMDGPU core types before using the prototypes. The main risk is calling the SOC21 GRBM selector on hardware that requires per-XCC selection or RLC shadowing semantics not represented by this prototype. Compile coverage, graphics ring tests, and queue/VMID selection tests on SOC21 hardware are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.c

## Purpose

`soc24.c` implements AMDGPU's common IP block for SOC24/GC12.0 devices. It is a streamlined successor to `soc21.c`: it supplies VCN 5.0.0 codec capabilities, ASIC callbacks, whitelisted register reads, reset policy, doorbell assignments, GC12 CG/PG flags, SR-IOV mailbox hooks, RAS IRQ enablement, NBIO/HDP/LSDMA gating, and lifecycle methods.

## Important APIs, Types, And Functions

The exported object is `soc24_common_ip_block`; `soc24_grbm_select()` writes `regGRBM_GFX_CNTL`. `soc24_query_video_codecs()` returns VCN 5.0.0 encode/decode caps and rejects fully harvested VCN configurations. `soc24_read_register()` exposes selected GC and SDMA status registers, returning cached `gb_addr_config` when available. `soc24_asic_reset_method()` supports user Mode1/Mode2/BACO overrides and defaults MP1 14.0.2/14.0.3 to Mode1, otherwise BACO if supported. `soc24_init_doorbell_index()` reuses Navi10-style assignments for KIQ, MEC, user queues, GFX, MES, SDMA, IH, VCN, and non-CP ranges.

## Control Flow

`soc24_common_early_init()` installs PCIe indirect and port accessors, ASIC callbacks, revision IDs, GC12-specific CG/PG flags, and SR-IOV VF settings. Late init gets VF mailbox IRQs or enables NBIO ATHUB RAS error events. Hardware init programs ASPM only for non-APU devices, initializes NBIO, remaps HDP, runs DF hardware init when present, and enables the doorbell aperture. Hardware fini disables doorbells and releases mailbox/RAS IRQs. Suspend and resume are direct fini/init wrappers.

## State And Persistence Behavior

The common block writes `adev` function tables, revision IDs, CG/PG flags, doorbell ranges, mailbox IRQ state, and RAS IRQ references. Hardware persistence includes NBIO/HDP/DF initialization, doorbell apertures, clock-gating bits, and LSDMA memory power-gating state. `get_pcie_replay_count()` is a dummy implementation returning zero, so sysfs users should not treat it as real hardware telemetry for this generation.

## Dependencies And Integration Points

The file depends on GC 12.0 and MP 14.0.2 register headers, SOC15 register macros, NBIO v6.3.1-style functions, HDP, DF, LSDMA v7 power-gating callbacks, DPM reset/BACO services, SR-IOV `mxgpu_nv`, RLC safe-mode support, and DRM video capability reporting.

## Risks And Test Signals

Risks include incomplete telemetry (`pcie_replay_count`), assumptions inherited from Navi10 doorbells, GC12 CG/PG tables that differ between 12.0.0 and 12.0.1, and RAS IRQ behavior tied to NBIF v6.3.1 comments. Tests should cover boot on both GC12 variants, codec queries, reset modes, non-APU ASPM programming, DF init ordering, SR-IOV VF mailbox IRQs, RAS event IRQs, clock/power gating, and doorbell/ring operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.h

## Purpose

`soc24.h` exposes the minimal SOC24 common interface to the rest of AMDGPU. It declares the common IP block and the GRBM selector implemented in `soc24.c`.

## Important APIs, Types, And Functions

`soc24_common_ip_block` is inserted into the AMDGPU IP block list for supported SOC24 devices. `soc24_grbm_select(struct amdgpu_device *adev, u32 me, u32 pipe, u32 queue, u32 vmid)` programs the active graphics engine/pipe/queue/VMID selection for register accesses that depend on GRBM context.

## Control Flow And State

No code runs from this header. It creates compile-time linkage between common AMDGPU setup code and the SOC24 implementation. State changes occur when the declared GRBM selector writes hardware registers or when the common IP block lifecycle callbacks in `soc24.c` are invoked.

## Dependencies, Risks, And Test Signals

The header relies on AMDGPU core type declarations. The risk is selecting this helper for hardware that needs a different GRBM addressing model, such as per-XCC shadowed GRBM writes. Build coverage, graphics/compute queue selection, and ring tests on SOC24 devices validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc_v1_0.c

## Purpose

`soc_v1_0.c` implements a newer AMDGPU common block for SOC v1.0/GC12.1-style multi-XCC devices. It provides standard ASIC/common lifecycle callbacks, VCN 5.0.2 codec capabilities, extended SMN addressing, doorbell setup, GRBM selection with XCC ID, and substantial XCP compute partition management for spatial/compute partition modes.

## Important APIs, Types, And Functions

Exports include `soc_v1_0_common_ip_block`, `soc_v1_0_encode_ext_smn_addressing()`, `soc_v1_0_grbm_select()`, `soc_v1_0_xcp_funcs`, `soc_v1_0_init_soc_config()`, and register normalization helpers. `soc_v1_0_doorbell_index_init()` assigns KIQ, MEC, MES, user queues, XCC doorbell range, SDMA ranges derived from SDMA instance count, IH, VCN, and non-CP ranges. `soc_v1_0_asic_reset_method()` only supports Mode2 for CPU-connected XGMI or MP1 15.0.8. XCP helpers derive/query partition modes, compute XCCs per XCP, describe XCP-owned GFXHUB/GFX/SDMA/VCN instances, calculate resource sharing, switch partitions through IMU, and optionally map XCPs to memory partition IDs through ACPI NUMA data.

## Control Flow

Early init installs PCIe indirect/extended/port accessors, ASIC callbacks, revision IDs, and minimal GC12.1 CG/PG flags. Common hw init/fini only toggles doorbell apertures. `soc_v1_0_init_soc_config()` derives AID mask from groups of four XCCs, builds an SDMA mask with two SDMA instances per XCC, initializes the XCP manager, updates supported modes, and initializes the IP map. Partition switching validates requested or auto mode against memory partitions, optionally locks KFD, runs pre-switch hooks, asks IMU firmware to switch compute partitioning, reinitializes XCP objects, runs post-switch hooks, and refreshes available modes.

## State And Persistence Behavior

Persistent driver state includes `adev->aid_mask`, `sdma_mask`, SDMA instance counts, `xcp_mgr` mode/availability/resource maps, IP maps, doorbell assignments, and `asic_funcs`. Hardware state includes doorbell aperture enablement, GRBM selection per XCC through RLC shadow writes, IMU-controlled compute partitioning, and extended SMN routing. Register normalization functions encode assumptions about XCC and MID1 register windows and directly affect cross-die register access paths.

## Dependencies And Integration Points

The file depends on SOC15 common macros, GC12.1 and MP15 register headers, GFXHUB v12.1, SDMA v7.1, GFX v12.1 XCP funcs, AMDGPU IMU, KFD locking, ACPI NUMA memory information when available, XGMI/GMC partition state, and AMDGPU IP map infrastructure.

## Risks And Test Signals

Partition math is the primary risk: invalid XCC/memory partition combinations can produce wrong resource masks or KFD-visible topology. `soc_v1_0_xcp_funcs` mutates its `switch_partition_mode` pointer for SR-IOV VFs, which is global static state and must be considered carefully. Reset support is intentionally narrow; non-Mode2 requests fail. Tests should cover SOC config derivation for different XCC masks, all valid SPX/DPX/TPX/QPX/CPX modes, auto mode, KFD lock/unlock paths, IMU partition switch failures, XCP resource maps, ACPI memory-ID mapping, register normalization, extended SMN addressing, and doorbell/ring operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc_v1_0.h

## Purpose

`soc_v1_0.h` declares the public SOC v1.0 common interfaces used by AMDGPU code outside `soc_v1_0.c`. It is focused on multi-XCC addressing, common IP block registration, SOC configuration initialization, GRBM selection, and register offset normalization.

## Important APIs, Types, And Functions

The header declares `soc_v1_0_common_ip_block`, `soc_v1_0_init_soc_config()`, `soc_v1_0_encode_ext_smn_addressing()`, `soc_v1_0_grbm_select()`, `soc_v1_0_normalize_xcc_reg_range()`, `soc_v1_0_normalize_xcc_reg_offset()`, `soc_v1_0_mid1_reg_range()`, and `soc_v1_0_normalize_reg_offset()`. It also exposes `AMDGPU_SOC_V1_0_DOORBELL_SIZE`, documenting the 2 MiB doorbell BAR contract.

## Control Flow And State

The header itself has no control flow. Callers use these declarations to initialize SoC-wide topology state, select GRBM context per XCC, encode extended SMN addresses for remote die/socket access, and normalize register offsets before lookup or access. The corresponding C implementation updates `adev` masks, XCP state, doorbell ranges, and hardware routing state.

## Dependencies, Risks, And Test Signals

The interfaces depend on AMDGPU core structures and the XCP/IP-map model. Risks are mostly contract mismatches: callers must understand whether a register is XCC-local, MID1, or globally addressed, and must pass correct XCC IDs to GRBM selection. Compile coverage plus multi-XCC register access, remote SMN access, XCP initialization, and KFD topology tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_rap_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_rap_if.h

## Purpose

`ta_rap_if.h` defines the host/shared-memory ABI for the RAP trusted application. RAP appears to validate register/address programming through PSP/TEE-mediated commands. The header is pure interface data: command IDs, status codes, validation method IDs, input/output payloads, and the shared memory layout exchanged with firmware.

## Important APIs, Types, And Functions

`RSP_ID_MASK` and `RSP_ID(cmdId)` encode responses by setting bit 31. `enum ta_rap_cmd` supports `INITIALIZE` and `VALIDATE_L0`; `enum ta_rap_validation_method` currently defines `METHOD_A`. `enum ta_rap_status` distinguishes success, unsupported command, invalid validation method, null pointer, not initialized, validation failure, unsupported ASIC, forbidden operation, and duplicate init. `struct ta_rap_cmd_output_data` reports validation counters and the last failed/checked address/value/expected value. `struct ta_rap_shared_memory` is the packed command/response mailbox shape used by the host and TA.

## Control Flow, State, And Dependencies

There is no executable control flow. The driver fills `cmd_id`, `validation_method_id`, and `rap_in_message`, submits the buffer through PSP TA infrastructure, and then reads `resp_id`, `rap_status`, and `rap_out_message`. Persistent state is in the TA session and shared buffer content. The ABI depends on fixed-width integer sizes and matching firmware layout.

## Risks And Test Signals

Risks include ABI drift, duplicate `RSP_ID` definitions across TA headers, enum size assumptions, and insufficient reserved space if firmware extends payloads. Tests should validate RAP TA load, initialize, successful and failing L0 validation, response ID matching, output counter parsing, unsupported ASIC behavior, and endian/layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_rap_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_ras_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_ras_if.h

## Purpose

`ta_ras_if.h` defines the shared-memory ABI between AMDGPU and the RAS trusted application. It lets the host enable/disable RAS features, trigger error injection, query block/sub-block information, and translate between MCA and physical addresses through PSP/TEE firmware.

## Important APIs, Types, And Functions

The ABI version is `RAS_TA_HOST_IF_VER`. `enum ras_command` covers enable, disable, trigger error, query block/sub-block info, query address. `enum ta_ras_status` includes success, reset-needed, invalid parameters, unavailable RAS, duplicate commands, injection failure, ASD/TEE/register access errors, unsupported device/IP/function/error injection, timeout, and PCS state failures. `enum ta_ras_block` enumerates UMC, SDMA, GFX, MMHUB, ATHUB, PCIE/BIF, HDP, XGMI/WAFL, DF, SMN, SEM, MP0/MP1, FUSE, MCA, VCN, JPEG, IH, MPIO, and MMSCH. Input/output unions reserve 256 dwords for ABI headroom and include init flags, feature toggles, error injection, and address translation payloads.

## Control Flow, State, And Dependencies

The driver writes `cmd_id`, `if_version`, and `ras_in_message`, invokes the TA, then checks `resp_id`, `ras_status`, and `ras_out_message`. State persists in TA initialization, enabled RAS features, injection switches, output flags, and queried address data. The header integrates with AMDGPU RAS, PSP TA loading, MCA/UMC address reporting, and NPS/memory partition handling.

## Risks And Test Signals

Risks include firmware/driver layout drift, enum value mismatches, oversized assumptions hidden by reserved padding, invalid node sentinel handling, and dangerous error-injection commands reaching production hardware. Tests should cover TA init flags, feature enable/disable by block/error type, injection failure and reset-needed statuses, MCA-to-PA and PA-to-MCA translation, unsupported IP/device statuses, and version mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_ras_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_secureDisplay_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_secureDisplay_if.h

## Purpose

`ta_secureDisplay_if.h` defines the shared-buffer ABI for the Secure Display trusted application. It supports querying TA responsiveness and sending display region-of-interest plus CRC data to an I2C path, including a v2 command that adds a ROI index.

## Important APIs, Types, And Functions

`enum ta_securedisplay_command` includes `QUERY_TA`, `SEND_ROI_CRC`, and `SEND_ROI_CRC_V2`. Status values describe success, generic failure, invalid parameter, null pointer, I2C write/init errors, DIO scratch read errors, and CRC read errors. `enum ta_securedisplay_phy_ID` supports four PHY IDs. Buffer-size constants define 15-byte v1 and 16-byte v2 I2C payloads. Input unions carry `phy_id` and optional `roi_idx`; output unions carry the query sentinel `0xAB` or the generated I2C buffer. `struct ta_securedisplay_cmd` is the 48-byte command layout.

## Control Flow, State, And Dependencies

The driver fills `cmd_id` and command input, invokes the Secure Display TA, and reads `status` plus output payload. The TA reads DIO scratch/CRC state and writes I2C data; the host only observes the output buffer. Persistent state is mostly external to this header: TA session state, display hardware scratch registers, and I2C target state.

## Risks And Test Signals

Risks include strict ABI size/layout expectations, invalid PHY or ROI index values, failure to distinguish v1/v2 buffer sizes, and secure display errors that only surface as TA status codes. Tests should query TA load using the `0xAB` sentinel, send ROI/CRC on each PHY, exercise v2 ROI indices, validate I2C buffer contents, and inject/read DIO, CRC, and I2C failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_secureDisplay_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_xgmi_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_xgmi_if.h

## Purpose

`ta_xgmi_if.h` defines the shared-memory ABI for the XGMI trusted application. It lets the driver initialize XGMI topology state, obtain local node and hive IDs, get/set topology information, and query peer link counts or extended peer port mappings.

## Important APIs, Types, And Functions

Commands include initialize, get node ID, get hive ID, get/set topology info, get peer links, and get extended peer links. Constants define up to 64 connected nodes, 32 internal state entries, 128 internal-state buffer entries, and 8 ports per peer. `struct ta_xgmi_node_info` records node ID, hop count, sharing state, and assigned SDMA engine. Peer link structures support simple link counts and extended source/destination port pairs. `struct ta_xgmi_shared_memory` includes command/response IDs, status, pagination flag for extended link records, capability flags, and command input/output unions.

## Control Flow, State, And Dependencies

The driver initializes the TA, queries IDs, sends or receives topology arrays, and may paginate extended link records by toggling `flag_extend_link_record`. State persists in TA topology/session state, XGMI hive configuration, peer sharing flags, SDMA engine assignment, and firmware capability flags. The ABI integrates with AMDGPU XGMI and PSP TA services.

## Risks And Test Signals

Risks include exceeding fixed node/port limits, partial extended-link pagination, confusing peer link formats with and without port numbers, signed SDMA engine enum handling, and stale topology state after hot reset. Tests should cover initialize, node/hive ID retrieval, valid and invalid topology arrays, sharing enablement, simple and extended peer link queries, pagination for more than 128 link records, and TA status error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ta_xgmi_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c

## Purpose

`tonga_ih.c` implements the AMDGPU interrupt handler IP block for Tonga/VI-generation hardware using an IH ring buffer. It allocates and initializes interrupt rings, programs IH registers, decodes interrupt vectors, manages read/write pointers, supports suspend/resume, and participates in soft reset handling.

## Important APIs, Types, And Functions

The exported object is `tonga_ih_ip_block`. `tonga_ih_irq_init()` programs `INTERRUPT_CNTL`, IH ring base, ring size, writeback, VMID, MSI rearm behavior, writeback address, RPTR/WPTR reset, optional doorbell RPTR, bus mastering, and enables interrupts. `tonga_ih_get_wptr()` reads writeback memory, detects overflow, repositions `rptr`, and clears overflow in `IH_RB_CNTL`. `tonga_ih_decode_iv()` converts four dwords into `amdgpu_iv_entry` fields and advances `rptr` by 16 bytes. `tonga_ih_set_rptr()` writes RPTR through doorbell or register. IP lifecycle functions wrap ring allocation, IRQ domain setup, hardware init/fini, idle waits, and soft reset.

## Control Flow

Early init creates the IRQ domain and installs IH function pointers. Software init allocates the hardware IH ring and software IH ring, enables doorbell mode, and initializes AMDGPU IRQ core. Hardware init disables interrupts, programs the ring, enables PCI bus mastering, and enables interrupts. IRQ processing outside this file calls the installed `get_wptr`, `decode_iv`, and `set_rptr` callbacks. Soft reset checks `SRBM_STATUS.IH_BUSY`, stores an SRBM reset mask, disables IH, toggles `SRBM_SOFT_RESET`, and reinitializes IH afterward.

## State And Persistence Behavior

Driver state lives in `adev->irq.ih`, `adev->irq.ih_soft`, `adev->irq.ih_funcs`, and `adev->irq.srbm_soft_reset`. Hardware state includes IH control registers, ring base, writeback address, doorbell RPTR, RPTR/WPTR, interrupt enable bits, and SRBM soft-reset bits. Overflow recovery deliberately skips to the last not-overwritten vector estimate, so some interrupt events may be lost but processing can resume.

## Dependencies And Integration Points

The file depends on OSS 3.0 and BIF 5.1 register headers, AMDGPU IRQ core, IH ring helpers, PCI bus mastering, doorbell writes, MSI behavior, and generic IP block lifecycle management. It feeds decoded IVs into the broader AMDGPU interrupt dispatch path.

## Risks And Test Signals

Risks include ring-size/order mismatches, writeback endianness, overflow handling that drops events, incorrect doorbell index programming, MSI rearm differences, and soft reset races with live interrupt writes. Tests should cover IRQ domain creation, ring allocation/free, MSI and non-MSI operation, doorbell and register RPTR modes, interrupt storm/overflow recovery, suspend/resume, soft reset while IH busy, idle timeout behavior, and decoded IV dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.h

## Purpose

`tonga_ih.h` is the public declaration header for the Tonga interrupt handler IP block. It exposes `tonga_ih_ip_block` so AMDGPU ASIC setup code can include the VI/Tonga IH implementation in the device IP block list.

## Important APIs, Control Flow, And State

The only API is `extern const struct amdgpu_ip_block_version tonga_ih_ip_block;`. The header has no executable logic and defines no state. Runtime behavior is implemented in `tonga_ih.c`, where the block installs IH function callbacks, allocates interrupt rings, programs IH registers, and manages suspend/resume and soft reset.

## Dependencies, Risks, And Test Signals

Consumers need AMDGPU IP block type definitions visible through normal include ordering. The risk is configuration-level: selecting this IP block for incompatible hardware would program the wrong IH register model. Compile coverage and probe/interrupt tests on Tonga/VI hardware validate the declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/tonga_ih.h -->
