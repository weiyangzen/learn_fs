# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 40017-42372

## Chunk Scope

This chunk is a generated AMD GC 12.1 register field header segment. It contains C preprocessor `#define` constants for bit shifts and masks, not executable functions. The definitions cover late graphics clock-gating controls, shader-array/user configuration, GRBMH remap controls, and a large GCVM/GCMC/GCUTCL2 virtual-memory register block. It is paired with `gc_12_1_0_offset.h`: offset macros identify MMIO registers, while this header identifies fields inside those 32-bit registers for `REG_SET_FIELD`, `REG_GET_FIELD`, direct shifts, and direct mask operations.

The range begins in the middle of `CGTT_PH_CLK_CTRL3`, so the first `CGTT_PH_CLK_CTRL3__SOFT_OVERRIDE*` definitions depend on earlier lines for the complete register field set. The chunk also ends in the middle of `GCVM_INVALIDATE_ENG11_REQ`; engines 12-17 request fields and later acknowledgement/range registers are outside this chunk.

## Purpose

The constants let GC 12.1 driver code program ASIC-specific hardware registers without embedding raw bit numbers at every call site. The visible register families support:

- Clock gating and power management overrides for TCP, LDS, UTCL1, GRBMH, scan converter, GL1 cache blocks, GCUTCL2, and GCVM L2.
- Shader engine/user-visible topology controls such as inactive WGPs, RB backend disablement, RMI redundancy repair, shader rate, GL1 pipe steering, and GL1 hash configuration.
- Remapping of WGP and RB resources through GRBMH hypervisor decode registers, including per-side SA0/SA1 remap enables and remap targets.
- GC memory-controller and VM apertures for framebuffer, AGP, system aperture, default page, dummy page, and identity mappings.
- GCVM L2 TLB/cache setup, cache invalidation, context control, protection-fault behavior, parity/debug/throttle controls, translation-assist request/response registers, and invalidation engine semaphore/request fields.

## Important Macro Groups

Clock-gating groups include `GFX_ICG_TCP_CTRL`, `GFX_ICG_TCP_CTRL2`, `ICG_LDS_CLK_CTRL`, `GFX_ICG_UTCL1_CTRL`, `GFX_ICG_GRBMH_CTRL`, `CGTT_SC_CLK_CTRL0..4`, `ICG_GL1C_CLK_CTRL`, `ICG_GL1XC_CLK_CTRL`, `ICG_GL1A_CTRL`, `ICG_GL1XA_CTRL`, and `GCUTCL2_ICG_CTRL` / `GCVM_L2_ICG_CTRL`. Most fields are `*_OVERRIDE`, `SOFT_OVERRIDE_*`, `OFF_HYSTERESIS`, `ON_DELAY`, `DYNAMIC_CLOCK_OVERRIDE`, `STATIC_CLOCK_OVERRIDE`, `AON_CLOCK_OVERRIDE`, or `PERFMON_CLOCK_OVERRIDE`. Driver code can force clock domains on/off, tune gating hysteresis, or keep debug/performance domains active.

Shader/topology groups include `GL1_PIPE_STEER_LSB`, `GL1_PIPE_STEER_MSB`, `GL1_HASH_CFG`, `GC_USER_SHADER_ARRAY_CONFIG`, `GC_USER_RB_BACKEND_DISABLE`, `GC_USER_RMI_REDUNDANCY`, and `GC_USER_SHADER_RATE_CONFIG_1`. These encode inactive WGP masks, RB backend masks, RMI repair controls, shader-rate fields, and GL1 steering/hash fields. `gfx_v12_1.c` uses the user shader array and RB backend masks when deriving active WGP/RB topology and programming harvested units.

GRBMH remap groups include `GRBMH_WGP_SA0_REMAP_CNTL`, `GRBMH_WGP_SA1_REMAP_CNTL`, `GRBMH_RB_SA0_REMAP_CNTL`, and `GRBMH_RB_SA1_REMAP_CNTL`. The WGP controls expose per-side `SIDE{0,1}_WGP{0..10}_SA{0,1}_REMAP_EN`, `REMAP_TO_SIDE`, and `REMAP_TO_WGP` fields; RB controls expose per-RB enable and remap target fields. These are low-level topology repair/remap knobs.

