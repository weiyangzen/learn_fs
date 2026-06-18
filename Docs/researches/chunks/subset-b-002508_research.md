# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 9916-12288

## Scope

This chunk covers generated shift and mask macros from `gc_11_0_0_sh_mask.h` for a GC 11.0.0 AMD GPU register header. The lines span the tail of one `GCEA_DSM_CNTL2A` definition and then register field layouts for several GC address blocks:

- `gc_gceadec3`: GCEA error/status, GL2C crossbar credit, probe, EDC, and SDP fields.
- `gc_spipdec2`: SPI queue/event and throttle control fields.
- `gc_rmi_rmidec`: RMI request/return path, UTC/UTCL1 controls, scoreboard, xbar, formatter, and spare/debug fields.
- `gc_pmmdec`: GCR PIO and PMM control/status fields.
- `gc_utcl1dec`: UTCL1 bypass, allocation logging, and busy/status fields.
- `gc_gcvmsharedpfdec`: physical-function shared GCMC aperture, VM aperture, GCUTCL2, and GCVML2 register fields.
- `gc_gcvml2pfdec`: physical-function VM L2 cache, protection fault, identity aperture, throttle, cache dump, translation assist, bank selection, and credit-safety fields.
- `gc_gcvmsharedvcdec`: virtual-client shared aperture and L1 TLB fields.
- `gc_gcvml2vcdec`: per-context VM controls and invalidate-engine semaphore/request fields.

The chunk exports preprocessor constants only. It defines no C functions, structs, storage, or executable control flow. Its behavior is the ABI-like contract that lets driver code build, update, and decode SOC15 MMIO register values without hard-coded bit positions.

## Purpose

The header gives bitfield metadata for GC 11.0.0 registers. Every field appears as a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used when encoding or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate that field in a 32-bit register value.

These macros are consumed by register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. Address values and reset defaults live in sibling generated files such as `gc_11_0_0_offset.h` and `gc_11_0_0_default.h`; this file supplies only field positions and masks.

The largest functional area in this chunk is graphics VM setup and invalidation. It defines the field contract used by the GFXHUB layer to configure VM L2 cache policy, page table depth, identity aperture behavior, protection fault handling, and TLB/cache invalidation requests.

## Important Macro Families

### GCEA and SPI

The GCEA section contains masks for GL2C crossbar and error-handling controls. Notable registers include:

- `GCEA_GL2C_XBR_CREDITS` and `GCEA_GL2C_XBR_MAXBURST`, which describe DRAM/IO read and write credit limits, reserves, max bursts, and combiner flush behavior.
- `GCEA_PROBE_CNTL` and `GCEA_PROBE_MAP`, which describe probe request/response delay, filtering, channel address mapping to right-side GL2C instances, and interleave size.
- `GCEA_ERR_STATUS`, whose fields expose SDP read/write response status, data status, dataparity error, fatal interrupt controls, busy-on-error behavior, and clear/status bits.
- `GCEA_MISC2`, `GCEA_RRET_MEM_RESERVE`, `GCEA_EDC_CNT3`, and `GCEA_SDP_ENABLE`, which describe request blocking, arbitration priority, virtual-channel reservation, EDC counters, and SDP write mux enablement.

The SPI portion is small and defines `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL` fields for queue/event behavior and export throttling.

### RMI and UTCL1

The `gc_rmi_rmidec` block defines the return memory interface and its connection to UTCL1. Important groups include:

