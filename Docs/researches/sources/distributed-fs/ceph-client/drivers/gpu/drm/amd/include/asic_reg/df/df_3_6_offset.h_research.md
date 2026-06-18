# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/df/df_3_6_offset.h

## Purpose
`df_3_6_offset.h` maps AMD Data Fabric 3.6 register names to MMIO or SMN addresses. It supports DF access-control, clock-gating, memory-interleave discovery, DF performance counters, indirect fabric configuration access, DRAM range reads, and RAS hardware-assert mask reads.

## Important APIs, Types, And Functions
The macro surface includes `mmFabricConfigAccessControl`, `mmDF_PIE_AON0_DfGlobalClkGater`, `mmDF_CS_UMC_AON0_DfGlobalCtrl`, `mmDF_CS_UMC_AON0_DramBaseAddress0`, `mmDF_GCM_AON0_DramMegaBaseAddress0`, and hardware assert mask registers. It also exports SMN addresses for `smnPerfMonCtlLo0` through `smnPerfMonCtlHi7`, `smnPerfMonCtrLo0` through `smnPerfMonCtrHi7`, fabric indirect config access address/data registers, and SMN DRAM base/limit registers.

## Control Flow
The header itself is declarative. In `df_v3_6.c`, its macros drive several flows: initialization queries hash/interleave state, broadcast mode reads and writes `mmFabricConfigAccessControl`, channel discovery reads either `mmDF_GCM_AON0_DramMegaBaseAddress0` for Aldebaran or `mmDF_CS_UMC_AON0_DramBaseAddress0` otherwise, perfmon code programs the SMN perfmon control and counter pairs, and RAS poison detection reads hardware assert mask low/high registers.

## State, Persistence, And Dependencies
The file has no software persistence. The addressed registers represent hardware state in DF, UMC-facing memory decode logic, performance monitors, and RAS controls. MMIO-style `mm*` constants depend on SOC15 accessors and `_BASE_IDX` values; `smn*` constants depend on SMN read/write helpers used elsewhere in the AMDGPU stack.

## Integration Points
`df_v3_6.c` includes this header directly. `amdgpu_xgmi.c` also includes it, so XGMI or multi-GPU fabric code can reuse the DF 3.6 address definitions. The macros integrate with `RREG32_SOC15`, `WREG32_SOC15`, SMN register helpers, `REG_GET_FIELD`, and the `amdgpu_df_funcs` operation table.

## Risks
Address drift is the primary risk: perfmon control/counter pairs, indirect access data registers, and RAS mask registers are sensitive to exact offsets. Mixing MMIO `mm*` and SMN `smn*` access paths is another risk because the same logical block appears through different address spaces. ASIC-specific differences, such as Aldebaran's alternate DRAM interleave mask, require consumers to choose the right macro set.

## Test Signals
Validation signals include successful DF perfmon allocation and counter reads, known-good HBM channel counts on both Aldebaran and non-Aldebaran devices, XGMI/fabric discovery tests, RAS poison-mode reporting from hardware assert masks, and register-access tracing that confirms SMN addresses are used only with SMN helpers.
