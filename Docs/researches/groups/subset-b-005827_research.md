# subset-b-005827 Research

Grouped research for Linux devicetree binding headers under `sources/distributed-fs/ceph-client/include/dt-bindings`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra234-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra234-mc.h

Purpose: NVIDIA Tegra234 memory-controller binding constants for Stream IDs, memory client IDs, and ICC CPU-cluster dummy clients.

Important APIs/types/functions: This header exports 362 DT-visible macros in the `memory` binding namespace. Main API surface: The exported surface is split into special SIDs, ISO/NISO0/NISO1/shared SIDs, hundreds of `TEGRA234_MEMORY_CLIENT_*` IDs, and `TEGRA_ICC_MC_CPU_CLUSTER*` interconnect IDs. First exported macros: `TEGRA234_SID_INVALID`, `TEGRA234_SID_PASSTHROUGH`, `TEGRA234_SID_ISO_NVDISPLAY`, `TEGRA234_SID_ISO_VI`, `TEGRA234_SID_ISO_VIFALC`, `TEGRA234_SID_ISO_VI2`, `TEGRA234_SID_ISO_VI2FALC`, `TEGRA234_SID_ISO_VI_VM2`. Last exported macros: `TEGRA234_MEMORY_CLIENT_MIU6W`, `TEGRA234_MEMORY_CLIENT_NVJPG1SRD`, `TEGRA234_MEMORY_CLIENT_NVJPG1SWR`, `TEGRA_ICC_MC_CPU_CLUSTER0`, `TEGRA_ICC_MC_CPU_CLUSTER1`, `TEGRA_ICC_MC_CPU_CLUSTER2`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: It is consumed by Tegra DT nodes and memory/interconnect/SMMU drivers that must agree on stream identity, client register indexes, and bandwidth client IDs. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra234-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra30-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra30-mc.h

Purpose: Tegra30 memory-controller binding constants for software groups, MC reset lines, and read/write memory clients.

Important APIs/types/functions: This header exports 103 DT-visible macros in the `memory` binding namespace. Main API surface: The API includes `TEGRA_SWGROUP_*`, `TEGRA30_MC_RESET_*`, and `TEGRA30_MC_*` client indexes for display, VDE, SATA, HDA, host1x, CPU, and peripheral initiators. First exported macros: `TEGRA_SWGROUP_PTC`, `TEGRA_SWGROUP_DC`, `TEGRA_SWGROUP_DCB`, `TEGRA_SWGROUP_EPP`, `TEGRA_SWGROUP_G2`, `TEGRA_SWGROUP_MPE`, `TEGRA_SWGROUP_VI`, `TEGRA_SWGROUP_AFI`. Last exported macros: `TEGRA30_MC_PPCSAHBSLVW`, `TEGRA30_MC_SATAW`, `TEGRA30_MC_VDEBSEVW`, `TEGRA30_MC_VDEDBGW`, `TEGRA30_MC_VDEMBEW`, `TEGRA30_MC_VDETPMW`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: It integrates with Tegra30 device trees, IOMMU/software-group setup, and memory-controller reset/client programming. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra30-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/arizona.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/arizona.h

Purpose: Cirrus/Wolfson Arizona MFD device-tree constants for GPIO function selection, GPIO config flags, clock selection, DMIC routing, input mode, MICD timing, accessory detect, and GPSW state.

Important APIs/types/functions: This header exports 89 DT-visible macros in the `mfd` binding namespace. Main API surface: `ARIZONA_GP_FN_*` values describe pin alternate functions; `ARIZONA_GPN_*` bits compose GPIO configuration words; convenience macros such as `ARIZONA_GP_INPUT` combine function and direction. First exported macros: `ARIZONA_GP_FN_TXLRCLK`, `ARIZONA_GP_FN_GPIO`, `ARIZONA_GP_FN_IRQ1`, `ARIZONA_GP_FN_IRQ2`, `ARIZONA_GP_FN_OPCLK`, `ARIZONA_GP_FN_FLL1_OUT`, `ARIZONA_GP_FN_FLL2_OUT`, `ARIZONA_GP_FN_PWM1`. Last exported macros: `ARIZONA_ACCDET_MODE_HPM`, `ARIZONA_ACCDET_MODE_ADC`, `ARIZONA_GPSW_OPEN`, `ARIZONA_GPSW_CLOSED`, `ARIZONA_GPSW_CLAMP_ENABLED`, `ARIZONA_GPSW_CLAMP_DISABLED`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The codec/MFD GPIO, clock, jack-detect, and audio routing drivers decode these values from board DT properties. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/arizona.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/as3722.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/as3722.h

Purpose: AMS AS3722 PMIC binding constants for external control pins and interrupt numbers.

Important APIs/types/functions: This header exports 35 DT-visible macros in the `mfd` binding namespace. Main API surface: `AS3722_EXT_CONTROL_PIN_ENABLE*` names board-level external enables, while `AS3722_IRQ_*` maps PMIC interrupt sources including lid, ACOK, on-key, low-battery, SD alarms, temperature, overcurrent, and ADC. First exported macros: `AS3722_EXT_CONTROL_PIN_ENABLE1`, `AS3722_EXT_CONTROL_PIN_ENABLE2`, `AS3722_EXT_CONTROL_PIN_ENABLE3`, `AS3722_IRQ_LID`, `AS3722_IRQ_ACOK`, `AS3722_IRQ_ENABLE1`, `AS3722_IRQ_OCCUR_ALARM_SD0`, `AS3722_IRQ_ONKEY_LONG_PRESS`. Last exported macros: `AS3722_IRQ_TEMP_SD2_SHUTDOWN`, `AS3722_IRQ_TEMP_SD0_ALARM`, `AS3722_IRQ_TEMP_SD1_ALARM`, `AS3722_IRQ_TEMP_SD6_ALARM`, `AS3722_IRQ_OCCUR_ALARM_SD6`, `AS3722_IRQ_ADC`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The AS3722 MFD, regulator, and interrupt-controller drivers use these values as DT-visible ABI indexes. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/as3722.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/at91-usart.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/at91-usart.h

Purpose: AT91 USART binding constants selecting whether a USART block operates as serial UART or SPI.

Important APIs/types/functions: This header exports 2 DT-visible macros in the `mfd` binding namespace. Main API surface: `AT91_USART_MODE_SERIAL` and `AT91_USART_MODE_SPI` are small enum-like constants parsed from DT. First exported macros: `AT91_USART_MODE_SERIAL`, `AT91_USART_MODE_SPI`. Last exported macros: `AT91_USART_MODE_SERIAL`, `AT91_USART_MODE_SPI`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The Atmel USART/MFD glue and serial/SPI child setup use the selected mode during probe. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/at91-usart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/atmel-flexcom.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/atmel-flexcom.h

Purpose: Atmel FLEXCOM binding constants selecting the child controller personality.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `mfd` binding namespace. Main API surface: `ATMEL_FLEXCOM_MODE_USART`, `ATMEL_FLEXCOM_MODE_SPI`, and `ATMEL_FLEXCOM_MODE_TWI` define the legal hardware modes. First exported macros: `ATMEL_FLEXCOM_MODE_USART`, `ATMEL_FLEXCOM_MODE_SPI`, `ATMEL_FLEXCOM_MODE_TWI`. Last exported macros: `ATMEL_FLEXCOM_MODE_USART`, `ATMEL_FLEXCOM_MODE_SPI`, `ATMEL_FLEXCOM_MODE_TWI`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The flexcom MFD driver uses the mode to expose the matching UART, SPI, or I2C/TWI child function. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/atmel-flexcom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/cros_ec.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/cros_ec.h

Purpose: ChromeOS EC MFD binding indexes for EC-backed PWM channels.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `mfd` binding namespace. Main API surface: `CROS_EC_PWM_DT_KB_LIGHT`, `CROS_EC_PWM_DT_DISPLAY_LIGHT`, and `CROS_EC_PWM_DT_COUNT` define the keyboard/display backlight channel ABI. First exported macros: `CROS_EC_PWM_DT_KB_LIGHT`, `CROS_EC_PWM_DT_DISPLAY_LIGHT`, `CROS_EC_PWM_DT_COUNT`. Last exported macros: `CROS_EC_PWM_DT_KB_LIGHT`, `CROS_EC_PWM_DT_DISPLAY_LIGHT`, `CROS_EC_PWM_DT_COUNT`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: DT PWM consumers and the cros-ec PWM provider rely on these indexes matching EC firmware semantics. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/cros_ec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/dbx500-prcmu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/dbx500-prcmu.h

