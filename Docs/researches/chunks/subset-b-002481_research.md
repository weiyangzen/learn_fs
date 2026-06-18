# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 12396-14895

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU and AMDKFD code to compose and decode 32-bit MMIO register values. The matching register addresses and base indices live in `gc_10_3_0_offset.h`.

The selected range starts at the end of `GCVM_CONTEXT15_CNTL`, covers GCVM context disable, GCVM invalidate engines, VM aperture/location controls, GCEA memory and IO arbitration controls, TCP invalidate/status fields, and begins the shader program register definitions for pixel and vertex stages. Although this repository subtree is named `ceph-client`, this file is GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or callbacks in this range. The exposed API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for the same field.
- Consumers pair these constants with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` macros from `gc_10_3_0_offset.h`, then use AMDGPU helper patterns such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

Major register groups in this chunk:

- GCVM context controls: the chunk begins with `GCVM_CONTEXT15_CNTL` protection-fault enable/default masks, then defines `GCVM_CONTEXTS_DISABLE` bits for disabling VM contexts 0 through 15.
- GCVM invalidate engines 0 through 17: each engine has a `*_SEM` semaphore bit, `*_REQ` fields for per-VMID invalidation, flush type, L2 PTE/PDE0/PDE1/PDE2 invalidation, L1 PTE invalidation, protection-fault status-address clear, request logging, and 4K-only invalidation, plus `*_ACK` acknowledgement status and `*_ADDR_RANGE_LO32/HI32` physical address range fields. `gfxhub_v2_0.c` and `gfxhub_v2_1.c` use the engine 0 request masks via `REG_SET_FIELD` and derive engine spacing from the adjacent offset macros.
- GCVM page-table base and range registers: contexts 0 through 15 expose low/high 32-bit page-table base, start, and end address fields. These describe VM context page-table placement and logical address bounds but do not implement the page-table programming sequence.
- Per-PF/VF PTE cache fragment sizing: `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and context 0 through 15 variants define small-page fragment size, large-page fragment size, and bank select fields used by the GCVM L2 PTE cache path.
- Shared GCVM PF decode controls: `GCMC_VM_NB_MMIOBASE`, `GCMC_VM_NB_MMIOLIMIT`, `GCMC_VM_NB_PCI_CTRL`, PCI arbitration, top-of-DRAM registers, framebuffer offset, system aperture default address, VM steering, virtual reset request/status fields, memory power light sleep, cacheable DRAM ranges, APT control, local HBM aperture lock/start/end, active function ID, XGMI LFB control/size, framebuffer no-allocate controls, and `GCUTCL2_HARVEST_BYPASS_GROUPS`.
- Shared GCVM VC decode controls: framebuffer location base/top, AGP top/bottom/base, system aperture low/high logical addresses, and `GCMC_VM_MX_L1_TLB_CNTL` fields such as L1 TLB enable, system access mode, unmapped access behavior, advanced driver model enable, ECO bits, and memory type.
- GCEA arbitration controls: DRAM and IO read/write client-to-group maps assign client IDs 0 through 31 to four groups; group-to-VC maps assign groups to virtual channels; lazy, CAM, burst, age, queueing, fixed-priority, urgency, urgency-mask, and quantization registers tune read/write arbitration for DRAM and IO traffic.
- TCP and TCI controls: `TCP_INVALIDATE` exposes a start bit, `TCP_STATUS` reports pending/stalled/invalidate and UTCL1 request state, `TCP_EDC_CNT` reports parity/EDC counts, `TCI_STATUS` exposes VM/TLB status, and `TCI_CNTL_1/2` publish control fields for the texture cache interface.
- Pixel shader program setup: `SPI_SHADER_PGM_RSRC4_PS`, checksum, `RSRC3`, program low/high address, `RSRC1`, `RSRC2`, 32 user data registers, request-control fields, and four user accumulation contribution fields. Important resource fields include VGPR/SGPR counts, priority, float mode, privilege, DX10 clamp, IEEE mode, VGPR component count, CU group enable, memory ordered and forward progress bits, FP16 overflow behavior, scratch enable, user SGPR count, trap presence, LDS and stream-output enables, exception enable mask, PC base enable, dispatch/draw enable, and shared VGPR count.
- Vertex shader program setup: equivalent VS program resource, checksum, late allocation, address, `RSRC1/RSRC2`, and user data registers 0 through 30 within this chunk. The next chunk continues with `SPI_SHADER_USER_DATA_VS_31` and `SPI_SHADER_REQ_CTRL_VS`.

Many full-register data fields use `0xFFFFFFFFL` masks, especially address/data and shader user-data registers. Field names are descriptive, but access permissions and programming sequences are not encoded in this header.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU and AMDKFD consumers:

1. GFX10.3 code includes `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
2. Driver paths select a concrete register using the `mm*` offset macro and base index.
3. The code composes or extracts fields using the shift and mask macros from this header.
4. MMIO helper calls read or write the register while higher-level VM, cache, shader, reset, power, or firmware paths provide ordering and synchronization.

The GCVM invalidate fields are a good example: the header only defines bits. `gfxhub_v2_0.c`/`gfxhub_v2_1.c` build a request with `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, and L1/L2 invalidation bits, program optional address ranges, write invalidate request registers, and poll acknowledgement through hub structures that use the register offsets. The header does not encode semaphore acquisition, acknowledgement polling, timeout policy, VMID ownership, or fault logging decisions.

Shader program resource fields are similarly declarative. The chunk defines how PS and VS resource registers are packed, but command submission, pipeline state assembly, shader upload, trap/debug setup, scratch allocation, stream-output configuration, and wave scheduling rules live in the driver, firmware, and hardware programming model.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state exposed through GC 10.3 registers.

