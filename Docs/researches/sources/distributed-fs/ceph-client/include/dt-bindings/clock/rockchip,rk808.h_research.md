# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk808.h

## Purpose
`rockchip,rk808.h` defines the clock-output indices for the Rockchip RK808 PMIC clock provider.

## Important APIs, types, and functions
The complete API is `RK808_CLKOUT0` and `RK808_CLKOUT1`. There are no functions or data structures.

## Control flow
Consumers include the header and reference one of the clock-output IDs in a PMIC clock phandle. The RK808 PMIC clock driver resolves the index and controls or exposes the matching hardware clock output.

## State and persistence
The header is stateless. PMIC register state determines whether each output is enabled and what downstream devices receive it.

## Dependencies and integration points
It integrates with Rockchip board DTS files, RK808 MFD/PMIC support, common clock framework registration, and peripherals that use PMIC-provided 32 kHz or reference outputs.

## Risks and test signals
Risks are limited but include swapping clockout indexes and breaking boards that route one output to Wi-Fi, Bluetooth, RTC, or codec components. Test signals include PMIC clock provider registration, correct `assigned-clocks` behavior, and downstream peripheral probe success.