Purpose: ST-Ericsson DBx500 PRCMU clock binding constants.

Important APIs/types/functions: This header exports 63 DT-visible macros in the `mfd` binding namespace. Main API surface: The API enumerates PRCMU clocks such as ARM, ACLK, UART, MSP, I2C, SDMMC, timers, HDMI, DSI, TV, RNG, ULP, and LCD-specific DSI clocks, ending with `PRCMU_NUM_CLKS`. First exported macros: `ARMCLK`, `PRCMU_ACLK`, `PRCMU_SVAMMCSPCLK`, `PRCMU_SDMMCHCLK`, `PRCMU_SIACLK`, `PRCMU_SIAMMDSPCLK`, `PRCMU_SGACLK`, `PRCMU_UARTCLK`. Last exported macros: `PRCMU_DSI0CLK_LCD`, `PRCMU_DSI1CLK_LCD`, `PRCMU_DSI0ESCCLK_LCD`, `PRCMU_DSI1ESCCLK_LCD`, `PRCMU_DSI2ESCCLK_LCD`, `PRCMU_NUM_CLKS`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: These IDs connect DT clock specifiers to the DBx500 PRCMU clock provider and dependent peripheral nodes. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/dbx500-prcmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/max77620.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/max77620.h

Purpose: Maxim MAX77620 PMIC binding constants for top-level interrupts and flexible power sequencer options.

Important APIs/types/functions: This header exports 20 DT-visible macros in the `mfd` binding namespace. Main API surface: `MAX77620_IRQ_*` values identify IRQ domain hwirqs; `MAX77620_FPS_EVENT_SRC_*`, inactive-state, and FPS source macros describe power-sequencer control. First exported macros: `MAX77620_IRQ_TOP_GLBL`, `MAX77620_IRQ_TOP_SD`, `MAX77620_IRQ_TOP_LDO`, `MAX77620_IRQ_TOP_GPIO`, `MAX77620_IRQ_TOP_RTC`, `MAX77620_IRQ_TOP_32K`, `MAX77620_IRQ_TOP_ONOFF`, `MAX77620_IRQ_LBT_MBATLOW`. Last exported macros: `MAX77620_FPS_INACTIVE_STATE_LOW_POWER`, `MAX77620_FPS_SRC_0`, `MAX77620_FPS_SRC_1`, `MAX77620_FPS_SRC_2`, `MAX77620_FPS_SRC_NONE`, `MAX77620_FPS_SRC_DEF`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The MAX77620 MFD, RTC, GPIO, regulator, and power sequencing code share these values with device trees. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/max77620.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/palmas.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/palmas.h

Purpose: TI Palmas PMIC binding constants for external control pins.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `mfd` binding namespace. Main API surface: `PALMAS_EXT_CONTROL_PIN_ENABLE1`, `ENABLE2`, and `NSLEEP` are regulator/control source selectors. First exported macros: `PALMAS_EXT_CONTROL_PIN_ENABLE1`, `PALMAS_EXT_CONTROL_PIN_ENABLE2`, `PALMAS_EXT_CONTROL_PIN_NSLEEP`. Last exported macros: `PALMAS_EXT_CONTROL_PIN_ENABLE1`, `PALMAS_EXT_CONTROL_PIN_ENABLE2`, `PALMAS_EXT_CONTROL_PIN_NSLEEP`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Palmas regulator DT properties use them to bind rails to external enable or sleep control lines. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/palmas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/qcom-rpm.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/qcom-rpm.h

Purpose: Qualcomm RPM resource binding constants plus regulator force-mode constants.

Important APIs/types/functions: This header exports 166 DT-visible macros in the `mfd` binding namespace. Main API surface: `QCOM_RPM_*` IDs map fabric, clock, DDR, switch, and PMIC regulator resources to RPM message resources; `QCOM_RPM_FORCE_MODE_*` selects regulator force behavior. First exported macros: `QCOM_RPM_APPS_FABRIC_ARB`, `QCOM_RPM_APPS_FABRIC_CLK`, `QCOM_RPM_APPS_FABRIC_HALT`, `QCOM_RPM_APPS_FABRIC_IOCTL`, `QCOM_RPM_APPS_FABRIC_MODE`, `QCOM_RPM_APPS_L2_CACHE_CTL`, `QCOM_RPM_CFPB_CLK`, `QCOM_RPM_CXO_BUFFERS`. Last exported macros: `QCOM_RPM_VOLTAGE_CORNER`, `QCOM_RPM_FORCE_MODE_NONE`, `QCOM_RPM_FORCE_MODE_LPM`, `QCOM_RPM_FORCE_MODE_HPM`, `QCOM_RPM_FORCE_MODE_AUTO`, `QCOM_RPM_FORCE_MODE_BYPASS`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: RPM regulator, clock, interconnect, and power-management drivers interpret DT resource specifiers through these stable numeric IDs. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/qcom-rpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/st,stpmic1.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/st,stpmic1.h

Purpose: STPMIC1 PMIC binding constants for interrupt sources and buck regulator mode.

Important APIs/types/functions: This header exports 32 DT-visible macros in the `mfd` binding namespace. Main API surface: `IT_*` interrupt numbers cover power key, wakeup, VBUS, switch output, buck/LDO overcurrent, thermal, VIN-low, and switch input events; `STPMIC1_BUCK_MODE_*` exposes normal/low-power modes. First exported macros: `IT_PONKEY_F`, `IT_PONKEY_R`, `IT_WAKEUP_F`, `IT_WAKEUP_R`, `IT_VBUS_OTG_F`, `IT_VBUS_OTG_R`, `IT_SWOUT_F`, `IT_SWOUT_R`. Last exported macros: `IT_VINLOW_F`, `IT_VINLOW_R`, `IT_SWIN_F`, `IT_SWIN_R`, `STPMIC1_BUCK_MODE_NORMAL`, `STPMIC1_BUCK_MODE_LP`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The STPMIC1 MFD IRQ domain and regulator bindings consume these values. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/st,stpmic1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/st-lpc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/st-lpc.h

Purpose: ST LPC binding constants selecting low-power controller function.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `mfd` binding namespace. Main API surface: `ST_LPC_MODE_RTC`, `ST_LPC_MODE_WDT`, and `ST_LPC_MODE_CLKSRC` define the block personality. First exported macros: `ST_LPC_MODE_RTC`, `ST_LPC_MODE_WDT`, `ST_LPC_MODE_CLKSRC`. Last exported macros: `ST_LPC_MODE_RTC`, `ST_LPC_MODE_WDT`, `ST_LPC_MODE_CLKSRC`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The ST LPC MFD/platform glue uses the mode to instantiate RTC, watchdog, or clocksource behavior. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/st-lpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32f4-rcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32f4-rcc.h

Purpose: STM32F4 RCC binding constants for bus-gated clocks and reset lines.

