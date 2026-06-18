# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/nvidia,tegra264-gpio.h

## Purpose
defines stable GPIO line identifiers for the NVIDIA Tegra nvidia tegra264 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 32 preprocessor constants. Representative symbols are `TEGRA264_MAIN_GPIO_PORT_T`, `TEGRA264_MAIN_GPIO_PORT_U`, `TEGRA264_MAIN_GPIO_PORT_V`, `TEGRA264_MAIN_GPIO_PORT_W`, `TEGRA264_MAIN_GPIO_PORT_AL`, `TEGRA264_MAIN_GPIO_PORT_Y`, `TEGRA264_MAIN_GPIO_PORT_Z`, `TEGRA264_MAIN_GPIO_PORT_X`, `TEGRA264_MAIN_GPIO_PORT_H`, `TEGRA264_MAIN_GPIO_PORT_J`. The file uses guard `_DT_BINDINGS_GPIO_TEGRA264_GPIO_H` and includes <dt-bindings/gpio/gpio.h>. numeric values span 0..18 across 29 direct numeric defines.

## Control Flow
There is no executable control flow. Pinctrl/GPIO device-tree entries use these names in specifier cells; the C preprocessor resolves them before DTB generation; the matching GPIO or pinctrl driver receives the resulting integer offset.

## State, Persistence, and Dependencies
The header has no mutable state or persistence logic. The persistent contract is the numeric namespace encoded into DTBs and expected by the platform GPIO/pinctrl driver. Integration is through DTS includes under the same SoC family, gpio-ranges and pinctrl bindings, and platform drivers that map these offsets to register banks or port/pin tuples.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Risks are off-by-one numbering, bank-boundary mistakes, duplicate values, and renumbering a published pin. Those errors route interrupts or GPIO consumers to the wrong hardware line.

## Test Signals
Useful signals are dtbs_check coverage, DTS compile coverage for every symbolic pin group, driver probe on boards using first/last pins in each bank, and duplicate-value scans across the header.
