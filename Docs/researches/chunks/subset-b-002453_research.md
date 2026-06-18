# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 10059-12432

## Scope

This chunk is a middle segment of the generated AMD GC 10.1.0 shift/mask header. It covers line 10059 through line 12432 and defines 2,182 preprocessor constants: 1,089 `__SHIFT` macros and 1,093 `_MASK` macros, plus address-block and register-group comments. The slice starts in the tail of `GB_TILE_MODE24` with `SAMPLE_SPLIT` and its masks, then covers `GB_TILE_MODE25` through `GB_TILE_MODE31`, all `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15`, color-buffer controls, GCEA/SDP request and error-reporting controls, SPI system knobs, RMI controls/status, PMM/GCR controls, UTCL1 controls, ATC L2 controls, GCVM L2 controls, and complete `GCVM_CONTEXT0_CNTL` and `GCVM_CONTEXT1_CNTL` definitions. It ends exactly at the `//GCVM_CONTEXT2_CNTL` marker, before that context's fields.

The content is declarative only. There are no C functions, structs, enums, branches, loops, allocations, or local runtime side effects. The exported surface is a generated macro namespace that tells driver code where each hardware register bitfield lives.

## Purpose

`gc_10_1_0_sh_mask.h` provides symbolic bit positions and bit masks for Graphics Core 10.1.0 registers. Consumers pair these macros with register offsets from `gc_10_1_0_offset.h` and access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` to build or decode MMIO register values without embedding raw shifts and masks in driver logic.

This chunk is primarily about memory layout, graphics backend behavior, graphics memory fabric controls, and GPU virtual-memory translation:

- `GB_TILE_MODE*` and `GB_MACROTILE_MODE*` describe surface tiling and macrotiling layout fields.
- `CB_*` and `GC_USER_RB_*` describe color-buffer cache, DCC, memory-arbiter, stutter, eviction, render-backend redundancy, and backend-disable controls.
- `GCEA_*` and `SPI_*` cover graphics command/error/address-decode plumbing, SDP credits, latency sampling, performance counters, EDC/DSM diagnostic controls, DRAM/GMI/IO arbitration, probe mapping, error status, and small SPI queue/compute knobs.
- `RMI_*`, `PMM_*`, `GCR_*`, and `UTCL1_*` describe request/return memory interface behavior, crossbar arbitration, VMID invalidation scoreboarding, clock gating, PIO/GCR controls, target disable masks, UTCL1 cache and invalidation controls, and address-log controls.
- `GC_ATC_L2_*` and `GCVM_L2_*` define ATC/GPUVM L2 cache, fault, invalidation, parity, fragment-size, group real-time class, clock-gating, and walker throttling fields.
- `GCVM_CONTEXT0_CNTL` and `GCVM_CONTEXT1_CNTL` define per-context enable, page-table shape, retry, and protection-fault policy fields.

## Exported API Surface

There are no callable APIs or local data types. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low-bit position.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted register mask for the field.

Important macro families in this chunk include:

- `GB_TILE_MODE24` through `GB_TILE_MODE31`: `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, `MICRO_TILE_MODE_NEW`, and `SAMPLE_SPLIT`. These fields encode graphics surface tile layout choices consumed by address calculations and metadata programming.
- `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15`: `BANK_WIDTH`, `BANK_HEIGHT`, `MACRO_TILE_ASPECT`, and `NUM_BANKS`. These define macrotiling geometry used with the tile-mode table.
- `CB_HW_CONTROL`, `CB_HW_CONTROL_1` through `_4`, `CB_DCC_CONFIG`, `CB_HW_MEM_ARBITER_RD`, `CB_HW_MEM_ARBITER_WR`, `CB_RMI_BC_GL2_CACHE_CONTROL`, `CB_STUTTER_CONTROL_*`, and `CB_CACHE_EVICT_POINTS`: color-buffer cache sizing, feature-disable, optimization, arbitration, DCC, cache-policy, latency, and eviction fields.
- `GC_USER_RB_REDUNDANCY` and `GC_USER_RB_BACKEND_DISABLE`: render-backend repair, redundancy, and backend-disable fields.
- `GCEA_*`: graphics command/error/address-decode controls for SDP request pass-through overrides, virtual-channel credits, DRAM/GMI/IO arbitration, latency sampling, performance-counter selection, EDC counters, DSM single-write/error injection controls, GL2C crossbar credits and max burst, probe mapping, error status, DRAM bank arbitration, address-hash/select controls, and SDP enable.
- `SPI_PQEV_CTRL`, `SPI_SYS_COMPUTE`, and `SPI_SYS_WIF_CNTL`: small SPI queue-duration, compute-pipe, and WIF threshold fields.
- `RMI_*`: RMI general controls, status, subblock status, crossbar muxing, probe pop logic, XNACK/misc controls, demux and xbar arbiters, UTCL1 controls, TCIW formatter controls, scoreboard controls/status, dynamic-clock control, client-ID maps, spare bits, and RMI redundancy.
- `PMM_*` and `GCR_*`: PMM mode/disable controls, GCR PIO indexing/status/data, general GCR request behavior, target-disable masks, command status, and spare bits.
- `UTCL1_*`: UTCL1 page-size, bypass, cache, invalidation, memory-hub, address-log, and target-disable fields.
- `GC_ATC_L2_*`: ATC translation request limits, cache update modes, cache data readout words, invalidate delay, ATS request credits, parity/status, memory light sleep, clock control, and SDP port clock-enable fields.
- `GCVM_L2_*` and `GCVML2_WALKER_*`: GPUVM L2 enable, cache-policy, invalidation, status, dummy page, protection-fault control/status/address, identity aperture, cache partitions, group real-time classes, reserved client IDs, parity test controls, clock gating, fragment size, GCR client, and walker throttle fields.
- `GCVM_CONTEXT0_CNTL` and `GCVM_CONTEXT1_CNTL`: context enable, page-table depth/block size, retry policy, and interrupt/default behavior for range, dummy page, PDE0, valid, read, write, and execute protection faults.