Important APIs/types/functions: This header exports 84 DT-visible macros in the `mfd` binding namespace. Main API surface: The header lists AHB1/AHB2/AHB3/APB1/APB2 peripheral bit numbers and function-like macros such as `STM32F4_AHB1_RESET(bit)` and `STM32F4_APB2_CLOCK(bit)` that derive reset/clock specifier IDs. First exported macros: `STM32F4_RCC_AHB1_GPIOA`, `STM32F4_RCC_AHB1_GPIOB`, `STM32F4_RCC_AHB1_GPIOC`, `STM32F4_RCC_AHB1_GPIOD`, `STM32F4_RCC_AHB1_GPIOE`, `STM32F4_RCC_AHB1_GPIOF`, `STM32F4_RCC_AHB1_GPIOG`, `STM32F4_RCC_AHB1_GPIOH`. Last exported macros: `STM32F4_RCC_APB2_SPI6`, `STM32F4_RCC_APB2_SAI1`, `STM32F4_RCC_APB2_LTDC`, `STM32F4_RCC_APB2_DSI`, `STM32F4_APB2_RESET(bit)`, `STM32F4_APB2_CLOCK(bit)`. Function-like/helper macros: `STM32F4_AHB1_RESET(bit)`, `STM32F4_AHB1_CLOCK(bit)`, `STM32F4_AHB2_RESET(bit)`, `STM32F4_AHB2_CLOCK(bit)`, `STM32F4_AHB3_RESET(bit)`, `STM32F4_AHB3_CLOCK(bit)`, `STM32F4_APB1_RESET(bit)`, `STM32F4_APB1_CLOCK(bit)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: STM32 clock/reset providers and peripheral DT nodes use the generated IDs to address RCC registers. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32f4-rcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32f7-rcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32f7-rcc.h

Purpose: STM32F7 RCC binding constants for reset and clock specifiers.

Important APIs/types/functions: This header exports 91 DT-visible macros in the `mfd` binding namespace. Main API surface: It mirrors the STM32F4 bus grouping while adding F7-specific peripherals such as LPTIM1, SPDIFRX, SAI2, and CAN3, with `STM32F7_*_RESET/CLOCK(bit)` arithmetic macros. First exported macros: `STM32F7_RCC_AHB1_GPIOA`, `STM32F7_RCC_AHB1_GPIOB`, `STM32F7_RCC_AHB1_GPIOC`, `STM32F7_RCC_AHB1_GPIOD`, `STM32F7_RCC_AHB1_GPIOE`, `STM32F7_RCC_AHB1_GPIOF`, `STM32F7_RCC_AHB1_GPIOG`, `STM32F7_RCC_AHB1_GPIOH`. Last exported macros: `STM32F7_RCC_APB2_SAI1`, `STM32F7_RCC_APB2_SAI2`, `STM32F7_RCC_APB2_LTDC`, `STM32F7_RCC_APB2_DSI`, `STM32F7_APB2_RESET(bit)`, `STM32F7_APB2_CLOCK(bit)`. Function-like/helper macros: `STM32F7_AHB1_RESET(bit)`, `STM32F7_AHB1_CLOCK(bit)`, `STM32F7_AHB2_RESET(bit)`, `STM32F7_AHB2_CLOCK(bit)`, `STM32F7_AHB3_RESET(bit)`, `STM32F7_AHB3_CLOCK(bit)`, `STM32F7_APB1_RESET(bit)`, `STM32F7_APB1_CLOCK(bit)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The DT clock/reset ABI depends on the numeric formula matching the STM32F7 RCC driver tables. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32f7-rcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32h7-rcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32h7-rcc.h

Purpose: STM32H7 RCC binding constants for AHB/APB buses and reset specifiers.

