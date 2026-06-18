# subset-b-005825 research

Grouped research for Linux Devicetree binding headers under `sources/distributed-fs/ceph-client/include/dt-bindings`, covering GPIO, I2C/I3C, IIO, input, and interconnect constant namespaces. Each source section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/aspeed-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/aspeed-gpio.h

## Purpose
defines stable GPIO line identifiers for the ASPEED aspeed gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 30 preprocessor constants. Representative symbols are `ASPEED_GPIO_PORT_A`, `ASPEED_GPIO_PORT_B`, `ASPEED_GPIO_PORT_C`, `ASPEED_GPIO_PORT_D`, `ASPEED_GPIO_PORT_E`, `ASPEED_GPIO_PORT_F`, `ASPEED_GPIO_PORT_G`, `ASPEED_GPIO_PORT_H`, `ASPEED_GPIO_PORT_I`, `ASPEED_GPIO_PORT_J`. The file uses guard `_DT_BINDINGS_GPIO_ASPEED_GPIO_H` and includes <dt-bindings/gpio/gpio.h>. numeric values span 0..28 across 29 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/aspeed-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/gpio.h

## Purpose
defines the generic GPIO active level, single-ended/open-drain/open-source, sleep retention, pull-up/down, and transitory flags used in the flag cell of GPIO Devicetree specifiers.

## Important APIs, Types, and Functions
The exported API is a set of bit-mask macros such as `GPIO_ACTIVE_HIGH`, `GPIO_ACTIVE_LOW`, `GPIO_OPEN_DRAIN`, `GPIO_OPEN_SOURCE`, `GPIO_PULL_UP`, and `GPIO_PULL_DOWN`. `GPIO_ASIS` is the all-zero default.

## Control Flow
There is no executable flow. DTS/DTSI files encode these macros in GPIO phandles; the Devicetree compiler substitutes constants; GPIO library parsing code later interprets the bits.

## State, Persistence, and Dependencies
The header stores no runtime state. Persistence is the ABI value baked into compiled device trees, so bit positions must remain stable. It has only its include guard and is consumed by board DTS files, GPIO controller bindings, and kernel GPIO-of translation helpers.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The risk is ABI drift: changing bit assignments breaks existing DTBs. Combining mutually exclusive flags such as open-drain and open-source also depends on downstream validation.

## Test Signals
Compile representative DTS users and verify `of_get_named_gpiod_flags()` or equivalent consumers decode polarity, drive mode, sleep, and pull flags as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-a1-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-a1-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson a1 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 62 preprocessor constants. Representative symbols are `GPIOP_0`, `GPIOP_1`, `GPIOP_2`, `GPIOP_3`, `GPIOP_4`, `GPIOP_5`, `GPIOP_6`, `GPIOP_7`, `GPIOP_8`, `GPIOP_9`. The file uses guard `_DT_BINDINGS_MESON_A1_GPIO_H` and has no header dependencies. numeric values span 0..61 across 62 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-a1-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-axg-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-axg-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson axg gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 101 preprocessor constants. Representative symbols are `GPIOAO_0`, `GPIOAO_1`, `GPIOAO_2`, `GPIOAO_3`, `GPIOAO_4`, `GPIOAO_5`, `GPIOAO_6`, `GPIOAO_7`, `GPIOAO_8`, `GPIOAO_9`. The file uses guard `_DT_BINDINGS_MESON_AXG_GPIO_H` and has no header dependencies. numeric values span 0..85 across 101 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-axg-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-g12a-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-g12a-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson g12a gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 100 preprocessor constants. Representative symbols are `GPIOAO_0`, `GPIOAO_1`, `GPIOAO_2`, `GPIOAO_3`, `GPIOAO_4`, `GPIOAO_5`, `GPIOAO_6`, `GPIOAO_7`, `GPIOAO_8`, `GPIOAO_9`. The file uses guard `_DT_BINDINGS_MESON_G12A_GPIO_H` and has no header dependencies. numeric values span 0..84 across 100 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-g12a-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-gxbb-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-gxbb-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson gxbb gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 134 preprocessor constants. Representative symbols are `GPIOAO_0`, `GPIOAO_1`, `GPIOAO_2`, `GPIOAO_3`, `GPIOAO_4`, `GPIOAO_5`, `GPIOAO_6`, `GPIOAO_7`, `GPIOAO_8`, `GPIOAO_9`. The file uses guard `_DT_BINDINGS_MESON_GXBB_GPIO_H` and has no header dependencies. numeric values span 0..118 across 134 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-gxbb-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-gxl-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-gxl-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson gxl gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 111 preprocessor constants. Representative symbols are `GPIOAO_0`, `GPIOAO_1`, `GPIOAO_2`, `GPIOAO_3`, `GPIOAO_4`, `GPIOAO_5`, `GPIOAO_6`, `GPIOAO_7`, `GPIOAO_8`, `GPIOAO_9`. The file uses guard `_DT_BINDINGS_MESON_GXL_GPIO_H` and has no header dependencies. numeric values span 0..99 across 111 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-gxl-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-s4-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-s4-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson s4 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 82 preprocessor constants. Representative symbols are `GPIOB_0`, `GPIOB_1`, `GPIOB_2`, `GPIOB_3`, `GPIOB_4`, `GPIOB_5`, `GPIOB_6`, `GPIOB_7`, `GPIOB_8`, `GPIOB_9`. The file uses guard `_DT_BINDINGS_MESON_S4_GPIO_H` and has no header dependencies. numeric values span 0..81 across 82 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson-s4-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson8-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson8-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson8 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 136 preprocessor constants. Representative symbols are `GPIOX_0`, `GPIOX_1`, `GPIOX_2`, `GPIOX_3`, `GPIOX_4`, `GPIOX_5`, `GPIOX_6`, `GPIOX_7`, `GPIOX_8`, `GPIOX_9`. The file uses guard `_DT_BINDINGS_MESON8_GPIO_H` and has no header dependencies. numeric values span 0..119 across 136 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson8-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson8b-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson8b-gpio.h

## Purpose
defines stable GPIO line identifiers for the Amlogic Meson meson8b gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 99 preprocessor constants. Representative symbols are `GPIOX_0`, `GPIOX_1`, `GPIOX_2`, `GPIOX_3`, `GPIOX_4`, `GPIOX_5`, `GPIOX_6`, `GPIOX_7`, `GPIOX_8`, `GPIOX_9`. The file uses guard `_DT_BINDINGS_MESON8B_GPIO_H` and has no header dependencies. numeric values span 0..82 across 99 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/meson8b-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/msc313-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/msc313-gpio.h

## Purpose
defines stable GPIO line identifiers for the SigmaStar MSC313 msc313 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 101 preprocessor constants. Representative symbols are `MSC313_GPIO_FUART`, `MSC313_GPIO_FUART_RX`, `MSC313_GPIO_FUART_TX`, `MSC313_GPIO_FUART_CTS`, `MSC313_GPIO_FUART_RTS`, `MSC313_GPIO_SR`, `MSC313_GPIO_SR_IO2`, `MSC313_GPIO_SR_IO3`, `MSC313_GPIO_SR_IO4`, `MSC313_GPIO_SR_IO5`. The file uses guard `_DT_BINDINGS_MSC313_GPIO_H` and has no header dependencies. numeric values span 0..0 across 2 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/msc313-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/nvidia,tegra264-gpio.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/nvidia,tegra264-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra-gpio.h

## Purpose
defines stable GPIO line identifiers for the NVIDIA Tegra tegra gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 33 preprocessor constants. Representative symbols are `TEGRA_GPIO_PORT_A`, `TEGRA_GPIO_PORT_B`, `TEGRA_GPIO_PORT_C`, `TEGRA_GPIO_PORT_D`, `TEGRA_GPIO_PORT_E`, `TEGRA_GPIO_PORT_F`, `TEGRA_GPIO_PORT_G`, `TEGRA_GPIO_PORT_H`, `TEGRA_GPIO_PORT_I`, `TEGRA_GPIO_PORT_J`. The file uses guard `_DT_BINDINGS_GPIO_TEGRA_GPIO_H` and includes <dt-bindings/gpio/gpio.h>. numeric values span 0..31 across 32 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra186-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra186-gpio.h

## Purpose
defines stable GPIO line identifiers for the NVIDIA Tegra tegra186 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 33 preprocessor constants. Representative symbols are `TEGRA186_MAIN_GPIO_PORT_A`, `TEGRA186_MAIN_GPIO_PORT_B`, `TEGRA186_MAIN_GPIO_PORT_C`, `TEGRA186_MAIN_GPIO_PORT_D`, `TEGRA186_MAIN_GPIO_PORT_E`, `TEGRA186_MAIN_GPIO_PORT_F`, `TEGRA186_MAIN_GPIO_PORT_G`, `TEGRA186_MAIN_GPIO_PORT_H`, `TEGRA186_MAIN_GPIO_PORT_I`, `TEGRA186_MAIN_GPIO_PORT_J`. The file uses guard `_DT_BINDINGS_GPIO_TEGRA186_GPIO_H` and includes <dt-bindings/gpio/gpio.h>. numeric values span 0..22 across 31 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra186-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra194-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra194-gpio.h

