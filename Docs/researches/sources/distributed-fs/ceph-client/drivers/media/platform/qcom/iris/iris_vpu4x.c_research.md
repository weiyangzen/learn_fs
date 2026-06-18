# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu4x.c

## Purpose
Implements VPU4x-specific hardware power sequencing, including efuse-gated subdomains for VPP0, VPP1, and APV.

## Important APIs And Functions
- `iris_vpu4x_genpd_set_hwmode()` toggles genpd hardware mode across HW/VPP/APV domains, skipping efuse-disabled subdomains and rolling back on error.
- `iris_vpu4x_power_on_apv()` and `_power_off_apv()` enable/disable APV PM domain and clock, perform NoC LPI/reset handshakes, and reset the APV bridge.
- `iris_vpu4x_ahb_sync_reset_apv()` and `_hardware()` reset APV or core AHB bridges.
- `iris_vpu4x_enable_hardware_clocks()` and `_disable_hardware_clocks()` sequence AXI, HW freerun, HW, BSE, VPP0, and VPP1 clocks with efuse guards.
- `iris_vpu4x_power_on_hardware()` enables efuse-available PM domains/clocks and optional APV.
- `iris_vpu4x_power_off_hardware()` disables hwmode, powers off APV, waits for core idle/LPI/reset, resets AHB bridge, disables clocks, and powers down domains.
- `iris_vpu4x_set_hwmode()` resets APV/core bridges and enables genpd hwmode.
- `iris_vpu4x_ops` exports the VPU4x operation table.

## Control Flow And Integration Points
Although none of the listed platform data selects `iris_vpu4x_ops`, the file defines the next-generation operation table for platforms that include VPU4x support. It uses the same resource helpers and PM-domain enum values defined in platform common data.

## State And Persistence Behavior
Reads efuse state from `WRAPPER_EFUSE_MONITOR`, mutates PM-domain hardware mode, PM-domain runtime state, clocks, and hardware reset/LPI registers. No additional software persistence.

## Dependencies
Linux iopoll/reset helpers, VPU common controller functions, register defines, and resource clock/PM-domain helpers. Requires platform data with APV/VPP PM domains and BSE/VPP/APV clock mappings when used.

## Risks
- Efuse bits dynamically remove subdomains; tests must cover disabled VPP/APV combinations.
- Some poll return values in power-off paths are not propagated, so logs may be the only signal of timeout.
- Clock/domain unwind paths are complex and must stay symmetric with power-on.
- `iris_vpu4x_enc_line_size()` passes `inst->codec` as the HFI standard argument even though helper comparisons expect HFI codec constants in related code; this needs integration review if VPU4x encoder is enabled.

## Test Signals
- Platform bring-up with efuse combinations for all subdomains.
- Runtime PM suspend/resume loops with register tracing for LPI/reset ack.
- Failure injection at each clock/PM-domain enable step to validate unwind.