Important APIs/types/functions: This header exports 101 DT-visible macros in the `mfd` binding namespace. Main API surface: The API covers AHB3, AHB1, AHB2, AHB4, APB3, APB1L/H, APB2, and APB4 peripheral bits, with reset macros that encode register offsets into global reset IDs. First exported macros: `STM32H7_RCC_AHB3_MDMA`, `STM32H7_RCC_AHB3_DMA2D`, `STM32H7_RCC_AHB3_JPGDEC`, `STM32H7_RCC_AHB3_FMC`, `STM32H7_RCC_AHB3_QUADSPI`, `STM32H7_RCC_AHB3_SDMMC1`, `STM32H7_RCC_AHB3_CPU`, `STM32H7_AHB3_RESET(bit)`. Last exported macros: `STM32H7_RCC_APB4_LPTIM5`, `STM32H7_RCC_APB4_COMP12`, `STM32H7_RCC_APB4_VREF`, `STM32H7_RCC_APB4_SAI4`, `STM32H7_RCC_APB4_TMPSENS`, `STM32H7_APB4_RESET(bit)`. Function-like/helper macros: `STM32H7_AHB3_RESET(bit)`, `STM32H7_AHB1_RESET(bit)`, `STM32H7_AHB2_RESET(bit)`, `STM32H7_AHB4_RESET(bit)`, `STM32H7_APB3_RESET(bit)`, `STM32H7_APB1L_RESET(bit)`, `STM32H7_APB1H_RESET(bit)`, `STM32H7_APB2_RESET(bit)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Peripheral DT nodes pass these IDs to STM32H7 RCC reset/clock providers. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mfd/stm32h7-rcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mips/lantiq_rcu_gphy.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mips/lantiq_rcu_gphy.h

Purpose: Lantiq RCU GPHY binding constants for Ethernet PHY firmware mode.

Important APIs/types/functions: This header exports 2 DT-visible macros in the `mips` binding namespace. Main API surface: `GPHY_MODE_GE` and `GPHY_MODE_FE` select Gigabit Ethernet or Fast Ethernet behavior. First exported macros: `GPHY_MODE_GE`, `GPHY_MODE_FE`. Last exported macros: `GPHY_MODE_GE`, `GPHY_MODE_FE`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Lantiq SoC DT and RCU/GPHY initialization code use these values when configuring embedded PHY firmware. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mips/lantiq_rcu_gphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mux/mux.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mux/mux.h

Purpose: Generic mux-controller binding constants for idle-state policy.

Important APIs/types/functions: This header exports 2 DT-visible macros in the `mux` binding namespace. Main API surface: `MUX_IDLE_AS_IS` leaves a mux at the last selected state and `MUX_IDLE_DISCONNECT` disconnects it when idle. First exported macros: `MUX_IDLE_AS_IS`, `MUX_IDLE_DISCONNECT`. Last exported macros: `MUX_IDLE_AS_IS`, `MUX_IDLE_DISCONNECT`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Generic mux consumers/providers use these constants in DT `idle-state` style properties. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mux/mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/microchip-lan78xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/net/microchip-lan78xx.h

Purpose: Microchip LAN7800/LAN7850 embedded PHY LED mode binding constants.

Important APIs/types/functions: This header exports 13 DT-visible macros in the `net` binding namespace. Main API surface: `LAN78XX_*` values select link/activity combinations, duplex/collision, autoneg-fault, and forced LED off/on modes. First exported macros: `LAN78XX_LINK_ACTIVITY`, `LAN78XX_LINK_1000_ACTIVITY`, `LAN78XX_LINK_100_ACTIVITY`, `LAN78XX_LINK_10_ACTIVITY`, `LAN78XX_LINK_100_1000_ACTIVITY`, `LAN78XX_LINK_10_1000_ACTIVITY`, `LAN78XX_LINK_10_100_ACTIVITY`, `LAN78XX_DUPLEX_COLLISION`. Last exported macros: `LAN78XX_DUPLEX_COLLISION`, `LAN78XX_COLLISION`, `LAN78XX_ACTIVITY`, `LAN78XX_AUTONEG_FAULT`, `LAN78XX_FORCE_LED_OFF`, `LAN78XX_FORCE_LED_ON`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The LAN78xx Ethernet driver applies these values to PHY LED configuration registers from DT. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/microchip-lan78xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/mscc-phy-vsc8531.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/net/mscc-phy-vsc8531.h

Purpose: Microsemi/Microchip VSC8531/VSC8584 PHY LED mode constants.

Important APIs/types/functions: This header exports 16 DT-visible macros in the `net` binding namespace. Main API surface: `VSC8531_*` and `VSC8584_*` modes cover link speed/activity, fiber/SGMII activity, serial mode, fault, and forced LED states. First exported macros: `VSC8531_LINK_ACTIVITY`, `VSC8531_LINK_1000_ACTIVITY`, `VSC8531_LINK_100_ACTIVITY`, `VSC8531_LINK_10_ACTIVITY`, `VSC8531_LINK_100_1000_ACTIVITY`, `VSC8531_LINK_10_1000_ACTIVITY`, `VSC8531_LINK_10_100_ACTIVITY`, `VSC8584_LINK_100FX_1000X_ACTIVITY`. Last exported macros: `VSC8531_ACTIVITY`, `VSC8584_100FX_1000X_ACTIVITY`, `VSC8531_AUTONEG_FAULT`, `VSC8531_SERIAL_MODE`, `VSC8531_FORCE_LED_OFF`, `VSC8531_FORCE_LED_ON`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: MSCC PHY driver LED setup consumes these DT values. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/mscc-phy-vsc8531.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/pcs-rzn1-miic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/net/pcs-rzn1-miic.h

Purpose: Renesas RZ/N1 MIIC binding constants for media interface connection matrix ports.

Important APIs/types/functions: This header exports 14 DT-visible macros in the `net` binding namespace. Main API surface: `MIIC_*_PORT` IDs name GMAC, RTOS, SERCOS, EtherCAT, switch, and HSR ports. First exported macros: `MIIC_GMAC1_PORT`, `MIIC_GMAC2_PORT`, `MIIC_RTOS_PORT`, `MIIC_SERCOS_PORTA`, `MIIC_SERCOS_PORTB`, `MIIC_ETHERCAT_PORTA`, `MIIC_ETHERCAT_PORTB`, `MIIC_ETHERCAT_PORTC`. Last exported macros: `MIIC_SWITCH_PORTA`, `MIIC_SWITCH_PORTB`, `MIIC_SWITCH_PORTC`, `MIIC_SWITCH_PORTD`, `MIIC_HSR_PORTA`, `MIIC_HSR_PORTB`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The RZ/N1 PCS/MIIC driver uses DT port IDs to program allowed internal Ethernet interconnect combinations. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/pcs-rzn1-miic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/qca-ar803x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/net/qca-ar803x.h

Purpose: Qualcomm Atheros AR803x PHY binding constants for output driver strength.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `net` binding namespace. Main API surface: `AR803X_STRENGTH_FULL`, `HALF`, and `QUARTER` are DT-visible strength selectors. First exported macros: `AR803X_STRENGTH_FULL`, `AR803X_STRENGTH_HALF`, `AR803X_STRENGTH_QUARTER`. Last exported macros: `AR803X_STRENGTH_FULL`, `AR803X_STRENGTH_HALF`, `AR803X_STRENGTH_QUARTER`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The AR803x PHY driver maps the selector to hardware strap/register drive-strength programming. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/qca-ar803x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/renesas,r9a09g077-pcs-miic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/net/renesas,r9a09g077-pcs-miic.h

Purpose: Renesas R9A09G077 PCS MIIC binding constants for Ethernet subsystem media-interface ports.

Important APIs/types/functions: This header exports 9 DT-visible macros in the `net` binding namespace. Main API surface: `ETHSS_*_PORT` constants name GMAC, ESC, and Ethernet switch ports according to the SW_MODE matrix documented in comments. First exported macros: `ETHSS_GMAC0_PORT`, `ETHSS_GMAC1_PORT`, `ETHSS_GMAC2_PORT`, `ETHSS_ESC_PORT0`, `ETHSS_ESC_PORT1`, `ETHSS_ESC_PORT2`, `ETHSS_ETHSW_PORT0`, `ETHSS_ETHSW_PORT1`. Last exported macros: `ETHSS_ESC_PORT0`, `ETHSS_ESC_PORT1`, `ETHSS_ESC_PORT2`, `ETHSS_ETHSW_PORT0`, `ETHSS_ETHSW_PORT1`, `ETHSS_ETHSW_PORT2`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The Renesas PCS/MIIC driver checks DT combinations against the matrix and programs the connection mode. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/renesas,r9a09g077-pcs-miic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/ti-dp83867.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/net/ti-dp83867.h

Purpose: TI DP83867 PHY binding constants for FIFO depth, RGMII internal delay, and clock-output selection.

Important APIs/types/functions: This header exports 34 DT-visible macros in the `net` binding namespace. Main API surface: `DP83867_PHYCR_FIFO_DEPTH_*`, `DP83867_RGMIIDCTL_*`, and `DP83867_CLK_O_SEL_*` expose register field values, including `DP83867_CLK_O_SEL_OFF` as a sentinel. First exported macros: `DP83867_PHYCR_FIFO_DEPTH_3_B_NIB`, `DP83867_PHYCR_FIFO_DEPTH_4_B_NIB`, `DP83867_PHYCR_FIFO_DEPTH_6_B_NIB`, `DP83867_PHYCR_FIFO_DEPTH_8_B_NIB`, `DP83867_RGMIIDCTL_250_PS`, `DP83867_RGMIIDCTL_500_PS`, `DP83867_RGMIIDCTL_750_PS`, `DP83867_RGMIIDCTL_1_NS`. Last exported macros: `DP83867_CLK_O_SEL_CHN_A_TCLK`, `DP83867_CLK_O_SEL_CHN_B_TCLK`, `DP83867_CLK_O_SEL_CHN_C_TCLK`, `DP83867_CLK_O_SEL_CHN_D_TCLK`, `DP83867_CLK_O_SEL_REF_CLK`, `DP83867_CLK_O_SEL_OFF`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The DP83867 PHY driver consumes these from DT to tune RGMII timing and clock outputs. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/ti-dp83867.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/ti-dp83869.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/net/ti-dp83869.h

Purpose: TI DP83869 PHY binding constants for FIFO depth, clock-output selection, and operation mode.

Important APIs/types/functions: This header exports 24 DT-visible macros in the `net` binding namespace. Main API surface: `DP83869_PHYCR_FIFO_DEPTH_*`, `DP83869_CLK_O_SEL_*`, and `DP83869_*` media/bridge mode constants describe DT-tunable PHY behavior. First exported macros: `DP83869_PHYCR_FIFO_DEPTH_3_B_NIB`, `DP83869_PHYCR_FIFO_DEPTH_4_B_NIB`, `DP83869_PHYCR_FIFO_DEPTH_6_B_NIB`, `DP83869_PHYCR_FIFO_DEPTH_8_B_NIB`, `DP83869_CLK_O_SEL_CHN_A_RCLK`, `DP83869_CLK_O_SEL_CHN_B_RCLK`, `DP83869_CLK_O_SEL_CHN_C_RCLK`, `DP83869_CLK_O_SEL_CHN_D_RCLK`. Last exported macros: `DP83869_RGMII_1000_BASE`, `DP83869_RGMII_100_BASE`, `DP83869_RGMII_SGMII_BRIDGE`, `DP83869_1000M_MEDIA_CONVERT`, `DP83869_100M_MEDIA_CONVERT`, `DP83869_SGMII_COPPER_ETHERNET`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The DP83869 PHY driver maps these constants directly to hardware configuration fields. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/net/ti-dp83869.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/nvmem/microchip,sama7g5-otpc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/nvmem/microchip,sama7g5-otpc.h

Purpose: Microchip SAMA7G5 OTPC nvmem binding helper for packet offsets.

Important APIs/types/functions: This header exports 1 DT-visible macros in the `nvmem` binding namespace. Main API surface: `OTP_PKT(id)` converts an OTP packet index into a byte offset by multiplying by the nvmem stride of four. First exported macros: `OTP_PKT(id)`. Last exported macros: `OTP_PKT(id)`. Function-like/helper macros: `OTP_PKT(id)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: DT nvmem cells use this macro to keep offsets aligned with the OTPC provider stride. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/nvmem/microchip,sama7g5-otpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-am654-serdes.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-am654-serdes.h

Purpose: TI AM654 SERDES binding constants for reference-clock inputs.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `phy` binding namespace. Main API surface: `AM654_SERDES_CMU_REFCLK`, `LO_REFCLK`, and `RO_REFCLK` select SERDES reference clock sources. First exported macros: `AM654_SERDES_CMU_REFCLK`, `AM654_SERDES_LO_REFCLK`, `AM654_SERDES_RO_REFCLK`. Last exported macros: `AM654_SERDES_CMU_REFCLK`, `AM654_SERDES_LO_REFCLK`, `AM654_SERDES_RO_REFCLK`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: AM654 SERDES DT nodes use these IDs in clock/source selection properties. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-am654-serdes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-cadence.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-cadence.h

Purpose: Cadence SERDES binding constants for spread-spectrum clocking and Torrent/Sierra reference/PLL selections.