## Purpose
defines stable GPIO line identifiers for the NVIDIA Tegra tegra194 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 35 preprocessor constants. Representative symbols are `TEGRA194_MAIN_GPIO_PORT_A`, `TEGRA194_MAIN_GPIO_PORT_B`, `TEGRA194_MAIN_GPIO_PORT_C`, `TEGRA194_MAIN_GPIO_PORT_D`, `TEGRA194_MAIN_GPIO_PORT_E`, `TEGRA194_MAIN_GPIO_PORT_F`, `TEGRA194_MAIN_GPIO_PORT_G`, `TEGRA194_MAIN_GPIO_PORT_H`, `TEGRA194_MAIN_GPIO_PORT_I`, `TEGRA194_MAIN_GPIO_PORT_J`. The file uses guard `_DT_BINDINGS_GPIO_TEGRA194_GPIO_H` and includes <dt-bindings/gpio/gpio.h>. numeric values span 0..27 across 33 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra194-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra234-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra234-gpio.h

## Purpose
defines stable GPIO line identifiers for the NVIDIA Tegra tegra234 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 33 preprocessor constants. Representative symbols are `TEGRA234_MAIN_GPIO_PORT_A`, `TEGRA234_MAIN_GPIO_PORT_B`, `TEGRA234_MAIN_GPIO_PORT_C`, `TEGRA234_MAIN_GPIO_PORT_D`, `TEGRA234_MAIN_GPIO_PORT_E`, `TEGRA234_MAIN_GPIO_PORT_F`, `TEGRA234_MAIN_GPIO_PORT_G`, `TEGRA234_MAIN_GPIO_PORT_H`, `TEGRA234_MAIN_GPIO_PORT_I`, `TEGRA234_MAIN_GPIO_PORT_J`. The file uses guard `_DT_BINDINGS_GPIO_TEGRA234_GPIO_H` and includes <dt-bindings/gpio/gpio.h>. numeric values span 0..24 across 31 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra234-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra241-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra241-gpio.h

## Purpose
defines stable GPIO line identifiers for the NVIDIA Tegra tegra241 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 16 preprocessor constants. Representative symbols are `TEGRA241_MAIN_GPIO_PORT_A`, `TEGRA241_MAIN_GPIO_PORT_B`, `TEGRA241_MAIN_GPIO_PORT_C`, `TEGRA241_MAIN_GPIO_PORT_D`, `TEGRA241_MAIN_GPIO_PORT_E`, `TEGRA241_MAIN_GPIO_PORT_F`, `TEGRA241_MAIN_GPIO_PORT_G`, `TEGRA241_MAIN_GPIO_PORT_H`, `TEGRA241_MAIN_GPIO_PORT_I`, `TEGRA241_MAIN_GPIO_PORT_J`. The file uses guard `_DT_BINDINGS_GPIO_TEGRA241_GPIO_H` and includes <dt-bindings/gpio/gpio.h>. numeric values span 0..11 across 14 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra241-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra256-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra256-gpio.h

## Purpose
defines stable GPIO line identifiers for the NVIDIA Tegra tegra256 gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 5 preprocessor constants. Representative symbols are `TEGRA256_MAIN_GPIO_PORT_A`, `TEGRA256_MAIN_GPIO_PORT_B`, `TEGRA256_MAIN_GPIO_PORT_C`, `TEGRA256_MAIN_GPIO_PORT_D`, `TEGRA256_MAIN_GPIO`. The file uses guard `_DT_BINDINGS_GPIO_TEGRA256_GPIO_H` and includes <dt-bindings/gpio/gpio.h>. numeric values span 0..3 across 4 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/tegra256-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/uniphier-gpio.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/gpio/uniphier-gpio.h

## Purpose
defines stable GPIO line identifiers for the Socionext UniPhier uniphier gpio controller so Devicetree nodes can refer to pins by symbolic name instead of raw offsets.

## Important APIs, Types, and Functions
The exported API is 4 preprocessor constants. Representative symbols are `UNIPHIER_GPIO_LINES_PER_BANK`, `UNIPHIER_GPIO_IRQ_OFFSET`, `UNIPHIER_GPIO_PORT`, `UNIPHIER_GPIO_IRQ`. The file uses guard `_DT_BINDINGS_GPIO_UNIPHIER_H` and has no header dependencies. numeric values span 8..8 across 1 direct numeric defines.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/gpio/uniphier-gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/i2c/i2c.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/i2c/i2c.h

## Purpose
defines I2C client address flags for Devicetree: 10-bit addresses and slave-mode addresses.

## Important APIs, Types, and Functions
The exported macros are `I2C_TEN_BIT_ADDRESS`, `I2C_OWN_SLAVE_ADDRESS`. They are high-bit flags intended to be ORed into the `reg` address cell, not standalone bus operations.

## Control Flow
No code executes here. DTS authors place the flags in an I2C child `reg`; OF/I2C registration strips and interprets them when creating the client device.

## State, Persistence, and Dependencies
There is no state. The persisted ABI is the chosen high-bit encoding in compiled DTBs. The header is included by DTS files and consumed by I2C OF client creation code that recognizes `I2C_TEN_BIT_ADDRESS` and `I2C_OWN_SLAVE_ADDRESS`.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Using the flags as literal addresses, changing high-bit values, or colliding with valid address ranges can misregister devices.

## Test Signals
Compile DTS examples with 7-bit, 10-bit, and own-slave addresses; verify created `i2c_client` flags and stripped addresses match expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/i2c/i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/i3c/i3c.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/i3c/i3c.h

## Purpose
defines I3C Devicetree dynamic-address assignment flags.

## Important APIs, Types, and Functions
The visible API is `I2C_FM`, `I2C_FM_PLUS`, `I2C_FILTER`, `I2C_NO_FILTER_HIGH_FREQUENCY`, `I2C_NO_FILTER_LOW_FREQUENCY`, an address-slot flag used by I3C controller bindings when describing devices that need dynamic address assignment policy.

## Control Flow
There is no runtime flow in the header. The flag is compiled into DTB data and interpreted by I3C core/controller code while building the bus device list.

## State, Persistence, and Dependencies
No state is stored; the ABI is the flag bit value encoded in Devicetree. Integration is with I3C bus bindings and controller/client registration paths.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The risk is conflicting flag bits or missing controller-side validation, which can cause wrong dynamic-address handling.

## Test Signals
DTS compile tests and controller probe tests should verify dynamic-address assignment behavior with and without the flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/i3c/i3c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad4695.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad4695.h

## Purpose
defines IIO channel, mode, or configuration constants for the adi ad4695 binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 7 macro constants. Representative symbols are `AD4695_COMMON_MODE_REFGND`, `AD4695_COMMON_MODE_COM`, `AD4695_TRIGGER_EVENT_BUSY`, `AD4695_TRIGGER_EVENT_ALERT`, `AD4695_TRIGGER_PIN_GP0`, `AD4695_TRIGGER_PIN_GP2`, `AD4695_TRIGGER_PIN_GP3`. numeric values span 0..255 across 7 direct numeric defines. Top naming groups: `AD4695_TRIGGER` (5), `AD4695_COMMON` (2).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad4695.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad7606.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad7606.h

## Purpose
defines IIO channel, mode, or configuration constants for the adi ad7606 binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 2 macro constants. Representative symbols are `AD7606_TRIGGER_EVENT_BUSY`, `AD7606_TRIGGER_EVENT_FRSTDATA`. numeric values span 0..1 across 2 direct numeric defines. Top naming groups: `AD7606_TRIGGER` (2).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad7606.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad7768-1.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad7768-1.h

## Purpose
defines IIO channel, mode, or configuration constants for the adi ad7768 1 binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 3 macro constants. Representative symbols are `AD7768_TRIGGER_SOURCE_SYNC_OUT`, `AD7768_TRIGGER_SOURCE_GPIO3`, `AD7768_TRIGGER_SOURCE_DRDY`. numeric values span 0..2 across 3 direct numeric defines. Top naming groups: `AD7768_TRIGGER` (3).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/adi,ad7768-1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/at91-sama5d2_adc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/at91-sama5d2_adc.h

## Purpose
defines IIO channel, mode, or configuration constants for the at91 sama5d2 adc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 4 macro constants. Representative symbols are `AT91_SAMA5D2_ADC_X_CHANNEL`, `AT91_SAMA5D2_ADC_Y_CHANNEL`, `AT91_SAMA5D2_ADC_P_CHANNEL`, `AT91_SAMA7G5_ADC_TEMP_CHANNEL`. numeric values span 24..31 across 4 direct numeric defines. Top naming groups: `AT91_SAMA5D2` (3), `AT91_SAMA7G5` (1).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/at91-sama5d2_adc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/fsl-imx25-gcq.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/fsl-imx25-gcq.h

## Purpose
defines IIO channel, mode, or configuration constants for the fsl imx25 gcq binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 8 macro constants. Representative symbols are `MX25_ADC_REFP_YP`, `MX25_ADC_REFP_XP`, `MX25_ADC_REFP_EXT`, `MX25_ADC_REFP_INT`, `MX25_ADC_REFN_XN`, `MX25_ADC_REFN_YN`, `MX25_ADC_REFN_NGND`, `MX25_ADC_REFN_NGND2`. numeric values span 0..3 across 8 direct numeric defines. Top naming groups: `MX25_ADC` (8).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/fsl-imx25-gcq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/gehc,pmc-adc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/gehc,pmc-adc.h

## Purpose
defines IIO channel, mode, or configuration constants for the gehc pmc adc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 2 macro constants. Representative symbols are `GEHC_PMC_ADC_VOLTAGE`, `GEHC_PMC_ADC_CURRENT`. numeric values span 0..1 across 2 direct numeric defines. Top naming groups: `GEHC_PMC` (2).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/gehc,pmc-adc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/ingenic,adc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/ingenic,adc.h