The represented hardware state includes VM context enable/disable bits, per-engine TLB/cache invalidation request and acknowledgement state, invalidate address ranges, page-table base/start/end addresses for contexts 0 through 15, PTE cache fragment sizing, PCI/MMIO/DRAM/framebuffer/aperture/TLB configuration, virtual reset and active-function state, GCEA client grouping and arbitration policy, TCP/TCI invalidate and status state, and PS/VS shader program configuration.

Persistence is hardware-defined. Some fields are durable configuration until GPU reset, suspend/resume, power-gating, VF reset, or explicit reprogramming. Others are live status bits, write-triggered strobes, self-clearing request bits, hardware-owned counters/status, or address/data payload registers. The macros do not identify read-only, write-only, write-one-to-clear, sticky, latched, protected, or reserved behavior, so consumers must rely on the ASIC programming guide and preserve unrelated bits when updating mixed-control registers.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which provides the corresponding MMIO offsets and base indices. Enum/default/generated headers such as AMD ASIC enum files provide values for fields where a mask alone is not enough.

Known direct include users of this GC 10.3.0 shift/mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`

The same field names are also used by common GFX hub code patterns in nearby IP versions, especially for `GCVM_INVALIDATE_ENG0_REQ`, address-range programming, semaphore/request/ack register offsets, and engine-distance calculations. Integration points include GPU VM setup, page-table aperture programming, TLB and PTE-cache invalidation, memory partitioning and virtualization, PCI/MMIO aperture setup, XGMI/local framebuffer handling, reset and power management, cache invalidation, shader stage programming, KFD queue setup, and profiling/debug paths that read status or program shader resources.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. Pairing `gc_10_3_0_sh_mask.h` with a different GC offset header can compile while programming the wrong register or field.
- The macros are untyped constants. A wrong register name or stale mask can silently affect the wrong VMID, invalidate engine, context, aperture, GCEA client group, priority coefficient, texture cache control, or shader resource field.
- GCVM invalidation is sequencing-sensitive. Semaphore ownership, request construction, optional address range setup, VMID masks, flush type, L1/L2/PDE selections, acknowledgement polling, timeout handling, and fault-status clearing must be coordinated by consumers.
- Context and aperture registers are security- and isolation-sensitive. Incorrect base/start/end addresses, AGP/framebuffer/system aperture bounds, active function IDs, VF reset controls, or PF/VF cache fragment settings can cause VM faults, memory exposure across processes or VFs, or GPU hangs.
- Several register families are replicated by context or invalidate engine. Code that assumes wrong spacing between engine or context registers can pass static compilation but program a neighboring engine/context at runtime.
- GCEA arbitration knobs can create performance cliffs or starvation. Client-to-group, group-to-VC, age, urgency, queueing, burst, and masking fields need ASIC-specific defaults and workload validation; small bitfield mistakes may appear only as bandwidth or latency regressions.
- Full-width masks do not imply safe writes. Address payloads, user-data registers, status fields, and hardware-owned state can all expose `0xFFFFFFFFL`; access semantics still come from the hardware spec and call site.
- Shader `RSRC1/RSRC2` fields interact with compiler output and queue state. Incorrect VGPR/SGPR counts, scratch enable, user SGPR count, trap, exception, stream-output, PC base, shared VGPR, or forward-progress fields can produce invalid waves, bad memory accesses, missed traps, or hard-to-debug rendering and compute failures.
- The chunk boundary is artificial. It starts after part of `GCVM_CONTEXT15_CNTL` and ends at `SPI_SHADER_USER_DATA_VS_30`; adjacent chunks are needed for the complete context-control and VS request-control view.

## Test Signals

Useful validation is mostly build, static, and hardware coverage:

- Build coverage for AMDGPU, AMDKFD, SDMA, GFX hub, and SMU files that include the GC 10.3.0 shift/mask header with `gc_10_3_0_offset.h`.
- Generated-header checks that every `__SHIFT` has a matching `_MASK`, masks are aligned to their shifts, replicated engine/context/register families have consistent spacing and field layouts, and register names match entries in the offset header.
- Static checks for non-overlapping fields within each register except documented aliases or full-width data/status fields.
- VM stress tests that create and destroy many GPUVM mappings, update page tables, trigger per-VMID invalidations, use address-range invalidation, and verify acknowledgement polling and timeout behavior.
- Fault-path tests for valid/read/write/execute/range/dummy/PDE protection faults, including logging and fault-status-address clearing where supported.
- Reset, suspend/resume, runtime power-management, and SR-IOV/PF/VF tests that verify context, aperture, cache fragment, active-function, and virtual reset state is restored or reinitialized correctly.
- Memory aperture tests covering framebuffer, AGP, system aperture, cacheable DRAM, local HBM, XGMI LFB, and no-allocate settings, with attention to VM faults and cross-process or cross-VF isolation.
- GCEA bandwidth/latency tests using DRAM and IO read/write workloads to catch client mapping, priority, urgency, burst, or masking field regressions.
- TCP/TCI cache invalidation smoke tests that write the `TCP_INVALIDATE` start bit, poll relevant status, and run texture/cache-heavy workloads after invalidation.
- Graphics and compute shader tests that exercise PS/VS resource programming across VGPR/SGPR pressure, scratch use, traps/exceptions, stream output, user SGPR/user-data registers, shared VGPR count, and forward progress; regression signals include zero or corrupted output, VM faults, hangs, missed traps, or failures isolated to GFX10.3 ASICs.