Important APIs/types/functions: This header exports 9 DT-visible macros in the `phy` binding namespace. Main API surface: `CDNS_SERDES_*_SSC`, `CDNS_TORRENT_*REFCLK`, and `CDNS_SIERRA_*` values encode clocking topology choices. First exported macros: `CDNS_SERDES_NO_SSC`, `CDNS_SERDES_EXTERNAL_SSC`, `CDNS_SERDES_INTERNAL_SSC`, `CDNS_TORRENT_REFCLK_DRIVER`, `CDNS_TORRENT_DERIVED_REFCLK`, `CDNS_TORRENT_RECEIVED_REFCLK`, `CDNS_SIERRA_PLL_CMNLC`, `CDNS_SIERRA_PLL_CMNLC1`. Last exported macros: `CDNS_TORRENT_REFCLK_DRIVER`, `CDNS_TORRENT_DERIVED_REFCLK`, `CDNS_TORRENT_RECEIVED_REFCLK`, `CDNS_SIERRA_PLL_CMNLC`, `CDNS_SIERRA_PLL_CMNLC1`, `CDNS_SIERRA_DERIVED_REFCLK`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Cadence Torrent and Sierra PHY drivers decode these DT constants during PLL/refclock setup. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-cadence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-imx8-pcie.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-imx8-pcie.h

Purpose: NXP i.MX8 PCIe PHY binding constants for reference-clock pad mode.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `phy` binding namespace. Main API surface: `IMX8_PCIE_REFCLK_PAD_UNUSED`, `INPUT`, and `OUTPUT` define pad ownership and direction. First exported macros: `IMX8_PCIE_REFCLK_PAD_UNUSED`, `IMX8_PCIE_REFCLK_PAD_INPUT`, `IMX8_PCIE_REFCLK_PAD_OUTPUT`. Last exported macros: `IMX8_PCIE_REFCLK_PAD_UNUSED`, `IMX8_PCIE_REFCLK_PAD_INPUT`, `IMX8_PCIE_REFCLK_PAD_OUTPUT`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The i.MX8 PCIe PHY/controller setup uses the selected pad mode to configure board clock routing. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-imx8-pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-lan966x-serdes.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-lan966x-serdes.h

Purpose: Microchip LAN966x SERDES binding helpers that allocate global lane IDs across CU, SERDES6G, and RGMII groups.

Important APIs/types/functions: This header exports 7 DT-visible macros in the `phy` binding namespace. Main API surface: Function-like macros `CU(x)`, `SERDES6G(x)`, and `RGMII(x)` build contiguous IDs; `*_MAX` and `SERDES_MAX` define group bounds. First exported macros: `CU(x)`, `CU_MAX`, `SERDES6G(x)`, `SERDES6G_MAX`, `RGMII(x)`, `RGMII_MAX`, `SERDES_MAX`. Last exported macros: `CU_MAX`, `SERDES6G(x)`, `SERDES6G_MAX`, `RGMII(x)`, `RGMII_MAX`, `SERDES_MAX`. Function-like/helper macros: `CU(x)`, `SERDES6G(x)`, `RGMII(x)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: LAN966x PHY consumers use these IDs as PHY specifier arguments. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-lan966x-serdes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-lantiq-vrx200-pcie.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-lantiq-vrx200-pcie.h

Purpose: Lantiq VRX200 PCIe PHY binding constants for reference clock frequency and SSC mode.

Important APIs/types/functions: This header exports 6 DT-visible macros in the `phy` binding namespace. Main API surface: `LANTIQ_PCIE_PHY_MODE_*` enumerates 25 MHz, 36 MHz, and 100 MHz, each with optional spread-spectrum clocking. First exported macros: `LANTIQ_PCIE_PHY_MODE_25MHZ`, `LANTIQ_PCIE_PHY_MODE_25MHZ_SSC`, `LANTIQ_PCIE_PHY_MODE_36MHZ`, `LANTIQ_PCIE_PHY_MODE_36MHZ_SSC`, `LANTIQ_PCIE_PHY_MODE_100MHZ`, `LANTIQ_PCIE_PHY_MODE_100MHZ_SSC`. Last exported macros: `LANTIQ_PCIE_PHY_MODE_25MHZ`, `LANTIQ_PCIE_PHY_MODE_25MHZ_SSC`, `LANTIQ_PCIE_PHY_MODE_36MHZ`, `LANTIQ_PCIE_PHY_MODE_36MHZ_SSC`, `LANTIQ_PCIE_PHY_MODE_100MHZ`, `LANTIQ_PCIE_PHY_MODE_100MHZ_SSC`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The VRX200 PCIe PHY driver uses the selected mode to program clock-generation hardware. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-lantiq-vrx200-pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-ocelot-serdes.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-ocelot-serdes.h

Purpose: Microsemi Ocelot SERDES binding helpers for 1G and 6G lane IDs.

Important APIs/types/functions: This header exports 5 DT-visible macros in the `phy` binding namespace. Main API surface: `SERDES1G(x)` and `SERDES6G(x)` produce contiguous lane IDs with `SERDES_MAX` as the total count. First exported macros: `SERDES1G(x)`, `SERDES1G_MAX`, `SERDES6G(x)`, `SERDES6G_MAX`, `SERDES_MAX`. Last exported macros: `SERDES1G(x)`, `SERDES1G_MAX`, `SERDES6G(x)`, `SERDES6G_MAX`, `SERDES_MAX`. Function-like/helper macros: `SERDES1G(x)`, `SERDES6G(x)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Ocelot switch/PHY DT consumers use these IDs when requesting a SERDES lane. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-ocelot-serdes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-pistachio-usb.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-pistachio-usb.h

Purpose: Imagination Pistachio USB PHY binding constants for reference-clock source.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `phy` binding namespace. Main API surface: `REFCLK_XO_CRYSTAL`, `REFCLK_X0_EXT_CLK`, and `REFCLK_CLK_CORE` enumerate hardware clock inputs. First exported macros: `REFCLK_XO_CRYSTAL`, `REFCLK_X0_EXT_CLK`, `REFCLK_CLK_CORE`. Last exported macros: `REFCLK_XO_CRYSTAL`, `REFCLK_X0_EXT_CLK`, `REFCLK_CLK_CORE`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The Pistachio USB PHY driver maps the selected source to PHY clock control registers. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-pistachio-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qmp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qmp.h

Purpose: Qualcomm QMP PHY binding constants for USB4/USB3/DisplayPort clocks and PHY lanes plus PCIe clock indexes.

Important APIs/types/functions: This header exports 7 DT-visible macros in the `phy` binding namespace. Main API surface: `QMP_USB43DP_*` constants distinguish USB3 pipe, DP link/VCO clocks, USB3 PHY, and DP PHY; `QMP_PCIE_*` indexes expose PCIe pipe/aux clocks. First exported macros: `QMP_USB43DP_USB3_PIPE_CLK`, `QMP_USB43DP_DP_LINK_CLK`, `QMP_USB43DP_DP_VCO_DIV_CLK`, `QMP_USB43DP_USB3_PHY`, `QMP_USB43DP_DP_PHY`, `QMP_PCIE_PIPE_CLK`, `QMP_PCIE_PHY_AUX_CLK`. Last exported macros: `QMP_USB43DP_DP_LINK_CLK`, `QMP_USB43DP_DP_VCO_DIV_CLK`, `QMP_USB43DP_USB3_PHY`, `QMP_USB43DP_DP_PHY`, `QMP_PCIE_PIPE_CLK`, `QMP_PCIE_PHY_AUX_CLK`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: QMP PHY providers and DT consumers use these IDs in multi-output clock/PHY specifiers. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qusb2.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qusb2.h

Purpose: Qualcomm QUSB2 PHY binding constants for USB high-speed transmit trim, preemphasis, and preemphasis width.

Important APIs/types/functions: This header exports 22 DT-visible macros in the `phy` binding namespace. Main API surface: `QUSB2_V2_HSTX_TRIM_*`, `QUSB2_V2_PREEMPHASIS_*`, and width constants are register field values. First exported macros: `QUSB2_V2_HSTX_TRIM_24_0_MA`, `QUSB2_V2_HSTX_TRIM_23_4_MA`, `QUSB2_V2_HSTX_TRIM_22_8_MA`, `QUSB2_V2_HSTX_TRIM_22_2_MA`, `QUSB2_V2_HSTX_TRIM_21_6_MA`, `QUSB2_V2_HSTX_TRIM_21_0_MA`, `QUSB2_V2_HSTX_TRIM_20_4_MA`, `QUSB2_V2_HSTX_TRIM_19_8_MA`. Last exported macros: `QUSB2_V2_PREEMPHASIS_NONE`, `QUSB2_V2_PREEMPHASIS_5_PERCENT`, `QUSB2_V2_PREEMPHASIS_10_PERCENT`, `QUSB2_V2_PREEMPHASIS_15_PERCENT`, `QUSB2_V2_PREEMPHASIS_WIDTH_FULL_BIT`, `QUSB2_V2_PREEMPHASIS_WIDTH_HALF_BIT`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: QUSB2 PHY DT tuning properties feed these values into analog USB PHY calibration. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-qcom-qusb2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-ti.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-ti.h