## Purpose
defines IIO channel, mode, or configuration constants for the ingenic adc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 10 macro constants. Representative symbols are `INGENIC_ADC_AUX`, `INGENIC_ADC_BATTERY`, `INGENIC_ADC_AUX2`, `INGENIC_ADC_TOUCH_XP`, `INGENIC_ADC_TOUCH_YP`, `INGENIC_ADC_TOUCH_XN`, `INGENIC_ADC_TOUCH_YN`, `INGENIC_ADC_TOUCH_XD`, `INGENIC_ADC_TOUCH_YD`, `INGENIC_ADC_AUX0`. numeric values span 0..9 across 10 direct numeric defines. Top naming groups: `INGENIC_ADC` (10).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/ingenic,adc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6357-auxadc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6357-auxadc.h

## Purpose
defines IIO channel, mode, or configuration constants for the mediatek mt6357 auxadc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 13 macro constants. Representative symbols are `MT6357_AUXADC_BATADC`, `MT6357_AUXADC_ISENSE`, `MT6357_AUXADC_VCDT`, `MT6357_AUXADC_BAT_TEMP`, `MT6357_AUXADC_CHIP_TEMP`, `MT6357_AUXADC_ACCDET`, `MT6357_AUXADC_VDCXO`, `MT6357_AUXADC_TSX_TEMP`, `MT6357_AUXADC_HPOFS_CAL`, `MT6357_AUXADC_DCXO_TEMP`. numeric values span 0..12 across 13 direct numeric defines. Top naming groups: `MT6357_AUXADC` (13).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6357-auxadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6358-auxadc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6358-auxadc.h

## Purpose
defines IIO channel, mode, or configuration constants for the mediatek mt6358 auxadc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 14 macro constants. Representative symbols are `MT6358_AUXADC_BATADC`, `MT6358_AUXADC_VCDT`, `MT6358_AUXADC_BAT_TEMP`, `MT6358_AUXADC_CHIP_TEMP`, `MT6358_AUXADC_ACCDET`, `MT6358_AUXADC_VDCXO`, `MT6358_AUXADC_TSX_TEMP`, `MT6358_AUXADC_HPOFS_CAL`, `MT6358_AUXADC_DCXO_TEMP`, `MT6358_AUXADC_VBIF`. numeric values span 0..13 across 14 direct numeric defines. Top naming groups: `MT6358_AUXADC` (14).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6358-auxadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6359-auxadc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6359-auxadc.h

## Purpose
defines IIO channel, mode, or configuration constants for the mediatek mt6359 auxadc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 14 macro constants. Representative symbols are `MT6359_AUXADC_BATADC`, `MT6359_AUXADC_BAT_TEMP`, `MT6359_AUXADC_CHIP_TEMP`, `MT6359_AUXADC_ACCDET`, `MT6359_AUXADC_VDCXO`, `MT6359_AUXADC_TSX_TEMP`, `MT6359_AUXADC_HPOFS_CAL`, `MT6359_AUXADC_DCXO_TEMP`, `MT6359_AUXADC_VBIF`, `MT6359_AUXADC_VCORE_TEMP`. numeric values span 0..13 across 14 direct numeric defines. Top naming groups: `MT6359_AUXADC` (14).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6359-auxadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6363-auxadc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6363-auxadc.h

## Purpose
defines IIO channel, mode, or configuration constants for the mediatek mt6363 auxadc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 16 macro constants. Representative symbols are `MT6363_AUXADC_BATADC`, `MT6363_AUXADC_VCDT`, `MT6363_AUXADC_BAT_TEMP`, `MT6363_AUXADC_CHIP_TEMP`, `MT6363_AUXADC_VSYSSNS`, `MT6363_AUXADC_VTREF`, `MT6363_AUXADC_VCORE_TEMP`, `MT6363_AUXADC_VPROC_TEMP`, `MT6363_AUXADC_VGPU_TEMP`, `MT6363_AUXADC_VIN1`. numeric values span 0..15 across 16 direct numeric defines. Top naming groups: `MT6363_AUXADC` (16).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6363-auxadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6370_adc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6370_adc.h

## Purpose
defines IIO channel, mode, or configuration constants for the mediatek mt6370 adc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 10 macro constants. Representative symbols are `MT6370_CHAN_VBUSDIV5`, `MT6370_CHAN_VBUSDIV2`, `MT6370_CHAN_VSYS`, `MT6370_CHAN_VBAT`, `MT6370_CHAN_TS_BAT`, `MT6370_CHAN_IBUS`, `MT6370_CHAN_IBAT`, `MT6370_CHAN_CHG_VDDP`, `MT6370_CHAN_TEMP_JC`, `MT6370_CHAN_MAX`. numeric values span 0..9 across 10 direct numeric defines. Top naming groups: `MT6370_CHAN` (10).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6370_adc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6373-auxadc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6373-auxadc.h

## Purpose
defines IIO channel, mode, or configuration constants for the mediatek mt6373 auxadc binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 11 macro constants. Representative symbols are `MT6373_AUXADC_CHIP_TEMP`, `MT6373_AUXADC_VCORE_TEMP`, `MT6373_AUXADC_VPROC_TEMP`, `MT6373_AUXADC_VGPU_TEMP`, `MT6373_AUXADC_VIN1`, `MT6373_AUXADC_VIN2`, `MT6373_AUXADC_VIN3`, `MT6373_AUXADC_VIN4`, `MT6373_AUXADC_VIN5`, `MT6373_AUXADC_VIN6`. numeric values span 0..10 across 11 direct numeric defines. Top naming groups: `MT6373_AUXADC` (11).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adc/mediatek,mt6373-auxadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/addac/adi,ad74413r.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/addac/adi,ad74413r.h

## Purpose
defines IIO channel, mode, or configuration constants for the adi ad74413r binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 13 macro constants. Representative symbols are `CH_FUNC_HIGH_IMPEDANCE`, `CH_FUNC_VOLTAGE_OUTPUT`, `CH_FUNC_CURRENT_OUTPUT`, `CH_FUNC_VOLTAGE_INPUT`, `CH_FUNC_CURRENT_INPUT_EXT_POWER`, `CH_FUNC_CURRENT_INPUT_LOOP_POWER`, `CH_FUNC_RESISTANCE_INPUT`, `CH_FUNC_DIGITAL_INPUT_LOGIC`, `CH_FUNC_DIGITAL_INPUT_LOOP_POWER`, `CH_FUNC_CURRENT_INPUT_EXT_POWER_HART`. numeric values span 0..10 across 11 direct numeric defines. Top naming groups: `CH_FUNC` (13).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/addac/adi,ad74413r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adi,ad5592r.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/adi,ad5592r.h

## Purpose
defines IIO channel, mode, or configuration constants for the adi ad5592r binding, allowing Devicetree to describe ADC/ADDAC wiring using symbolic names.

## Important APIs, Types, and Functions
The exported API is 9 macro constants. Representative symbols are `CH_MODE_UNUSED`, `CH_MODE_ADC`, `CH_MODE_DAC`, `CH_MODE_DAC_AND_ADC`, `CH_MODE_GPIO`, `CH_OFFSTATE_PULLDOWN`, `CH_OFFSTATE_OUT_LOW`, `CH_OFFSTATE_OUT_HIGH`, `CH_OFFSTATE_OUT_TRISTATE`. numeric values span 0..8 across 9 direct numeric defines. Top naming groups: `CH_MODE` (5), `CH_OFFSTATE` (4).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with the named IIO binding YAML, board DTS files, and the matching ADC/ADDAC driver that interprets channel indexes, oversampling modes, or function values.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Misnumbered channels, renamed macros, or mismatched driver enum tables can route consumers to the wrong analog input or configuration mode.