## Control Flow And State Behavior

This header has no local control flow. Runtime control flow appears when AMDGPU and KFD code include the generated constants and use them in read-modify-write sequences against GC 10.1.0 registers.

The field families imply several hardware state machines and persistent hardware states:

- Tile and macrotile mode registers hold layout table entries that influence how the graphics block interprets color/depth metadata and surface addresses. Their state persists in the hardware register file until reset or reprogramming.
- Color-buffer and RMI controls affect cache, DCC, write-combine, early write-ack, arbitration, stutter, clock-gating, and backend repair behavior. These are global or semi-global graphics-pipeline settings rather than per-process software state.
- GCEA performance, EDC, DSM, probe, and error-status registers expose diagnostic state. Some fields count errors, inject errors, clear status, select counters, or indicate busy/error conditions; consumers must know whether fields are write-one-to-clear, sticky, read-only, or destructive from the hardware spec.
- RMI, GCR, UTCL1, ATC L2, and GCVM L2 fields encode virtual-memory translation behavior, invalidation, XNACK/retry behavior, cache and fragment-size policy, parity testing, walker throttling, and fault reporting. Incorrect sequencing here can affect all queues using the graphics hub.
- `GCVM_CONTEXT0_CNTL` and `GCVM_CONTEXT1_CNTL` are context-policy registers. They determine whether a VM context is enabled, the page-table layout expected by hardware, which protection faults raise interrupts, which use default pages, and whether retry behavior is enabled.