Purpose: TI WIZ/SERDES binding constants for output clock indexes.

Important APIs/types/functions: This header exports 4 DT-visible macros in the `phy` binding namespace. Main API surface: `TI_WIZ_PLL0_REFCLK`, `PLL1_REFCLK`, `REFCLK_DIG`, and `PHY_EN_REFCLK` identify mux and miscellaneous clocks. First exported macros: `TI_WIZ_PLL0_REFCLK`, `TI_WIZ_PLL1_REFCLK`, `TI_WIZ_REFCLK_DIG`, `TI_WIZ_PHY_EN_REFCLK`. Last exported macros: `TI_WIZ_PLL0_REFCLK`, `TI_WIZ_PLL1_REFCLK`, `TI_WIZ_REFCLK_DIG`, `TI_WIZ_PHY_EN_REFCLK`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: TI SERDES/WIZ clock providers use these indexes for DT clock-output cells. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy-ti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy.h

Purpose: Generic PHY framework binding constants for PHY type and polarity.

Important APIs/types/functions: This header exports 17 DT-visible macros in the `phy` binding namespace. Main API surface: `PHY_TYPE_*` covers SATA, PCIe, USB2/3, UFS, DisplayPort, XPCS, SGMII/QSGMII/USXGMII, D-PHY/C-PHY, and XAUI; `PHY_POL_*` describes lane polarity. First exported macros: `PHY_NONE`, `PHY_TYPE_SATA`, `PHY_TYPE_PCIE`, `PHY_TYPE_USB2`, `PHY_TYPE_USB3`, `PHY_TYPE_UFS`, `PHY_TYPE_DP`, `PHY_TYPE_XPCS`. Last exported macros: `PHY_TYPE_CPHY`, `PHY_TYPE_USXGMII`, `PHY_TYPE_XAUI`, `PHY_POL_NORMAL`, `PHY_POL_INVERT`, `PHY_POL_AUTO`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Generic PHY providers and consumers share these values in DT properties and specifier arguments. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/phy/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am33xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am33xx.h

Purpose: TI AM33xx pinctrl binding constants for pad configuration and SoC pin offsets.

Important APIs/types/functions: This header exports 136 DT-visible macros in the `pinctrl` binding namespace. Main API surface: It includes OMAP pinctrl defaults, overrides pull/input bits for AM33xx, defines `PIN_*` convenience configs, and enumerates `AM335X_PIN_*` offsets from GPMC through USB drive-VBUS pins. First exported macros: `PULL_DISABLE`, `INPUT_EN`, `SLEWCTRL_SLOW`, `SLEWCTRL_FAST`, `PIN_OUTPUT`, `PIN_OUTPUT_PULLUP`, `PIN_OUTPUT_PULLDOWN`, `PIN_INPUT`. Last exported macros: `AM335X_PIN_RTC_PWRONRSTN`, `AM335X_PIN_PMIC_POWER_EN`, `AM335X_PIN_EXT_WAKEUP`, `AM335X_PIN_USB0_DRVVBUS`, `AM335X_PIN_USB1_DRVVBUS`, `AM335X_PIN_OFFSET_MAX`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: `<dt-bindings/pinctrl/omap.h>` It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: AM335x board DTS files use these offsets and config bits in pinctrl-single pad entries. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am33xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am43xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am43xx.h

Purpose: TI AM43xx pinctrl binding constants for mux modes, active/off-state pad bits, and IOPAD address helper.

Important APIs/types/functions: This header exports 36 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MUX_MODE*`, `PULL_*`, `INPUT_EN`, `DS0_*`, `PIN_*`, and `AM4372_IOPAD(pa, val)` compose pad register values. First exported macros: `MUX_MODE0`, `MUX_MODE1`, `MUX_MODE2`, `MUX_MODE3`, `MUX_MODE4`, `MUX_MODE5`, `MUX_MODE6`, `MUX_MODE7`. Last exported macros: `PIN_OUTPUT_PULLUP`, `PIN_OUTPUT_PULLDOWN`, `PIN_INPUT`, `PIN_INPUT_PULLUP`, `PIN_INPUT_PULLDOWN`, `AM4372_IOPAD(pa, val)`. Function-like/helper macros: `AM4372_IOPAD(pa, val)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: AM437x DTS pinctrl-single nodes use the helper to translate physical pad addresses to register offsets. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/am43xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/amlogic,pinctrl.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/amlogic,pinctrl.h

Purpose: Amlogic pinctrl binding constants for bank IDs and packed pinmux encoding.

Important APIs/types/functions: This header exports 32 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `AMLOGIC_GPIO_*` names banks from A through analog/test groups; `AML_PINMUX(bank, offset, mode)` packs bank, pin offset, and function mode into one DT cell. First exported macros: `AMLOGIC_GPIO_A`, `AMLOGIC_GPIO_B`, `AMLOGIC_GPIO_C`, `AMLOGIC_GPIO_D`, `AMLOGIC_GPIO_E`, `AMLOGIC_GPIO_F`, `AMLOGIC_GPIO_G`, `AMLOGIC_GPIO_H`. Last exported macros: `AMLOGIC_GPIO_DV`, `AMLOGIC_GPIO_AO`, `AMLOGIC_GPIO_CC`, `AMLOGIC_GPIO_TEST_N`, `AMLOGIC_GPIO_ANALOG`, `AML_PINMUX(bank, offset, mode)`. Function-like/helper macros: `AML_PINMUX(bank, offset, mode)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Amlogic pinctrl drivers unpack these values to select bank-local pin functions. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/amlogic,pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/apple.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/apple.h

Purpose: Apple pinctrl binding helpers for packing and unpacking pin/function selector cells.

Important APIs/types/functions: This header exports 3 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `APPLE_PINMUX(pin, func)` packs function in the high bits; `APPLE_PIN(pinmux)` and `APPLE_FUNC(pinmux)` recover each component. First exported macros: `APPLE_PINMUX(pin, func)`, `APPLE_PIN(pinmux)`, `APPLE_FUNC(pinmux)`. Last exported macros: `APPLE_PINMUX(pin, func)`, `APPLE_PIN(pinmux)`, `APPLE_FUNC(pinmux)`. Function-like/helper macros: `APPLE_PINMUX(pin, func)`, `APPLE_PIN(pinmux)`, `APPLE_FUNC(pinmux)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Apple SoC pinctrl DT entries use the packed cell as a compact selector ABI. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/apple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/at91.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/at91.h

Purpose: Atmel AT91 pinctrl binding constants for pull, drive, debounce, output, peripheral mux, and drive strength.