## Test Signals
dtbs_check and driver probe tests should verify every exported constant accepted by the binding maps to the expected channel/configuration path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/adi,ad5592r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm7325.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm7325.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi adc7 pm7325 so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 43 macro constants. Representative symbols are `PM7325_SID`, `PM7325_ADC7_REF_GND`, `PM7325_ADC7_1P25VREF`, `PM7325_ADC7_VREF_VADC`, `PM7325_ADC7_DIE_TEMP`, `PM7325_ADC7_AMUX_THM1`, `PM7325_ADC7_AMUX_THM2`, `PM7325_ADC7_AMUX_THM3`, `PM7325_ADC7_AMUX_THM4`, `PM7325_ADC7_AMUX_THM5`. numeric values span 1..1 across 1 direct numeric defines. Top naming groups: `PM7325_ADC7` (42), `PM7325` (1).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm7325.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm8350.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm8350.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi adc7 pm8350 so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 42 macro constants. Representative symbols are `PM8350_ADC7_REF_GND`, `PM8350_ADC7_1P25VREF`, `PM8350_ADC7_VREF_VADC`, `PM8350_ADC7_DIE_TEMP`, `PM8350_ADC7_AMUX_THM1`, `PM8350_ADC7_AMUX_THM2`, `PM8350_ADC7_AMUX_THM3`, `PM8350_ADC7_AMUX_THM4`, `PM8350_ADC7_AMUX_THM5`, `PM8350_ADC7_GPIO1`. 42 expression-valued defines are present. Top naming groups: `PM8350_ADC7` (42).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm8350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm8350b.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm8350b.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi adc7 pm8350b so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 62 macro constants. Representative symbols are `PM8350B_SID`, `PM8350B_ADC7_REF_GND`, `PM8350B_ADC7_1P25VREF`, `PM8350B_ADC7_VREF_VADC`, `PM8350B_ADC7_DIE_TEMP`, `PM8350B_ADC7_AMUX_THM1`, `PM8350B_ADC7_AMUX_THM2`, `PM8350B_ADC7_AMUX_THM3`, `PM8350B_ADC7_AMUX_THM4`, `PM8350B_ADC7_AMUX_THM5`. numeric values span 3..3 across 1 direct numeric defines. Top naming groups: `PM8350B_ADC7` (61), `PM8350B` (1).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pm8350b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmk8350.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmk8350.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi adc7 pmk8350 so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 25 macro constants. Representative symbols are `PMK8350_SID`, `PMK8350_ADC7_REF_GND`, `PMK8350_ADC7_1P25VREF`, `PMK8350_ADC7_VREF_VADC`, `PMK8350_ADC7_DIE_TEMP`, `PMK8350_ADC7_AMUX_THM1`, `PMK8350_ADC7_AMUX_THM2`, `PMK8350_ADC7_AMUX_THM3`, `PMK8350_ADC7_AMUX_THM4`, `PMK8350_ADC7_AMUX_THM5`. numeric values span 0..0 across 1 direct numeric defines. Top naming groups: `PMK8350_ADC7` (24), `PMK8350` (1).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmk8350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmr735a.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmr735a.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi adc7 pmr735a so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 11 macro constants. Representative symbols are `PMR735A_SID`, `PMR735A_ADC7_REF_GND`, `PMR735A_ADC7_1P25VREF`, `PMR735A_ADC7_VREF_VADC`, `PMR735A_ADC7_DIE_TEMP`, `PMR735A_ADC7_GPIO1`, `PMR735A_ADC7_GPIO2`, `PMR735A_ADC7_GPIO3`, `PMR735A_ADC7_GPIO1_100K_PU`, `PMR735A_ADC7_GPIO2_100K_PU`. numeric values span 4..4 across 1 direct numeric defines. Top naming groups: `PMR735A_ADC7` (10), `PMR735A` (1).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmr735a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmr735b.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmr735b.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi adc7 pmr735b so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 11 macro constants. Representative symbols are `PMR735B_SID`, `PMR735B_ADC7_REF_GND`, `PMR735B_ADC7_1P25VREF`, `PMR735B_ADC7_VREF_VADC`, `PMR735B_ADC7_DIE_TEMP`, `PMR735B_ADC7_GPIO1`, `PMR735B_ADC7_GPIO2`, `PMR735B_ADC7_GPIO3`, `PMR735B_ADC7_GPIO1_100K_PU`, `PMR735B_ADC7_GPIO2_100K_PU`. numeric values span 5..5 across 1 direct numeric defines. Top naming groups: `PMR735B_ADC7` (10), `PMR735B` (1).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-pmr735b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-smb139x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-smb139x.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi adc7 smb139x so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 6 macro constants. Representative symbols are `SMB139x_1_ADC7_SMB_TEMP`, `SMB139x_1_ADC7_ICHG_SMB`, `SMB139x_1_ADC7_IIN_SMB`, `SMB139x_2_ADC7_SMB_TEMP`, `SMB139x_2_ADC7_ICHG_SMB`, `SMB139x_2_ADC7_IIN_SMB`. 6 expression-valued defines are present. Top naming groups: `SMB139x_1` (3), `SMB139x_2` (3).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-adc7-smb139x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-vadc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-vadc.h

## Purpose
defines Qualcomm SPMI VADC/ADC7 channel identifiers for qcom spmi vadc so PMIC ADC clients can request named measurements from Devicetree.

## Important APIs, Types, and Functions
The exported API is 256 macro constants. Representative symbols are `VADC_USBIN`, `VADC_DCIN`, `VADC_VCHG_SNS`, `VADC_SPARE1_03`, `VADC_USB_ID_MV`, `VADC_VCOIN`, `VADC_VBAT_SNS`, `VADC_VSYS`, `VADC_DIE_TEMP`, `VADC_REF_625MV`. numeric values span 0..255 across 256 direct numeric defines. Top naming groups: `VADC_LR` (44), `VADC_P` (32), `ADC7_AMUX` (24), `ADC5_AMUX` (20), `ADC5` (11).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with Qualcomm SPMI ADC/VADC bindings, PMIC DTS files, thermal/charger/battery consumers, and the qcom-spmi ADC drivers that decode channel ids and scaling selectors.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Channel-id drift or duplicated offsets can make battery, charger, die-temperature, or GPIO-ratio measurements read the wrong PMIC input.

## Test Signals
dtbs_check plus PMIC ADC driver probe tests should cover representative channel ids, ADC mux variants, thermal zone consumers, and scale/pre-scaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/qcom,spmi-vadc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/temperature/thermocouple.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/iio/temperature/thermocouple.h

## Purpose
defines thermocouple type identifiers for IIO temperature sensor bindings.

## Important APIs, Types, and Functions
The exported API is 8 macro constants. Representative symbols are `THERMOCOUPLE_TYPE_B`, `THERMOCOUPLE_TYPE_E`, `THERMOCOUPLE_TYPE_J`, `THERMOCOUPLE_TYPE_K`, `THERMOCOUPLE_TYPE_N`, `THERMOCOUPLE_TYPE_R`, `THERMOCOUPLE_TYPE_S`, `THERMOCOUPLE_TYPE_T`. numeric values span 0..7 across 8 direct numeric defines. Top naming groups: `THERMOCOUPLE_TYPE` (8).

## Control Flow
The header has no branches or function calls. Values are compiled into DTBs, then the corresponding IIO driver parses the property cells and maps them to channel specifications or mode tables.

## State, Persistence, and Dependencies
No runtime state is stored here. The persistent behavior is the numeric binding ABI used by existing DTBs and userspace-visible IIO channels after driver registration. It integrates with thermocouple-capable IIO sensor bindings and drivers that select conversion tables by type.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Changing numeric type ids or accepting invalid combinations can make temperature conversion use the wrong thermocouple curve.

## Test Signals
DTS compile tests and driver unit/probe tests should check each type maps to the intended conversion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/iio/temperature/thermocouple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/atmel-maxtouch.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/input/atmel-maxtouch.h

## Purpose
defines small input-subsystem binding constants for atmel maxtouch, such as key wakeup policy, GPIO key type selection, or haptic effect/library ids.

## Important APIs, Types, and Functions
The exported macros are `ATMEL_MXT_WAKEUP_NONE`, `ATMEL_MXT_WAKEUP_I2C_SCL`, `ATMEL_MXT_WAKEUP_GPIO`. numeric values span 0..2 across 3 direct numeric defines.

## Control Flow
There is no executable flow; values are compiled into DTB properties and consumed by the matching input driver during probe.

## State, Persistence, and Dependencies
No state is kept in the header. The ABI values persist in DTBs and affect input device registration or event reporting. Integration is through input binding YAML, board DTS files, and Linux input drivers that translate the values into event types, key properties, or haptics modes.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Numeric drift or missing validation can lead to wrong input event type, wake behavior, or haptic waveform selection.

## Test Signals
Run dtbs_check and probe the relevant input drivers with representative properties, confirming reported input capabilities and wake/haptic behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/atmel-maxtouch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/cros-ec-keyboard.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/input/cros-ec-keyboard.h

## Purpose
defines ChromeOS EC keyboard matrix position macros and function-row aliases used by Devicetree keymap descriptions.

## Important APIs, Types, and Functions
The exported macros include `CROS_STD_TOP_ROW_KEYMAP`, `CROS_STD_MAIN_KEYMAP`, `CROS_TOP_ROW_KEYMAP_V30`, `CROS_MAIN_KEYMAP_V30`; many values are `MATRIX_KEY(row, col, code)` expressions tying matrix coordinates to Linux key codes.

## Control Flow
No code runs here. DTS keymap nodes expand these macros into packed matrix entries, and the cros-ec keyboard/input driver later scans EC matrix events and reports the mapped Linux key code.

## State, Persistence, and Dependencies
No state is stored. The durable contract is the matrix coordinate and key-code layout in board DTBs. It includes or relies on `input.h`/Linux event-code definitions and integrates with ChromeOS EC keyboard bindings and matrix-keymap parsing.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Wrong row/column aliases or stale key-code constants produce swapped keys. Matrix-size changes must stay aligned with EC firmware and board wiring.

## Test Signals
DTS compile coverage, matrix-keymap parser tests, and board keyboard smoke tests should validate representative alphanumeric, function, and special keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/cros-ec-keyboard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/gpio-keys.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/input/gpio-keys.h

## Purpose
defines small input-subsystem binding constants for gpio keys, such as key wakeup policy, GPIO key type selection, or haptic effect/library ids.

## Important APIs, Types, and Functions
The exported macros are `EV_ACT_ANY`, `EV_ACT_ASSERTED`, `EV_ACT_DEASSERTED`. numeric values span 0..2 across 3 direct numeric defines.

## Control Flow
There is no executable flow; values are compiled into DTB properties and consumed by the matching input driver during probe.

## State, Persistence, and Dependencies
No state is kept in the header. The ABI values persist in DTBs and affect input device registration or event reporting. Integration is through input binding YAML, board DTS files, and Linux input drivers that translate the values into event types, key properties, or haptics modes.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Numeric drift or missing validation can lead to wrong input event type, wake behavior, or haptic waveform selection.

## Test Signals
Run dtbs_check and probe the relevant input drivers with representative properties, confirming reported input capabilities and wake/haptic behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/gpio-keys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/input.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/input/input.h

## Purpose
defines small input-subsystem binding constants for input, such as key wakeup policy, GPIO key type selection, or haptic effect/library ids.