- `RMI_GENERAL_CNTL` and `RMI_GENERAL_CNTL1`: demux, skid FIFO, ordering, clock-gating, and protocol options.
- `RMI_GENERAL_STATUS` and `RMI_SUBBLOCK_STATUS0..3`: busy bits and FIFO occupancy/free-space counters for demux, xbar, scoreboard, TCIW formatters, return formatters, consumer FIFOs, and skid/probe FIFOs.
- `RMI_XBAR_CONFIG`, `RMI_XBAR_ARBITER_CONFIG`, and `RMI_XBAR_ARBITER_CONFIG_1`: xbar mux override, arbiter modes, stalls, timer overrides, and round-robin weights.
- `RMI_PROBE_POP_LOGIC_CNTL`, `RMI_DEMUX_CNTL`, and `RMI_TCIW_FORMATTER0/1_CNTL`: probe combine/depth limits, demux arbitration overrides, write combine windows, max inflight requests, reorder disable, and all-fault-return-data bits.
- `RMI_UTC_XNACK_N_MISC_CNTL`, `RMI_UTCL1_CNTL1`, `RMI_UTCL1_CNTL2`, `RMI_UTC_UNIT_CONFIG`, and `RMI_UTCL1_STATUS`: XNACK timing, VM permission mode, response/fault modes, invalidation controls, cache/FIFO reductions, snoop/ack controls, TMZ request enablement, and fault/retry/PRT status.
- `RMI_SCOREBOARD_CNTL` and `RMI_SCOREBOARD_STATUS0..2`: RB flush completion, VMID invalidation progress, running/snapshot counters, underflow/overflow flags, timestamp flush status, and CP VMID invalidation state.
- `RMI_RB_GLX_CID_MAP` and `RMI_SPARE*`: client-id mapping for CB/DB paths and spare knobs for no-fill behavior, reorder bypass, early ack, XNACK return override, address masks, and clock-gating disables.

The standalone `gc_utcl1dec` block then defines `UTCL1_CTRL_1`, `UTCL1_ALOG`, and `UTCL1_STATUS`, which provide broader UTCL1 bypass controls, forced invalidation/all-done bits, page-size selection, allocation logging controls, and hit/miss/invalidation busy signals.

### PMM and GCR PIO

The PMM block provides `GCR_PIO_CNTL`, `GCR_PIO_DATA`, `PMM_CNTL`, and `PMM_STATUS` fields. These cover PIO index/write/read controls, GCR data payload, PMM timeout and force controls, timeout actions, state, and status/error flags. Consumers can use these masks to drive low-level performance or power-management monitor access paths.

### Shared VM Aperture and Memory Policy

The `gc_gcvmsharedpfdec` and `gc_gcvmsharedvcdec` blocks define memory aperture and address-range fields:

- PF/shared fields: top-of-DRAM slots, TOM2 lower/upper enable/ranges, framebuffer offset, system aperture default address LSB/MSB, VM steering, memory power light-sleep setup/hold, cacheable DRAM range, local sysmem range, APT controls, local FB range, FB-address lock, FB no-alloc policy, GCUTCL2 harvest bypass/fault status, and GCUTCL2 clock/busy controls.
- VC/shared fields: framebuffer base/top, AGP top/bottom/base, system aperture low/high, and `GCMC_VM_MX_L1_TLB_CNTL` fields for L1 TLB enablement, system access mode, unmapped aperture access, advanced driver model, ECO bits, and memory type.

These fields are part of the GPU memory-controller programming surface and are paired with offset/default definitions in sibling generated headers.

### GCVM L2, Faults, and Translation Assist

The `gc_gcvml2pfdec` block is the densest part of this chunk. It describes:

- `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_L2_CNTL4`, and `GCVM_L2_CNTL5`: VM L2 enablement, fragment processing, PTE/PDE endian modes, cache split/effective sizes, invalidate controls, PDE cache size, cache associativity, force-miss bits, tap physical-request controls, IFIFO transaction limits, fragment sizing, walker priority client id, walker noalloc/MTYPE enables, and clock-gating options.
- `GCVM_L2_STATUS`: L2 busy, context-domain busy vector, and parity error flags for 4K/bigK PTE caches and PDE caches.
- `GCVM_DUMMY_PAGE_FAULT_*`: dummy page fault enable, address mode, compare MSBs, and low/high address components.
- `GCVM_L2_PROTECTION_FAULT_CNTL`, `GCVM_L2_PROTECTION_FAULT_CNTL2`, `GCVM_L2_PROTECTION_FAULT_MM_CNTL3/4`, `GCVM_L2_PROTECTION_FAULT_STATUS`, and fault address/default address registers: controls for clearing and updating fault status, default enable bits for fault classes, retry/no-retry interrupt selection by client id, crash-on-fault bits, active migration PTE handling, retry fault interrupt enable, fault source fields, VMID/VF/VFID, PRT flag, and recorded logical/default physical page addresses.
- `GCVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `GCVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`: identity-mapped aperture bounds and physical offset.
- `GCVM_L2_MM_GROUP_RT_CLASSES`, `GCVM_L2_BANK_SELECT_RESERVED_CID*`, `GCVM_L2_BANK_SELECT_MASKS`: routing and bank selection metadata.
- `GCVM_L2_CACHE_PARITY_CNTL`, `GCVM_L2_ICG_CTRL`, `GCVM_L2_CGTT_BUSY_CTRL`: parity forcing/checking and clock/busy override fields.
- `GCVML2_WALKER_*_THROTTLE_*`: macro/micro walker throttle time and fetch limit fields.
- `GCVM_L2_PTE_CACHE_DUMP_CNTL` and `GCVM_L2_PTE_CACHE_DUMP_READ`: PTE cache dump selection and data readout.
- `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_*` and `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_RESPONSE_*`: explicit translation-assist request fields for address, VMID, VFID/VF, GPA, permissions, client id, request bit, and response fields for translated address, permissions, fragment size, snoop/SPA/IO/TMZ/no-PTE/MTYPE/memlog/NACK/noalloc/ACK.
- `GCUTCL2_CREDIT_SAFETY_*` and `GCVML2_*_CREDIT_SAFETY_*`: credit values and update bits for return, invalidation, fault interrupt, and walker fetch paths.

### GCVM Contexts and Invalidation Engines

The `gc_gcvml2vcdec` block defines repeated `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` macros. Each context has the same field layout:

- Enablement and page-table shape: `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, and `PAGE_TABLE_BLOCK_SIZE`.
- Retry controls: `RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` and `RETRY_OTHER_FAULT`.
- Interrupt/default enable bits for range, dummy page, PDE0, valid, read, write, and execute protection faults.

The chunk then defines `GCVM_CONTEXTS_DISABLE`, a bitmap that disables contexts 0 through 15, followed by `GCVM_INVALIDATE_ENG0_SEM` through `GCVM_INVALIDATE_ENG17_SEM` semaphore bits. It also defines invalidate request layouts for engines 0 through 9 within this line range. Each request includes per-VMID invalidate bits, flush type, invalidation of L2 PTEs and PDE0/PDE1/PDE2, L1 PTE invalidation, protection-fault-status-address clear, request logging, and 4K-only invalidation.

## Control Flow and State Behavior

This header does not execute any control flow and persists no software state. It is a compile-time description of hardware state layout. Runtime control flow appears in consumers that include this header. For example, `amdgpu/gfxhub_v2_0.c` and `amdgpu/gfxhub_v2_1.c` use `REG_SET_FIELD` with `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_CONTEXT0_CNTL`, and `GCVM_INVALIDATE_ENG0_REQ` to configure GFXHUB VM behavior, issue invalidations, and derive context/invalidation register distances. Those consumers read and write hardware MMIO registers through SOC15 helper macros.

The persistent state affected by these macros is hardware state, not C memory in this header. Important persistent hardware-visible state includes VM context enable bits, retry/default fault policy, L2 cache configuration, fault status latches, dummy/default fault addresses, identity apertures, invalidate request/semaphore state, FIFO/scoreboard busy flags, and performance/debug counters. Some fields are command-like or write-one/control bits, such as invalidate requests, clear fault status fields, forced invalidation toggles, or update bits for credit-safety registers. Consumers must respect hardware sequencing and polling rules from the corresponding driver code and hardware documentation.

## Dependencies and Integration Points