Important APIs/types/functions: This header exports 31 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `AT91_PINCTRL_*` bit fields include computed value helpers for output and debounce; `AT91_PERIPH_*` selects GPIO/A/B/C/D; `ATMEL_PIO_DRVSTR_*` selects drive strength. First exported macros: `AT91_PINCTRL_NONE`, `AT91_PINCTRL_PULL_UP`, `AT91_PINCTRL_MULTI_DRIVE`, `AT91_PINCTRL_DEGLITCH`, `AT91_PINCTRL_PULL_DOWN`, `AT91_PINCTRL_DIS_SCHMIT`, `AT91_PINCTRL_OUTPUT`, `AT91_PINCTRL_OUTPUT_VAL(x)`. Last exported macros: `AT91_PERIPH_B`, `AT91_PERIPH_C`, `AT91_PERIPH_D`, `ATMEL_PIO_DRVSTR_LO`, `ATMEL_PIO_DRVSTR_ME`, `ATMEL_PIO_DRVSTR_HI`. Function-like/helper macros: `AT91_PINCTRL_OUTPUT_VAL(x)`, `AT91_PINCTRL_DEBOUNCE_VAL(x)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: AT91 pinctrl nodes compose these constants into pin configuration words. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/at91.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/bcm2835.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/bcm2835.h

Purpose: Broadcom BCM2835 pinctrl binding constants for GPIO function select and pull state.

Important APIs/types/functions: This header exports 11 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `BCM2835_FSEL_*` enumerates input, output, and ALT0-ALT5 mux values; `BCM2835_PUD_*` enumerates pull off/down/up. First exported macros: `BCM2835_FSEL_GPIO_IN`, `BCM2835_FSEL_GPIO_OUT`, `BCM2835_FSEL_ALT5`, `BCM2835_FSEL_ALT4`, `BCM2835_FSEL_ALT0`, `BCM2835_FSEL_ALT1`, `BCM2835_FSEL_ALT2`, `BCM2835_FSEL_ALT3`. Last exported macros: `BCM2835_FSEL_ALT1`, `BCM2835_FSEL_ALT2`, `BCM2835_FSEL_ALT3`, `BCM2835_PUD_OFF`, `BCM2835_PUD_DOWN`, `BCM2835_PUD_UP`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Raspberry Pi/BCM2835 pinctrl DT data maps these values to GPFSEL and pull control programming. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/bcm2835.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/brcm,pinctrl-stingray.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/brcm,pinctrl-stingray.h

Purpose: Broadcom Stingray pinctrl binding constants for mux mode and pad electrical control.

Important APIs/types/functions: This header exports 23 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MODE_*` selects Nitro/NAND/PNOR/GPIO functions, while `PAD_*` and `*_MASK` constants encode slew, drive strength, pulls, input disable, and hysteresis. First exported macros: `MODE_NITRO`, `MODE_NAND`, `MODE_PNOR`, `MODE_GPIO`, `PAD_SLEW_RATE_ENA`, `PAD_SLEW_RATE_ENA_MASK`, `PAD_DRIVE_STRENGTH_2_MA`, `PAD_DRIVE_STRENGTH_4_MA`. Last exported macros: `PAD_PULL_DOWN_ENA`, `PAD_PULL_DOWN_ENA_MASK`, `PAD_INPUT_PATH_DIS`, `PAD_INPUT_PATH_DIS_MASK`, `PAD_HYSTERESIS_ENA`, `PAD_HYSTERESIS_ENA_MASK`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The Stingray pinctrl driver decodes DT pad words using these masks and field values. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/brcm,pinctrl-stingray.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/dm814x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/dm814x.h

Purpose: TI DM814x pinctrl binding constants overriding OMAP pad config bits.

Important APIs/types/functions: This header exports 9 DT-visible macros in the `pinctrl` binding namespace. Main API surface: After including `omap.h`, the header undefines and redefines `INPUT_EN`, `PULL_UP`, `PULL_DISABLE`, and `PIN_*` convenience macros with DM814x bit positions. First exported macros: `INPUT_EN`, `PULL_UP`, `PULL_DISABLE`, `PIN_OUTPUT`, `PIN_OUTPUT_PULLUP`, `PIN_OUTPUT_PULLDOWN`, `PIN_INPUT`, `PIN_INPUT_PULLUP`. Last exported macros: `PIN_OUTPUT`, `PIN_OUTPUT_PULLUP`, `PIN_OUTPUT_PULLDOWN`, `PIN_INPUT`, `PIN_INPUT_PULLUP`, `PIN_INPUT_PULLDOWN`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: `<dt-bindings/pinctrl/omap.h>` It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: DM814x DTS pinctrl-single entries depend on these SoC-specific bit assignments. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/dm814x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/dra.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/dra.h

Purpose: TI DRA7xx pinctrl binding constants for mux modes, pad config bits, IOPAD address conversion, and delay programming.

Important APIs/types/functions: This header exports 50 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MUX_MODE0` through `MUX_MODE15`, `PIN_*`, `DRA7XX_CORE_IOPAD(pa, val)`, `A_DELAY_PS(val)`, and `G_DELAY_PS(val)` compose mux and delay values. First exported macros: `MUX_MODE0`, `MUX_MODE1`, `MUX_MODE2`, `MUX_MODE3`, `MUX_MODE4`, `MUX_MODE5`, `MUX_MODE6`, `MUX_MODE7`. Last exported macros: `PIN_INPUT_SLEW`, `PIN_INPUT_PULLUP`, `PIN_INPUT_PULLDOWN`, `DRA7XX_CORE_IOPAD(pa, val)`, `A_DELAY_PS(val)`, `G_DELAY_PS(val)`. Function-like/helper macros: `DRA7XX_CORE_IOPAD(pa, val)`, `A_DELAY_PS(val)`, `G_DELAY_PS(val)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: DRA7xx board DTS files use these macros for core pad registers and IO delay cells. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/dra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/hisi.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/hisi.h

Purpose: HiSilicon pinctrl binding constants for mux modes, pull options, Schmitt trigger, slew, and multiple drive-strength encodings.

Important APIs/types/functions: This header exports 47 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MUX_M*`, `PULL_*`, `STRENGTH*`, `DRIVE*`, and `SLEW_RATE_*` represent the register field vocabulary shared by HiSilicon pin controllers. First exported macros: `MUX_M0`, `MUX_M1`, `MUX_M2`, `MUX_M3`, `MUX_M4`, `MUX_M5`, `MUX_M6`, `MUX_M7`. Last exported macros: `DRIVE7_06MA`, `DRIVE7_08MA`, `DRIVE7_10MA`, `DRIVE7_12MA`, `DRIVE7_14MA`, `DRIVE7_16MA`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: HiSilicon DTS pin configuration entries pass these field values to the pinctrl driver. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/hisi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/k210-fpioa.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/k210-fpioa.h

Purpose: Kendryte K210 FPIOA binding constants for assigning SoC functions to package pins and selecting IO power domain.

Important APIs/types/functions: This header exports 261 DT-visible macros in the `pinctrl` binding namespace. Main API surface: The header enumerates `K210_PCF_*` functions for JTAG, SPI, I2S, DVP, UART, timer, clock, GPIO, debug, and other signals; `K210_FPIOA(pin, func)` packs pin and function; `K210_PC_POWER_*` selects 3.3 V or 1.8 V. First exported macros: `PINCTRL_K210_FPIOA_H`, `K210_PCF_MASK`, `K210_PCF_JTAG_TCLK`, `K210_PCF_JTAG_TDI`, `K210_PCF_JTAG_TMS`, `K210_PCF_JTAG_TDO`, `K210_PCF_SPI0_D0`, `K210_PCF_SPI0_D1`. Last exported macros: `K210_PCF_DEBUG29`, `K210_PCF_DEBUG30`, `K210_PCF_DEBUG31`, `K210_FPIOA(pin, func)`, `K210_PC_POWER_3V3`, `K210_PC_POWER_1V8`. Function-like/helper macros: `K210_FPIOA(pin, func)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: K210 pinctrl/FPIOA DT uses these constants to route flexible IO matrix functions. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/k210-fpioa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/keystone.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/keystone.h

Purpose: TI Keystone pinctrl binding constants for mux modes, buffer class, pulls, and address translation.

Important APIs/types/functions: This header exports 15 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MUX_MODE0` through `MUX_MODE5`, `BUFFER_CLASS_*`, `PIN_PULL*`, `KEYSTONE_IOPAD_OFFSET(pa, offset)`, and `K2G_CORE_IOPAD(pa)` define pad selector cells. First exported macros: `MUX_MODE0`, `MUX_MODE1`, `MUX_MODE2`, `MUX_MODE3`, `MUX_MODE4`, `MUX_MODE5`, `BUFFER_CLASS_B`, `BUFFER_CLASS_C`. Last exported macros: `BUFFER_CLASS_E`, `PULL_DISABLE`, `PIN_PULLUP`, `PIN_PULLDOWN`, `KEYSTONE_IOPAD_OFFSET(pa, offset)`, `K2G_CORE_IOPAD(pa)`. Function-like/helper macros: `KEYSTONE_IOPAD_OFFSET(pa, offset)`, `K2G_CORE_IOPAD(pa)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: Keystone/K2G DTS pinctrl-single entries use these to form register offsets and config values. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/keystone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/lochnagar.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/lochnagar.h