## Important APIs, Types, and Functions
The exported macros are `MATRIX_KEY`. 1 expression-valued defines are present.

## Control Flow
There is no executable flow; values are compiled into DTB properties and consumed by the matching input driver during probe.

## State, Persistence, and Dependencies
No state is kept in the header. The ABI values persist in DTBs and affect input device registration or event reporting. Integration is through input binding YAML, board DTS files, and Linux input drivers that translate the values into event types, key properties, or haptics modes.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Numeric drift or missing validation can lead to wrong input event type, wake behavior, or haptic waveform selection.

## Test Signals
Run dtbs_check and probe the relevant input drivers with representative properties, confirming reported input capabilities and wake/haptic behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/linux-event-codes.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/input/linux-event-codes.h

## Purpose
exposes Linux input event, key, relative/absolute axis, switch, LED, sound, force-feedback, and property code constants to Devicetree users through the dt-bindings input symlink.

## Important APIs, Types, and Functions
The API is the full UAPI input-event code namespace: 795 macros such as `INPUT_PROP_POINTER`, `INPUT_PROP_DIRECT`, `INPUT_PROP_BUTTONPAD`, `INPUT_PROP_SEMI_MT`, `INPUT_PROP_TOPBUTTONPAD`, `INPUT_PROP_POINTING_STICK`, `INPUT_PROP_ACCELEROMETER`, `INPUT_PROP_PRESSUREPAD`, `INPUT_PROP_MAX`, `INPUT_PROP_CNT`. This path is a symlink to `sources/distributed-fs/ceph-client/include/uapi/linux/input-event-codes.h` and carries the same ABI as the kernel UAPI header.

## Control Flow
There is no executable flow. DTS files include the dt-bindings path for keymaps or GPIO-key codes; the compiler emits numeric event codes; input drivers report those codes through the Linux input subsystem.

## State, Persistence, and Dependencies
The header is immutable ABI data. Persistence is through compiled DTBs and userspace-visible event codes; values must match UAPI expectations. It depends on the UAPI input-event namespace and is consumed by keyboard matrices, GPIO keys, EC keyboards, touch/buttons, and any DT binding that names Linux input codes.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Any divergence from UAPI, broken symlink handling in source packaging, or use of unsupported event codes can break key reporting or userspace input interpretation.

## Test Signals
Compile DTS keymaps that include this path, compare representative constants against UAPI values, and exercise input drivers to confirm emitted EV_KEY/EV_ABS/etc. codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/linux-event-codes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/ti-drv260x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/input/ti-drv260x.h

## Purpose
defines small input-subsystem binding constants for ti drv260x, such as key wakeup policy, GPIO key type selection, or haptic effect/library ids.

## Important APIs, Types, and Functions
The exported macros are `DRV260X_LRA_MODE`, `DRV260X_LRA_NO_CAL_MODE`, `DRV260X_ERM_MODE`, `DRV260X_LIB_EMPTY`, `DRV260X_ERM_LIB_A`, `DRV260X_ERM_LIB_B`, `DRV260X_ERM_LIB_C`, `DRV260X_ERM_LIB_D`, and 3 more. numeric values span 0..7 across 11 direct numeric defines.

## Control Flow
There is no executable flow; values are compiled into DTB properties and consumed by the matching input driver during probe.

## State, Persistence, and Dependencies
No state is kept in the header. The ABI values persist in DTBs and affect input device registration or event reporting. Integration is through input binding YAML, board DTS files, and Linux input drivers that translate the values into event types, key properties, or haptics modes.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
Numeric drift or missing validation can lead to wrong input event type, wake behavior, or haptic waveform selection.

## Test Signals
Run dtbs_check and probe the relevant input drivers with representative properties, confirming reported input capabilities and wake/haptic behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/input/ti-drv260x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/fsl,imx8mp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/fsl,imx8mp.h

## Purpose
defines NXP i.MX interconnect node identifiers for fsl imx8mp, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 40 `#define` constants. Representative symbols are `IMX8MP_ICN_NOC`, `IMX8MP_ICN_MAIN`, `IMX8MP_ICS_DRAM`, `IMX8MP_ICS_OCRAM`, `IMX8MP_ICM_A53`, `IMX8MP_ICM_SUPERMIX`, `IMX8MP_ICM_GIC`, `IMX8MP_ICM_MLMIX`, `IMX8MP_ICN_AUDIO`, `IMX8MP_ICM_DSP`. numeric values span 0..39 across 40 direct numeric defines. Top naming groups: `IMX8MP_ICM` (30), `IMX8MP_ICN` (8), `IMX8MP_ICS` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the NXP i.MX interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/fsl,imx8mp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mm.h

## Purpose
defines NXP i.MX interconnect node identifiers for imx8mm, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 29 `#define` constants. Representative symbols are `IMX8MM_ICN_NOC`, `IMX8MM_ICS_DRAM`, `IMX8MM_ICS_OCRAM`, `IMX8MM_ICM_A53`, `IMX8MM_ICM_VPU_H1`, `IMX8MM_ICM_VPU_G1`, `IMX8MM_ICM_VPU_G2`, `IMX8MM_ICN_VIDEO`, `IMX8MM_ICM_GPU2D`, `IMX8MM_ICM_GPU3D`. numeric values span 1..29 across 29 direct numeric defines. Top naming groups: `IMX8MM_ICM` (19), `IMX8MM_ICN` (8), `IMX8MM_ICS` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the NXP i.MX interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mn.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mn.h

## Purpose
defines NXP i.MX interconnect node identifiers for imx8mn, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 23 `#define` constants. Representative symbols are `IMX8MN_ICN_NOC`, `IMX8MN_ICS_DRAM`, `IMX8MN_ICS_OCRAM`, `IMX8MN_ICM_A53`, `IMX8MN_ICM_GPU`, `IMX8MN_ICN_GPU`, `IMX8MN_ICM_CSI1`, `IMX8MN_ICM_CSI2`, `IMX8MN_ICM_ISI`, `IMX8MN_ICM_LCDIF`. numeric values span 1..23 across 23 direct numeric defines. Top naming groups: `IMX8MN_ICM` (15), `IMX8MN_ICN` (6), `IMX8MN_ICS` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the NXP i.MX interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mq.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mq.h

## Purpose
defines NXP i.MX interconnect node identifiers for imx8mq, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 28 `#define` constants. Representative symbols are `IMX8MQ_ICN_NOC`, `IMX8MQ_ICS_DRAM`, `IMX8MQ_ICS_OCRAM`, `IMX8MQ_ICM_A53`, `IMX8MQ_ICM_VPU`, `IMX8MQ_ICN_VIDEO`, `IMX8MQ_ICM_GPU`, `IMX8MQ_ICN_GPU`, `IMX8MQ_ICM_DCSS`, `IMX8MQ_ICN_DCSS`. numeric values span 1..28 across 28 direct numeric defines. Top naming groups: `IMX8MQ_ICM` (17), `IMX8MQ_ICN` (9), `IMX8MQ_ICS` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the NXP i.MX interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8183.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8183.h

## Purpose
defines MediaTek interconnect node identifiers for mediatek mt8183, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 11 `#define` constants. Representative symbols are `SLAVE_DDR_EMI`, `MASTER_MCUSYS`, `MASTER_MFG`, `MASTER_MMSYS`, `MASTER_MM_VPU`, `MASTER_MM_DISP`, `MASTER_MM_VDEC`, `MASTER_MM_VENC`, `MASTER_MM_CAM`, `MASTER_MM_IMG`. numeric values span 0..10 across 11 direct numeric defines. Top naming groups: `MASTER_MM` (7), `MASTER` (3), `SLAVE_DDR` (1).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the MediaTek interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8183.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8195.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8195.h

## Purpose
defines MediaTek interconnect node identifiers for mediatek mt8195, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 33 `#define` constants. Representative symbols are `SLAVE_DDR_EMI`, `MASTER_MCUSYS`, `MASTER_GPUSYS`, `MASTER_MMSYS`, `MASTER_MM_VPU`, `MASTER_MM_DISP`, `MASTER_MM_VDEC`, `MASTER_MM_VENC`, `MASTER_MM_CAM`, `MASTER_MM_IMG`. numeric values span 0..32 across 33 direct numeric defines. Top naming groups: `MASTER` (11), `MASTER_HRT` (8), `MASTER_MM` (7), `MASTER_PCIE` (2), `MASTER_VPU` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the MediaTek interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8195.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8196.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8196.h

## Purpose
defines MediaTek interconnect node identifiers for mediatek mt8196, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 38 `#define` constants. Representative symbols are `SLAVE_DDR_EMI`, `MASTER_MCUSYS`, `MASTER_MCU_0`, `MASTER_MCU_1`, `MASTER_MCU_2`, `MASTER_MCU_3`, `MASTER_MCU_4`, `MASTER_GPUSYS`, `MASTER_MMSYS`, `MASTER_MM_VPU`. numeric values span 0..37 across 38 direct numeric defines. Top naming groups: `MASTER` (12), `MASTER_HRT` (9), `MASTER_MM` (7), `MASTER_MCU` (5), `MASTER_VPU` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the MediaTek interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8196.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,eliza-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,eliza-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom eliza rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 113 `#define` constants. Representative symbols are `MASTER_QSPI_0`, `MASTER_QUP_1`, `MASTER_UFS_MEM`, `MASTER_USB3_0`, `SLAVE_A1NOC_SNOC`, `MASTER_QUP_2`, `MASTER_CRYPTO`, `MASTER_IPA`, `MASTER_SOCCP_AGGR_NOC`, `MASTER_QDSS_ETR`. numeric values span 0..29 across 113 direct numeric defines. Top naming groups: `SLAVE` (10), `MASTER` (6), `MASTER_CAMNOC` (4), `MASTER_CNOC` (4), `MASTER_QUP` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,eliza-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,glymur-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,glymur-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom glymur rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 175 `#define` constants. Representative symbols are `MASTER_CRYPTO`, `MASTER_SOCCP_PROC`, `MASTER_QDSS_ETR`, `MASTER_QDSS_ETR_1`, `SLAVE_A1NOC_SNOC`, `MASTER_UFS_MEM`, `MASTER_USB3_2`, `MASTER_USB4_2`, `SLAVE_A2NOC_SNOC`, `MASTER_QSPI_0`. numeric values span 0..51 across 175 direct numeric defines. Top naming groups: `SLAVE_PCIE` (23), `MASTER_PCIE` (13), `SLAVE` (12), `MASTER` (11), `MASTER_QUP` (6).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,glymur-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,icc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,icc.h