No software persistence is implemented here. Persistence is the hardware register contents themselves, managed by ASIC reset domains, suspend/resume save/restore, golden-register programming, VM hub initialization, and any runtime KFD/AMDGPU register writes.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk depends on the companion offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides matching `mm...` register addresses such as `mmGB_TILE_MODE25`, `mmGCEA_SDP_REQ_CNTL`, `mmRMI_GENERAL_CNTL`, `mmGC_ATC_L2_CNTL`, and `mmGCVM_CONTEXT0_CNTL`.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`, which includes this header and uses `GCVM_CONTEXT0_CNTL` fields to enable context 0, set page-table depth/block size, compute context register distance, and program VM hub context registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c`, `kfd_mqd_manager_v10.c`, and `kfd_packet_manager_v9.c`, which include the GC 10.1.0 shift/mask namespace for queue and memory-management programming.

Related integration points include AMDGPU VM hub initialization, KFD process/queue setup, GPUVM invalidation and retry-fault handling, golden-register programming, render-backend harvesting/repair, color-buffer cache/DCC setup, RMI arbitration, ATC L2 translation behavior, and low-level diagnostics for parity, EDC, DSM, probes, and performance counters.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently program adjacent bits in tiling, backend disable, cache policy, invalidation, or VM fault-control registers.
- The file gives status, control, clear, inject, and reserved fields the same macro shape. Driver code must rely on hardware documentation and existing access helpers to avoid writing read-only, sticky, clear-on-read, or write-one-to-clear fields incorrectly.
- VM context and L2 fields are high blast-radius controls. Bad values in `GCVM_L2_CNTL*`, `GCVM_L2_PROTECTION_FAULT_*`, `GCVM_INVALIDATE_CNTL`, or `GCVM_CONTEXT*_CNTL` can cause page faults, incorrect retry behavior, stale translations, dummy-page use where faults were expected, or GPU hangs.
- Tile and macrotiling definitions need to remain consistent with the address library and firmware expectations. Incorrect `ARRAY_MODE`, `PIPE_CONFIG`, `TILE_SPLIT`, bank geometry, or sample-split masks can present as data corruption rather than an immediate register-programming failure.
- Error injection and parity-test fields, such as DSM controls and `GCVM_L2_CACHE_PARITY_CNTL`, are dangerous if enabled outside validation paths.
- Many controls are global to graphics or memory-fabric behavior. A change made for one queue, context, or workload can affect unrelated graphics and compute clients.
- This slice starts and ends at chunk boundaries inside register groups: `GB_TILE_MODE24` is only partially covered here, and `GCVM_CONTEXT2_CNTL` only appears as a marker with its definitions in the next chunk.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU and KFD code paths that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`, especially `gfxhub_v2_0.c` and KFD v10 queue/MQD/packet managers.
- Generation checks that complete register groups in the full header have matching `__SHIFT` and `_MASK` definitions, with explicit chunk-boundary exceptions for the tail of `GB_TILE_MODE24` and the marker-only `GCVM_CONTEXT2_CNTL`.
- Cross-check this header against the GC 10.1.0 register database and companion offset names.
- Runtime VM tests on GC 10.1.0-class hardware: VM context enablement, page-table depth/block-size programming, VMID invalidation, retry faults, no-retry faults, dummy-page behavior, read/write/execute protection faults, XNACK behavior, and suspend/resume restoration.
- Graphics memory-layout tests: color/depth rendering with tile modes 24-31, DCC/CMASK/FMASK paths, backend-disable/harvesting configurations, and cache eviction/stutter behavior.
- Diagnostics and fault-injection validation: EDC counters, DSM injection paths, GCVM L2 parity controls, GCEA/RMI error status, performance-counter selection, and register readback of clear/status behavior.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 10059-12432 of `gc_10_1_0_sh_mask.h`. Earlier chunks should cover the beginning of `GB_TILE_MODE24` and prior GC register groups. Later chunks should start with the `GCVM_CONTEXT2_CNTL` definitions and continue the GCVM context/register map. The final per-file report should treat the whole file as a generated ASIC register bitfield map for AMD GC 10.1.0 programming, not as handwritten runtime logic.