Purpose: Cirrus Logic Lochnagar audio evaluation board pinctrl binding constants.

Important APIs/types/functions: This header exports 116 DT-visible macros in the `pinctrl` binding namespace. Main API surface: The API enumerates Lochnagar1 and Lochnagar2 logical pins, including codec/DSP resets, CIF modes, FPGA GPIOs, SPDIF/I2C/SPI/GF GPIOs, clocks, and DSP GPIOs, ending in per-device `*_NUM_GPIOS` bounds. First exported macros: `LOCHNAGAR1_PIN_CDC_RESET`, `LOCHNAGAR1_PIN_DSP_RESET`, `LOCHNAGAR1_PIN_CDC_CIF1MODE`, `LOCHNAGAR1_PIN_NUM_GPIOS`, `LOCHNAGAR2_PIN_CDC_RESET`, `LOCHNAGAR2_PIN_DSP_RESET`, `LOCHNAGAR2_PIN_CDC_CIF1MODE`, `LOCHNAGAR2_PIN_CDC_LDOENA`. Last exported macros: `LOCHNAGAR2_PIN_PSIA1_MCLK`, `LOCHNAGAR2_PIN_PSIA2_MCLK`, `LOCHNAGAR2_PIN_GF_GPIO1`, `LOCHNAGAR2_PIN_GF_GPIO5`, `LOCHNAGAR2_PIN_DSP_GPIO20`, `LOCHNAGAR2_PIN_NUM_GPIOS`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: The Lochnagar MFD/pinctrl driver uses these IDs to expose board-level pin and GPIO routing. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/lochnagar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mediatek,mt8188-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mediatek,mt8188-pinfunc.h

Purpose: MediaTek MT8188 pin-function binding constants for every GPIO alternate function.

Important APIs/types/functions: This header exports 1091 DT-visible macros in the `pinctrl` binding namespace. Main API surface: It includes `mt65xx.h` and defines more than one thousand `PINMUX_GPIO<n>__FUNC_*` entries built with `MTK_PIN_NO(n) | function`, covering GPIO, SPI, UART, I2S, DMIC, debug monitor, SPMI, LVTS, JTAG, MSDC, and many SoC-specific signals. First exported macros: `PINMUX_GPIO0__FUNC_B_GPIO0`, `PINMUX_GPIO0__FUNC_B0_TP_GPIO0_AO`, `PINMUX_GPIO0__FUNC_O_SPIM5_CSB`, `PINMUX_GPIO0__FUNC_O_UTXD1`, `PINMUX_GPIO0__FUNC_O_DMIC3_CLK`, `PINMUX_GPIO0__FUNC_B0_I2SIN_MCK`, `PINMUX_GPIO0__FUNC_O_I2SO2_MCK`, `PINMUX_GPIO0__FUNC_B0_DBG_MON_A0`. Last exported macros: `PINMUX_GPIO174__FUNC_B1_MSDC2_DAT3`, `PINMUX_GPIO174__FUNC_I0_LVTS_SDI`, `PINMUX_GPIO175__FUNC_B_GPIO175`, `PINMUX_GPIO175__FUNC_B0_SPMI_M_SCL`, `PINMUX_GPIO176__FUNC_B_GPIO176`, `PINMUX_GPIO176__FUNC_B0_SPMI_M_SDA`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: `"mt65xx.h"` It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: MT8188 DTS pinmux entries use these constants as the ABI between board descriptions and the MediaTek pinctrl driver. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mediatek,mt8188-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt65xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt65xx.h

Purpose: Shared MediaTek pinctrl binding helpers and electrical configuration constants.

Important APIs/types/functions: This header exports 27 DT-visible macros in the `pinctrl` binding namespace. Main API surface: `MTK_PIN_NO(x)`, `MTK_GET_PIN_NO(x)`, and `MTK_GET_PIN_FUNC(x)` pack/unpack pinmux cells; `MTK_PUPD_SET_*`, `MTK_PULL_SET_RSEL_*`, and `MTK_DRIVE_*mA` expose pull/drive encodings. First exported macros: `MTK_PIN_NO(x)`, `MTK_GET_PIN_NO(x)`, `MTK_GET_PIN_FUNC(x)`, `MTK_PUPD_SET_R1R0_00`, `MTK_PUPD_SET_R1R0_01`, `MTK_PUPD_SET_R1R0_10`, `MTK_PUPD_SET_R1R0_11`, `MTK_PULL_SET_RSEL_000`. Last exported macros: `MTK_DRIVE_14mA`, `MTK_DRIVE_16mA`, `MTK_DRIVE_20mA`, `MTK_DRIVE_24mA`, `MTK_DRIVE_28mA`, `MTK_DRIVE_32mA`. Function-like/helper macros: `MTK_PIN_NO(x)`, `MTK_GET_PIN_NO(x)`, `MTK_GET_PIN_FUNC(x)`

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: No local include dependency. It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: MediaTek SoC-specific pinfunc headers include this file and depend on its packed-cell layout. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt65xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6779-pinfunc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6779-pinfunc.h

Purpose: MediaTek MT6779 pin-function binding constants for GPIO alternate functions.

Important APIs/types/functions: This header exports 1019 DT-visible macros in the `pinctrl` binding namespace. Main API surface: It includes the shared `mt65xx.h` helpers and defines `PINMUX_GPIO<n>__FUNC_*` values for GPIO0 through GPIO209, covering SPI, I2S/TDM/PCM, I2C, UART, touch panel, antenna/PTA, display, camera, debug, and clock monitor functions. First exported macros: `PINMUX_GPIO0__FUNC_GPIO0`, `PINMUX_GPIO0__FUNC_SPI6_MI`, `PINMUX_GPIO0__FUNC_I2S5_LRCK`, `PINMUX_GPIO0__FUNC_TDM_LRCK_2ND`, `PINMUX_GPIO0__FUNC_PCM1_SYNC`, `PINMUX_GPIO0__FUNC_SCL_6306`, `PINMUX_GPIO0__FUNC_TP_GPIO0_AO`, `PINMUX_GPIO0__FUNC_PTA_RXD`. Last exported macros: `PINMUX_GPIO204__FUNC_GPIO204`, `PINMUX_GPIO205__FUNC_GPIO205`, `PINMUX_GPIO206__FUNC_GPIO206`, `PINMUX_GPIO207__FUNC_GPIO207`, `PINMUX_GPIO208__FUNC_GPIO208`, `PINMUX_GPIO209__FUNC_GPIO209`. Function-like/helper macros: No function-like macros; all exported constants are direct numeric or bit-field values.

Control flow: There is no runtime C control flow. The only execution-like behavior is C preprocessor expansion: device trees include the header, symbolic macro names become integer cells or bit fields, and kernel drivers later parse those cells during probe or configuration. Include guards prevent duplicate definitions, and any helper macros perform arithmetic or bit packing at preprocessing time.

State and persistence behavior: The file stores no runtime state and performs no persistence. Its numeric values are persistent ABI between DTS sources, compiled DTBs, and kernel drivers, so changing an existing value changes the meaning of shipped device trees.

Dependencies: `<dt-bindings/pinctrl/mt65xx.h>` It otherwise depends only on the C preprocessor and the Linux devicetree binding include path.

Integration points: MT6779 DTS pinmux properties use these constants to select SoC pin alternate functions. The source-tree integration point is `include/dt-bindings`, which is shared by DTS files, binding examples, and drivers that need symbolic constants.

Risks: The major risk is ABI drift: renumbering macros, changing packed-bit layouts, or reusing a value with different hardware meaning can silently misconfigure clocks, resets, memory clients, PHYs, pinmuxes, interrupts, or regulators. For function-like macros, arithmetic offset formulas must match the provider driver's register layout. For large pin-function tables, duplicate or wrong alternate-function numbers can compile cleanly but route pins to the wrong signal.

Test signals: Useful validation is mostly integration-oriented: run `dtbs_check` for schemas that reference this header, compile representative DTBs, and boot or probe hardware/emulators enough to verify the relevant provider driver decodes the expected numeric IDs. Static checks should confirm include guards, macro count/names, no accidental renumbering against upstream, and successful preprocessing of DTS files using the first and last macros listed above.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/mt6779-pinfunc.h -->