## Purpose
defines shared Qualcomm interconnect helper constants used by multiple SoC-specific interconnect bindings.

## Important APIs, Types, and Functions
The exported API is 9 `#define` constants. Representative symbols are `QCOM_ICC_BUCKET_AMC`, `QCOM_ICC_BUCKET_WAKE`, `QCOM_ICC_BUCKET_SLEEP`, `QCOM_ICC_NUM_BUCKETS`, `QCOM_ICC_TAG_AMC`, `QCOM_ICC_TAG_WAKE`, `QCOM_ICC_TAG_SLEEP`, `QCOM_ICC_TAG_ACTIVE_ONLY`, `QCOM_ICC_TAG_ALWAYS`. numeric values span 0..3 across 4 direct numeric defines. Top naming groups: `QCOM_ICC` (9).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It is included by Qualcomm interconnect DTS files or binding users that need shared tag/bus identifiers, and is interpreted by the qcom interconnect framework/provider drivers.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,icc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq5332.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq5332.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom ipq5332, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 39 `#define` constants. Representative symbols are `INTERCONNECT_QCOM_IPQ5332_H`, `MASTER_SNOC_PCIE3_1_M`, `SLAVE_SNOC_PCIE3_1_M`, `MASTER_ANOC_PCIE3_1_S`, `SLAVE_ANOC_PCIE3_1_S`, `MASTER_SNOC_PCIE3_2_M`, `SLAVE_SNOC_PCIE3_2_M`, `MASTER_ANOC_PCIE3_2_S`, `SLAVE_ANOC_PCIE3_2_S`, `MASTER_SNOC_USB`. numeric values span 0..25 across 38 direct numeric defines. Top naming groups: `MASTER_NSSNOC` (13), `SLAVE_NSSNOC` (13), `MASTER_SNOC` (3), `SLAVE_SNOC` (3), `MASTER_ANOC` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq5332.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq5424.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq5424.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom ipq5424, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 53 `#define` constants. Representative symbols are `INTERCONNECT_QCOM_IPQ5424_H`, `MASTER_ANOC_PCIE0`, `SLAVE_ANOC_PCIE0`, `MASTER_CNOC_PCIE0`, `SLAVE_CNOC_PCIE0`, `MASTER_ANOC_PCIE1`, `SLAVE_ANOC_PCIE1`, `MASTER_CNOC_PCIE1`, `SLAVE_CNOC_PCIE1`, `MASTER_ANOC_PCIE2`. numeric values span 0..37 across 52 direct numeric defines. Top naming groups: `MASTER_NSSNOC` (14), `SLAVE_NSSNOC` (14), `MASTER_CNOC` (6), `SLAVE_CNOC` (6), `MASTER_ANOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq5424.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq9574.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq9574.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom ipq9574, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 53 `#define` constants. Representative symbols are `INTERCONNECT_QCOM_IPQ9574_H`, `MASTER_ANOC_PCIE0`, `SLAVE_ANOC_PCIE0`, `MASTER_SNOC_PCIE0`, `SLAVE_SNOC_PCIE0`, `MASTER_ANOC_PCIE1`, `SLAVE_ANOC_PCIE1`, `MASTER_SNOC_PCIE1`, `SLAVE_SNOC_PCIE1`, `MASTER_ANOC_PCIE2`. numeric values span 0..41 across 52 direct numeric defines. Top naming groups: `MASTER_NSSNOC` (15), `SLAVE_NSSNOC` (15), `MASTER_ANOC` (4), `MASTER_SNOC` (4), `SLAVE_ANOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,ipq9574.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,kaanapali-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,kaanapali-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom kaanapali rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 127 `#define` constants. Representative symbols are `MASTER_QSPI_0`, `MASTER_CRYPTO`, `MASTER_QUP_1`, `MASTER_SDCC_4`, `MASTER_UFS_MEM`, `MASTER_USB3`, `MASTER_QUP_2`, `MASTER_QUP_3`, `MASTER_QUP_4`, `MASTER_IPA`. numeric values span 0..35 across 127 direct numeric defines. Top naming groups: `SLAVE` (12), `MASTER` (9), `MASTER_QUP` (9), `SLAVE_QUP` (9), `MASTER_CAMNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,kaanapali-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,milos-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,milos-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom milos rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 118 `#define` constants. Representative symbols are `MASTER_QUP_1`, `MASTER_UFS_MEM`, `MASTER_USB3_0`, `SLAVE_A1NOC_SNOC`, `MASTER_QDSS_BAM`, `MASTER_QSPI_0`, `MASTER_QUP_0`, `MASTER_CRYPTO`, `MASTER_IPA`, `MASTER_QDSS_ETR`. numeric values span 0..35 across 118 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (8), `SLAVE_PCIE` (5), `SLAVE_SERVICE` (5), `MASTER_CNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,milos-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8909.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8909.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8909, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 78 `#define` constants. Representative symbols are `MAS_APPS_PROC`, `MAS_OXILI`, `MAS_SNOC_BIMC_0`, `MAS_SNOC_BIMC_1`, `MAS_TCU_0`, `MAS_TCU_1`, `SLV_EBI`, `SLV_BIMC_SNOC`, `MAS_AUDIO`, `MAS_SPDM`. numeric values span 0..46 across 78 direct numeric defines. Top naming groups: `SLV` (10), `MAS` (9), `PCNOC_S` (7), `MM_INT` (4), `SLV_SNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8909.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8916.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8916.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8916, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 85 `#define` constants. Representative symbols are `BIMC_SNOC_SLV`, `MASTER_JPEG`, `MASTER_MDP_PORT0`, `MASTER_QDSS_BAM`, `MASTER_QDSS_ETR`, `MASTER_SNOC_CFG`, `MASTER_VFE`, `MASTER_VIDEO_P0`, `SNOC_MM_INT_0`, `SNOC_MM_INT_1`. numeric values span 0..49 across 85 direct numeric defines. Top naming groups: `SLAVE` (11), `MASTER` (7), `PCNOC_SLV` (7), `SNOC_BIMC` (4), `SNOC_MM` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8916.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8937.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8937.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8937, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 76 `#define` constants. Representative symbols are `MAS_APPS_PROC`, `MAS_OXILI`, `MAS_SNOC_BIMC_0`, `MAS_SNOC_BIMC_2`, `MAS_SNOC_BIMC_1`, `MAS_TCU_0`, `SLV_EBI`, `SLV_BIMC_SNOC`, `MAS_SPDM`, `MAS_BLSP_1`. numeric values span 0..42 across 76 direct numeric defines. Top naming groups: `SLV` (10), `MAS` (9), `PCNOC_S` (8), `SLV_SNOC` (5), `MAS_SNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8937.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8939.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8939.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8939, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 89 `#define` constants. Representative symbols are `BIMC_SNOC_SLV`, `MASTER_QDSS_BAM`, `MASTER_QDSS_ETR`, `MASTER_SNOC_CFG`, `PCNOC_SNOC_SLV`, `SLAVE_APSS`, `SLAVE_CATS_128`, `SLAVE_OCMEM_64`, `SLAVE_IMEM`, `SLAVE_QDSS_STM`. numeric values span 0..51 across 89 direct numeric defines. Top naming groups: `SLAVE` (11), `MASTER` (7), `PCNOC_SLV` (7), `SNOC_BIMC` (6), `SNOC_INT` (3).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8939.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8953.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8953.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8953, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 76 `#define` constants. Representative symbols are `MAS_APPS_PROC`, `MAS_OXILI`, `MAS_SNOC_BIMC_0`, `MAS_SNOC_BIMC_2`, `MAS_SNOC_BIMC_1`, `MAS_TCU_0`, `SLV_EBI`, `SLV_BIMC_SNOC`, `MAS_SPDM`, `MAS_BLSP_1`. numeric values span 0..41 across 76 direct numeric defines. Top naming groups: `MAS` (11), `SLV` (11), `PCNOC_S` (9), `SLV_SNOC` (5), `MAS_SNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8953.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8974.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8974.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8974, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 129 `#define` constants. Representative symbols are `BIMC_MAS_AMPSS_M0`, `BIMC_MAS_AMPSS_M1`, `BIMC_MAS_MSS_PROC`, `BIMC_TO_MNOC`, `BIMC_TO_SNOC`, `BIMC_SLV_EBI_CH0`, `BIMC_SLV_AMPSS_L2`, `CNOC_MAS_RPM_INST`, `CNOC_MAS_RPM_DATA`, `CNOC_MAS_RPM_SYS`. numeric values span 0..36 across 129 direct numeric defines. Top naming groups: `CNOC_SLV` (29), `PNOC_SLV` (15), `MNOC_SLV` (14), `SNOC_MAS` (12), `PNOC_MAS` (11).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8974.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8976.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8976.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8976, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 80 `#define` constants. Representative symbols are `MAS_APPS_PROC`, `MAS_SMMNOC_BIMC`, `MAS_SNOC_BIMC`, `MAS_TCU_0`, `SLV_EBI`, `SLV_BIMC_SNOC`, `MAS_USB_HS2`, `MAS_BLSP_1`, `MAS_USB_HS1`, `MAS_BLSP_2`. numeric values span 0..44 across 80 direct numeric defines. Top naming groups: `MAS` (9), `SLV` (7), `PCNOC_S` (6), `MAS_SDCC` (3), `PCNOC_INT` (3).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8976.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8996-cbf.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8996-cbf.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8996 cbf, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 2 `#define` constants. Representative symbols are `MASTER_CBF_M4M`, `SLAVE_CBF_M4M`. numeric values span 0..1 across 2 direct numeric defines. Top naming groups: `MASTER_CBF` (1), `SLAVE_CBF` (1).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8996-cbf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8996.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8996.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom msm8996, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 136 `#define` constants. Representative symbols are `MASTER_PCIE_0`, `MASTER_PCIE_1`, `MASTER_PCIE_2`, `MASTER_CNOC_A1NOC`, `MASTER_CRYPTO_CORE0`, `MASTER_PNOC_A1NOC`, `MASTER_USB3`, `MASTER_IPA`, `MASTER_UFS`, `MASTER_AMPSS_M0`. numeric values span 0..39 across 136 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (9), `SLAVE_PCIE` (6), `SLAVE_SMMU` (6), `SLAVE_SNOC` (6).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,msm8996.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,osm-l3.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,osm-l3.h