VM aperture and shared-function groups include `GCMC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_{LSB,MSB}`, `GCMC_VM_FB_LOCATION_*`, `GCMC_VM_AGP_*`, `GCMC_VM_SYSTEM_APERTURE_*`, `GCMC_VM_MX_L1_TLB_CNTL`, and `GCMC_SHARED_ACTIVE_FCN_ID`. `gfxhub_v12_1.c` uses these register families to configure framebuffer/AGP/system apertures, default page addresses, L1 TLB behavior, and SR-IOV-visible framebuffer copy registers.

GCVM L2 groups include `GCVM_L2_CNTL`, `GCVM_L2_CNTL2`, `GCVM_L2_CNTL3`, `GCVM_L2_CNTL4`, `GCVM_L2_CNTL5`, `GCVM_L2_STATUS`, `GCVM_L2_MM_GROUP_RT_CLASSES`, bank-select, parity, GCR, PTE-cache dump, throttle, debug, and credit-safety registers. These fields configure L2 cache enablement, fragment processing, endian modes, PDE/PTE cache sizing and associativity, invalidate behavior, bank selection, parity checking/injection, page-walker throttling, credit updates, and fault-interrupt routing.

Protection-fault groups include `GCVM_L2_PROTECTION_FAULT_CNTL_LO32`, `GCVM_L2_PROTECTION_FAULT_CNTL_HI32`, `GCVM_L2_PROTECTION_FAULT_CNTL2`, `GCVM_L2_PROTECTION_FAULT_MM_CNTL3/4`, status/address/default-address registers, and `GCVML2_IH_FAULT_INTERRUPT_CNTL`. They cover fault status clearing, subsequent update allowance, default fault behavior for range/PDE/valid/read/write/execute/dummy faults, client-id interrupt masks, crash-on-fault controls, retry-fault interrupt controls, active page migration retry behavior, poison interrupt routing, and logged fault fields such as walker error, permission faults, CID, RW, VMID, VF, and VFID.

Context groups include repeated `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL` definitions plus `GCVM_CONTEXTS_DISABLE`. Each context control register has the same field layout in this chunk: `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry flags for permission/invalid and other faults, and interrupt/default bits for range, dummy-page, PDE0, valid, read, write, and execute protection faults. `GCVM_CONTEXTS_DISABLE` provides one disable bit per context 0-15.

Invalidation groups include `GCVM_INVALIDATE_ENG0_SEM` through `GCVM_INVALIDATE_ENG17_SEM` and request layouts for `GCVM_INVALIDATE_ENG0_REQ` through the visible portion of `GCVM_INVALIDATE_ENG11_REQ`. Request fields include `PER_VMID_INVALIDATE_REQ`, `FLUSH_TYPE`, `INVALIDATE_L2_PTES`, `INVALIDATE_L2_PDE0..3`, `INVALIDATE_L1_PTES`, `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, `LOG_REQUEST`, and `INVALIDATE_4K_PAGES_ONLY`.

Translation-assist groups include `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_REQUEST_ADDR_*`, request attributes, response address, and response attributes. They encode VMID/VFID/VF, GPA mode, requested permissions, client ID, request bit, response permissions, fragment size, snoop/SPA/IO/TMZ/no-PTE/MTYPE/compression/NACK/HDM/TMPM retry, and ACK.

## Control Flow and State Behavior

There is no local control flow because the file is declarative. Runtime control flow appears in consumers:

- `gfxhub_v12_1.c` reads and writes GCVM/GCMC registers through `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, and `WREG32_SOC15_OFFSET`, using these masks with `REG_SET_FIELD` / `REG_GET_FIELD`.
- GFX hub initialization programs VM page-table base/start/end registers, system/AGP/framebuffer apertures, default fault pages, L1 TLB controls, GCVM L2 cache controls, context control registers, and identity apertures.
- VM invalidation code builds `GCVM_INVALIDATE_ENG0_REQ` values with the request masks in this chunk, then writes invalidate request registers and polls related semaphore/acknowledgement state from adjacent register definitions.
- Fault handling reads `GCVM_L2_PROTECTION_FAULT_STATUS_LO32` and decodes status bits from this chunk to report more faults, walker errors, permission failures, mapping errors, VMID/client fields, and access direction.
- KFD queue management copies `hub->vm_cntx_cntl` and toggles `GCVM_CONTEXT0_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT__SHIFT` for per-process XNACK behavior.

The state represented here is persistent hardware state, not software-owned memory. Values survive as MMIO register contents until rewritten by initialization, reset, suspend/resume restore, virtualization policy, or hardware events. Some fields are configuration state, such as context enable bits and cache sizing. Others are status or command-like state, such as fault status bits, invalidation request bits, semaphore bits, PTE dump readiness, credit update strobes, and translation-assist request/ack bits.

## Dependencies and Integration Points

This header depends on the AMDGPU register access macro stack understanding the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention. In practice, `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)` concatenate these names to find the generated shift/mask macros.

Known direct includers in the GC 12.1 code path include `amdgpu/gfxhub_v12_1.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/mes_v12_1.c`, `amdgpu/sdma_v7_1.c`, `amdgpu/imu_v12_1.c`, `amdgpu/soc_v1_0.c`, `amdgpu/amdgpu_amdkfd_gfx_v12_1.c`, and KFD queue/MQD managers. The VM and fault fields are most tightly integrated with `gfxhub_v12_1.c`; shader-array and RB fields are used by `gfx_v12_1.c`; XNACK retry control is used by `kfd_device_queue_manager_v12_1.c`.

The source is ASIC-version-specific. Similar names exist in older `gc_10_*` and `gc_12_0_0` headers, but field positions can differ. For example, GC 12.1 `GCVM_CONTEXT0_CNTL__PAGE_TABLE_BLOCK_SIZE__SHIFT` is visible at bit 4 in this chunk, while older GC headers place comparable fields differently. Reusing constants across ASIC generations would silently program wrong bits.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can break GPU VM setup, page fault retry behavior, invalidation, cache coherency, clock-gating, or resource harvesting without compiler errors.
- Repeated context and invalidate-engine definitions invite copy/paste or generator mistakes. Context 0-15 should remain layout-identical in this chunk; invalidate engine request definitions should remain layout-identical across engines, with the caveat that this chunk truncates after part of engine 11.
- Clock-gating override fields can affect power, hangs, and performance. Misprogramming `*_OVERRIDE`, `ALWAYS_BUSY`, or hysteresis fields may hide hardware idle/busy transitions or keep domains active.
- Fault-control fields are security and reliability sensitive. Defaults for read/write/execute/valid/PDE faults, retry-fault interrupts, no-retry crash behavior, and status clearing affect whether GPU VM faults are recoverable, visible, or fatal.
- SR-IOV/VF fields and framebuffer copy registers interact with virtualization policy. `gfxhub_v12_1.c` already avoids some aperture programming for VFs; any future consumer of `GCMC_SHARED_ACTIVE_FCN_ID` or `GCMC_VM_FB_LOCATION_*` must preserve PF/VF access rules.
- The line range starts and ends mid-register-family. A merged per-file report must reconcile neighboring chunks for complete `CGTT_PH_CLK_CTRL3` and `GCVM_INVALIDATE_ENG11+` coverage.

## Test and Validation Signals

- Build coverage: compile AMDGPU/KFD with GC 12.1 support so all `REG_SET_FIELD` / `REG_GET_FIELD` references resolve against this header and its offset companion.
- Boot/init signal: on GC 12.1 hardware or simulator, `gfxhub_v12_1` should initialize GART/system apertures, GCVM L2 controls, context controls, and identity aperture registers without VM hub timeouts.
- VM invalidation signal: GPUVM map/unmap and TLB invalidation paths should complete, with invalidation engine semaphore/ack polling not timing out.
- Fault signal: intentional GPUVM fault tests should decode `GCVM_L2_PROTECTION_FAULT_STATUS_LO32` fields coherently and should respect retry/no-retry and XNACK settings.
- KFD signal: per-process XNACK enable/disable should toggle the GCVM context retry bit consistently with `SH_MEM_CONFIG__RETRY_DISABLE`, and compute queues should continue to launch.
- Topology signal: harvested WGP/RB configurations should produce expected inactive WGP and RB backend masks in `gfx_v12_1.c`.
- Power/performance signal: clock-gating register programming should not regress idle power, hang detection, perf counter access, or workload stability.