This chunk depends on the naming convention shared by generated AMD ASIC register headers:

- `gc_11_0_0_offset.h` supplies `reg...`, `mm...`, and base-index address constants for the same register names.
- `gc_11_0_0_default.h` supplies reset/default values, such as defaults for `GCVM_L2_CNTL`, `GCVM_CONTEXT0_CNTL`, `GCVM_INVALIDATE_ENG0_REQ`, `GCEA_ERR_STATUS`, and `RMI_GENERAL_STATUS`.
- Register helper macros in the AMDGPU DRM driver consume the `__SHIFT` and `_MASK` constants to safely compose bitfields.

Observed integration points in the source tree include:

- `amdgpu/gfxhub_v2_0.c` and `amdgpu/gfxhub_v2_1.c`, which program GFXHUB VM L2, contexts, and invalidate requests using these GCVM macros.
- `amdgpu/imu_v11_0_3.c`, which lists golden/default-like GCVM register programming values.
- `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdkfd/kfd_device_queue_manager_v11.c`, and `amdkfd/kfd_mqd_manager_v11.c`, which include this GC 11 mask header for queue/KFD interactions.
- `display/amdgpu_dm/amdgpu_dm_plane.c`, which includes the header for GC 11 display-plane related register field access.
- Earlier or sibling ASIC generations reuse similar register names, so edits must not assume a field layout is portable across GC versions. For example, GC 12 headers contain similar names but may shift fields differently.

## Risks

- Bitfield accuracy is critical. A wrong shift or mask can write unrelated hardware bits, causing VM faults, cache coherency failures, invalidation hangs, interrupts being missed or over-triggered, or GPU reset.
- Repeated context and invalidate-engine macro families are easy to update inconsistently. Engines and contexts have mostly identical layouts; one typo in a repeated mask may affect only a subset of VMIDs or invalidation engines.
- Cross-generation similarity is a trap. Code that includes `gc_11_0_0_sh_mask.h` must pair it with matching GC 11.0.0 offsets/defaults. Similar GC 12 or GC 10 names cannot be blindly mixed.
- Some fields represent status/clear, semaphore, toggle, or request semantics. Treating them as ordinary persistent configuration bits can lose fault logs, force stale invalidations, or break synchronization with hardware.
- This generated header contains no validation logic. Compile success only proves macro names and syntax are present, not that hardware programming sequences are correct.

## Test and Validation Signals

Useful validation for this chunk is mostly integration-level:

- Build coverage for AMDGPU/KFD/display sources that include `gc/gc_11_0_0_sh_mask.h`; this catches missing or renamed macros.
- Compile-time references in `gfxhub_v2_0.c` and `gfxhub_v2_1.c` should continue to resolve for `GCVM_L2_*`, `GCVM_CONTEXT*`, and `GCVM_INVALIDATE_ENG*_REQ` fields.
- Runtime VM tests should exercise GPU VM setup, context programming, page table depth/block-size handling, invalidation paths, and retry/no-retry fault behavior.
- Fault-injection or fault-observation tests should verify `GCVM_L2_PROTECTION_FAULT_STATUS`, fault address registers, retry/PRT interrupts, and GCEA/RMI error status reporting.
- Suspend/resume and reset tests should verify that persistent hardware state programmed from these macros is saved, restored, or reinitialized by the owning GFXHUB/GMC code.
- Debug/performance validation can inspect RMI busy/status, UTCL1 allocation logging, PTE cache dump controls, and credit-safety update paths when diagnosing hangs or VM pressure.

## Unresolved Cross-Chunk References

This chunk starts after earlier `GCEA_DSM_CNTL2A` definitions have already begun, and it ends mid-family after `GCVM_INVALIDATE_ENG9_REQ`; later chunks should cover invalidate request engines beyond 9 and any following GCVM registers. The final merged per-file report should connect this chunk with earlier/later chunks to describe the full generated header, include guards, any preceding register families, and remaining invalidate engine definitions.