## Purpose
defines Qualcomm OSM/L3 interconnect performance-state identifiers used when describing CPU/L3 bandwidth or frequency votes.

## Important APIs, Types, and Functions
The exported API is 4 `#define` constants. Representative symbols are `MASTER_OSM_L3_APPS`, `SLAVE_OSM_L3`, `MASTER_EPSS_L3_APPS`, `SLAVE_EPSS_L3_SHARED`. numeric values span 0..1 across 4 direct numeric defines. Top naming groups: `MASTER_EPSS` (1), `MASTER_OSM` (1), `SLAVE_EPSS` (1), `SLAVE_OSM` (1).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm OSM L3 interconnect provider and CPU/cluster consumers in DTS.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,osm-l3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcm2290.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcm2290.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom qcm2290, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 75 `#define` constants. Representative symbols are `MASTER_APPSS_PROC`, `MASTER_SNOC_BIMC_RT`, `MASTER_SNOC_BIMC_NRT`, `MASTER_SNOC_BIMC`, `MASTER_TCU_0`, `MASTER_GFX3D`, `SLAVE_EBI1`, `SLAVE_BIMC_SNOC`, `MASTER_SNOC_CNOC`, `MASTER_QDSS_DAP`. numeric values span 0..34 across 75 direct numeric defines. Top naming groups: `SLAVE` (12), `MASTER` (6), `MASTER_SNOC` (5), `SLAVE_SNOC` (5), `MASTER_QDSS` (3).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcm2290.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs404.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs404.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom qcs404, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 73 `#define` constants. Representative symbols are `MASTER_AMPSS_M0`, `MASTER_OXILI`, `MASTER_MDP_PORT0`, `MASTER_SNOC_BIMC_1`, `MASTER_TCU_0`, `SLAVE_EBI_CH0`, `SLAVE_BIMC_SNOC`, `MASTER_SPDM`, `MASTER_BLSP_1`, `MASTER_BLSP_2`. numeric values span 0..45 across 73 direct numeric defines. Top naming groups: `PCNOC_S` (11), `SLAVE` (11), `MASTER` (7), `PCNOC_INT` (3), `SLAVE_SNOC` (3).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs404.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs615-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs615-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom qcs615 rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 117 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_QDSS_BAM`, `MASTER_QSPI`, `MASTER_QUP_0`, `MASTER_BLSP_1`, `MASTER_CNOC_A2NOC`, `MASTER_CRYPTO`, `MASTER_IPA`, `MASTER_EMAC_EVB`, `MASTER_PCIE`. numeric values span 1..43 across 117 direct numeric defines. Top naming groups: `SLAVE` (14), `MASTER` (12), `MASTER_CAMNOC` (6), `SLAVE_SERVICE` (5), `MASTER_SNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs615-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs8300-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs8300-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom qcs8300 rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 167 `#define` constants. Representative symbols are `MASTER_QUP_3`, `MASTER_EMAC`, `MASTER_SDC`, `MASTER_UFS_MEM`, `MASTER_USB2`, `MASTER_USB3_0`, `SLAVE_A1NOC_SNOC`, `MASTER_QDSS_BAM`, `MASTER_QUP_0`, `MASTER_QUP_1`. numeric values span 0..74 across 167 direct numeric defines. Top naming groups: `SLAVE` (15), `MASTER` (11), `SLAVE_SERVICE` (9), `SLAVE_PCIE` (7), `MASTER_QUP` (6).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qcs8300-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qdu1000-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qdu1000-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom qdu1000 rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 85 `#define` constants. Representative symbols are `MASTER_QUP_CORE_0`, `MASTER_QUP_CORE_1`, `SLAVE_QUP_CORE_0`, `SLAVE_QUP_CORE_1`, `MASTER_SYS_TCU`, `MASTER_APPSS_PROC`, `MASTER_GEMNOC_ECPRI_DMA`, `MASTER_FEC_2_GEMNOC`, `MASTER_ANOC_PCIE_GEM_NOC`, `MASTER_SNOC_GC_MEM_NOC`. numeric values span 0..67 across 85 direct numeric defines. Top naming groups: `SLAVE` (11), `MASTER` (7), `MASTER_QUP` (4), `MASTER_SNOC` (4), `SLAVE_QUP` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,qdu1000-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,rpm-icc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,rpm-icc.h

## Purpose
defines shared Qualcomm interconnect helper constants used by multiple SoC-specific interconnect bindings.

## Important APIs, Types, and Functions
The exported API is 3 `#define` constants. Representative symbols are `RPM_ACTIVE_TAG`, `RPM_SLEEP_TAG`, `RPM_ALWAYS_TAG`. 3 expression-valued defines are present. Top naming groups: `RPM_ACTIVE` (1), `RPM_ALWAYS` (1), `RPM_SLEEP` (1).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It is included by Qualcomm interconnect DTS files or binding users that need shared tag/bus identifiers, and is interpreted by the qcom interconnect framework/provider drivers.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,rpm-icc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sa8775p-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sa8775p-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sa8775p rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 193 `#define` constants. Representative symbols are `MASTER_QUP_3`, `MASTER_EMAC`, `MASTER_EMAC_1`, `MASTER_SDC`, `MASTER_UFS_MEM`, `MASTER_USB2`, `MASTER_USB3_0`, `MASTER_USB3_1`, `SLAVE_A1NOC_SNOC`, `MASTER_QDSS_BAM`. numeric values span 0..85 across 193 direct numeric defines. Top naming groups: `SLAVE` (15), `MASTER` (12), `SLAVE_SERVICE` (10), `MASTER_QUP` (8), `SLAVE_PCIE` (8).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sa8775p-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sar2130p-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sar2130p-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sar2130p rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 117 `#define` constants. Representative symbols are `MASTER_QUP_CORE_0`, `MASTER_QUP_CORE_1`, `SLAVE_QUP_CORE_0`, `SLAVE_QUP_CORE_1`, `MASTER_GEM_NOC_CNOC`, `MASTER_GEM_NOC_PCIE_SNOC`, `MASTER_QDSS_DAP`, `SLAVE_AHB2PHY_SOUTH`, `SLAVE_AOSS`, `SLAVE_CAMERA_CFG`. numeric values span 0..47 across 117 direct numeric defines. Top naming groups: `SLAVE` (11), `MASTER` (8), `SLAVE_LPASS` (5), `SLAVE_SERVICE` (5), `MASTER_QDSS` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sar2130p-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc7180.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc7180.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sc7180, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 135 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_QSPI`, `MASTER_QUP_0`, `MASTER_SDCC_2`, `MASTER_EMMC`, `MASTER_UFS_MEM`, `SLAVE_A1NOC_SNOC`, `SLAVE_SERVICE_A1NOC`, `MASTER_A2NOC_CFG`, `MASTER_QDSS_BAM`. numeric values span 0..52 across 135 direct numeric defines. Top naming groups: `SLAVE` (14), `MASTER` (11), `SLAVE_NPU` (10), `SLAVE_SERVICE` (7), `MASTER_CAMNOC` (6).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc7180.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc7280.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc7280.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sc7280, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 142 `#define` constants. Representative symbols are `MASTER_QSPI_0`, `MASTER_QUP_0`, `MASTER_QUP_1`, `MASTER_A1NOC_CFG`, `MASTER_PCIE_0`, `MASTER_PCIE_1`, `MASTER_SDCC_1`, `MASTER_SDCC_2`, `MASTER_SDCC_4`, `MASTER_UFS_MEM`. numeric values span 0..46 across 142 direct numeric defines. Top naming groups: `SLAVE` (14), `SLAVE_SERVICE` (9), `MASTER` (8), `MASTER_CNOC` (4), `MASTER_QUP` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc7280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc8180x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc8180x.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sc8180x, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 164 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_UFS_CARD`, `MASTER_UFS_GEN4`, `MASTER_UFS_MEM`, `MASTER_USB3`, `MASTER_USB3_1`, `MASTER_USB3_2`, `A1NOC_SNOC_SLV`, `SLAVE_SERVICE_A1NOC`, `MASTER_A2NOC_CFG`. numeric values span 0..56 across 164 direct numeric defines. Top naming groups: `SLAVE` (15), `MASTER` (10), `SLAVE_PCIE` (8), `SLAVE_SERVICE` (7), `MASTER_CAMNOC` (6).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc8180x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc8280xp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc8280xp.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sc8280xp, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 196 `#define` constants. Representative symbols are `MASTER_QSPI_0`, `MASTER_QUP_1`, `MASTER_QUP_2`, `MASTER_A1NOC_CFG`, `MASTER_IPA`, `MASTER_EMAC_1`, `MASTER_SDCC_4`, `MASTER_UFS_MEM`, `MASTER_USB3_0`, `MASTER_USB3_1`. numeric values span 0..84 across 196 direct numeric defines. Top naming groups: `SLAVE_PCIE` (15), `SLAVE` (14), `MASTER` (11), `SLAVE_SERVICE` (11), `MASTER_PCIE` (8).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sc8280xp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm660.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm660.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sdm660, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 97 `#define` constants. Representative symbols are `MASTER_IPA`, `MASTER_CNOC_A2NOC`, `MASTER_SDCC_1`, `MASTER_SDCC_2`, `MASTER_BLSP_1`, `MASTER_BLSP_2`, `MASTER_UFS`, `MASTER_USB_HS`, `MASTER_USB3`, `MASTER_CRYPTO_C0`. numeric values span 0..35 across 97 direct numeric defines. Top naming groups: `SLAVE` (15), `MASTER` (9), `MASTER_CNOC` (3), `MASTER_QDSS` (3), `MASTER_SNOC` (3).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm660.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm670-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm670-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sdm670 rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 116 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_BLSP_1`, `MASTER_TSIF`, `MASTER_EMMC`, `MASTER_SDCC_2`, `MASTER_SDCC_4`, `MASTER_UFS_MEM`, `SLAVE_A1NOC_SNOC`, `SLAVE_SERVICE_A1NOC`, `MASTER_A2NOC_CFG`. numeric values span 0..40 across 116 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (9), `SLAVE_SERVICE` (7), `MASTER_CAMNOC` (6), `MASTER_SNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm670-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm845.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm845.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sdm845, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 130 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_TSIF`, `MASTER_SDCC_2`, `MASTER_SDCC_4`, `MASTER_UFS_CARD`, `MASTER_UFS_MEM`, `MASTER_PCIE_0`, `SLAVE_A1NOC_SNOC`, `SLAVE_SERVICE_A1NOC`, `SLAVE_ANOC_PCIE_A1NOC_SNOC`. numeric values span 0..46 across 130 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (12), `SLAVE_SERVICE` (7), `MASTER_CAMNOC` (6), `MASTER_SNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdm845.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx55.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx55.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sdx55, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 58 `#define` constants. Representative symbols are `MASTER_LLCC`, `SLAVE_EBI_CH0`, `MASTER_TCU_0`, `MASTER_SNOC_GC_MEM_NOC`, `MASTER_AMPSS_M0`, `SLAVE_LLCC`, `SLAVE_MEM_NOC_SNOC`, `SLAVE_MEM_NOC_PCIE_SNOC`, `MASTER_AUDIO`, `MASTER_BLSP_1`. numeric values span 0..49 across 58 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (7), `MASTER_MEM` (2), `MASTER_QDSS` (2), `MASTER_SNOC` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx55.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx65.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx65.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sdx65, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 55 `#define` constants. Representative symbols are `MASTER_LLCC`, `SLAVE_EBI1`, `MASTER_TCU_0`, `MASTER_SNOC_GC_MEM_NOC`, `MASTER_APPSS_PROC`, `SLAVE_LLCC`, `SLAVE_MEM_NOC_SNOC`, `SLAVE_MEM_NOC_PCIE_SNOC`, `MASTER_AUDIO`, `MASTER_BLSP_1`. numeric values span 0..46 across 55 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (6), `MASTER_MEM` (2), `MASTER_QDSS` (2), `MASTER_SNOC` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx65.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx75.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx75.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sdx75, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 85 `#define` constants. Representative symbols are `MASTER_QUP_CORE_0`, `SLAVE_QUP_CORE_0`, `MASTER_LLCC`, `SLAVE_EBI1`, `MASTER_CNOC_DC_NOC`, `SLAVE_LAGG_CFG`, `SLAVE_MCCC_MASTER`, `SLAVE_GEM_NOC_CFG`, `SLAVE_SNOOP_BWMON`, `MASTER_SYS_TCU`. numeric values span 0..59 across 85 direct numeric defines. Top naming groups: `SLAVE` (11), `SLAVE_PCIE` (8), `MASTER` (7), `MASTER_PCIE` (5), `MASTER_GEM` (3).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx75.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm6115.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm6115.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sm6115, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 89 `#define` constants. Representative symbols are `MASTER_AMPSS_M0`, `MASTER_SNOC_BIMC_RT`, `MASTER_SNOC_BIMC_NRT`, `SNOC_BIMC_MAS`, `MASTER_GRAPHICS_3D`, `MASTER_TCU_0`, `SLAVE_EBI_CH0`, `BIMC_SNOC_SLV`, `SNOC_CNOC_MAS`, `MASTER_QDSS_DAP`. numeric values span 0..48 across 89 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (5), `MASTER_QDSS` (3), `MASTER_SNOC` (3), `SLAVE_CAMERA` (3).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm6115.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm6350.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm6350.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sm6350, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 127 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_QUP_0`, `MASTER_EMMC`, `MASTER_UFS_MEM`, `A1NOC_SNOC_SLV`, `SLAVE_SERVICE_A1NOC`, `MASTER_A2NOC_CFG`, `MASTER_QDSS_BAM`, `MASTER_QUP_1`, `MASTER_CRYPTO_CORE_0`. numeric values span 0..44 across 127 direct numeric defines. Top naming groups: `SLAVE` (13), `SLAVE_NPU` (8), `MASTER` (7), `SLAVE_SERVICE` (7), `MASTER_CAMNOC` (6).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm6350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm7150-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm7150-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sm7150 rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 127 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_QUP_0`, `MASTER_TSIF`, `MASTER_EMMC`, `MASTER_SDCC_2`, `MASTER_SDCC_4`, `MASTER_UFS_MEM`, `A1NOC_SNOC_SLV`, `SLAVE_SERVICE_A1NOC`, `MASTER_A2NOC_CFG`. numeric values span 0..50 across 127 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (11), `MASTER_CAMNOC` (8), `SLAVE_SERVICE` (6), `MASTER_CNOC` (3).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm7150-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8150.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8150.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sm8150, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 138 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_QUP_0`, `MASTER_EMAC`, `MASTER_UFS_MEM`, `MASTER_USB3`, `MASTER_USB3_1`, `A1NOC_SNOC_SLV`, `SLAVE_SERVICE_A1NOC`, `MASTER_A2NOC_CFG`, `MASTER_QDSS_BAM`. numeric values span 0..53 across 138 direct numeric defines. Top naming groups: `SLAVE` (14), `MASTER` (13), `MASTER_CAMNOC` (6), `SLAVE_SERVICE` (6), `SLAVE_PCIE` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8150.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8250.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8250.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sm8250, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 154 `#define` constants. Representative symbols are `MASTER_A1NOC_CFG`, `MASTER_QSPI_0`, `MASTER_QUP_1`, `MASTER_QUP_2`, `MASTER_TSIF`, `MASTER_PCIE_2`, `MASTER_SDCC_4`, `MASTER_UFS_MEM`, `MASTER_USB3`, `MASTER_USB3_1`. numeric values span 0..51 across 154 direct numeric defines. Top naming groups: `SLAVE` (12), `MASTER` (9), `SLAVE_NPU` (9), `SLAVE_SERVICE` (9), `MASTER_QUP` (6).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8350.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8350.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sm8350, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 140 `#define` constants. Representative symbols are `MASTER_QSPI_0`, `MASTER_QUP_1`, `MASTER_A1NOC_CFG`, `MASTER_SDCC_4`, `MASTER_UFS_MEM`, `MASTER_USB3_0`, `MASTER_USB3_1`, `SLAVE_A1NOC_SNOC`, `SLAVE_SERVICE_A1NOC`, `MASTER_QDSS_BAM`. numeric values span 0..60 across 140 direct numeric defines. Top naming groups: `SLAVE` (13), `SLAVE_SERVICE` (10), `MASTER` (9), `SLAVE_LPASS` (4), `SLAVE_PCIE` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8350.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8450.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8450.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sm8450, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 150 `#define` constants. Representative symbols are `MASTER_QSPI_0`, `MASTER_QUP_1`, `MASTER_A1NOC_CFG`, `MASTER_SDCC_4`, `MASTER_UFS_MEM`, `MASTER_USB3_0`, `SLAVE_A1NOC_SNOC`, `SLAVE_SERVICE_A1NOC`, `MASTER_QDSS_BAM`, `MASTER_QUP_0`. numeric values span 0..54 across 150 direct numeric defines. Top naming groups: `SLAVE` (11), `MASTER` (10), `SLAVE_SERVICE` (8), `MASTER_QUP` (6), `SLAVE_QUP` (6).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8450.h -->
