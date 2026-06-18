# subset-b-005826 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8550-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8550-rpmh.h

## Purpose
This binding header assigns stable integer node IDs for the Qualcomm SM8550 RPMh interconnect provider. It gives DTS authors symbolic names for A1NOC, A2NOC, QUP core, CNOC, GEM_NOC, MC/LLCC, MNOC, CDSP, PCIe ANOC, and SNOC master/slave endpoints.

## Important APIs, types, and functions
The public API is the macro namespace: `MASTER_*` and `SLAVE_*` IDs such as `MASTER_QSPI_0`, `MASTER_UFS_MEM`, `SLAVE_A1NOC_SNOC`, `MASTER_GPU_TCU`, `SLAVE_LLCC`, `MASTER_CAMNOC_HF`, and `SLAVE_EBI1`. There are no C types or functions.

## Control flow
DTS files include the header, then use these constants in interconnect specifier cells. At build time the C preprocessor replaces names with integers; at runtime the Qualcomm ICC driver resolves those IDs against the SM8550 provider tables for bandwidth voting through RPMh.

## State and persistence
The header has no runtime state. Its numbers are ABI-like device-tree data and must remain stable for compiled DTBs that reference them.

## Dependencies and integration points
It integrates with Qualcomm interconnect bindings, the SM8550 interconnect driver data, RPMh bandwidth voting, and DT nodes for display, camera, video, storage, USB, PCIe, GPU, modem, compute DSP, LPASS, and debug clients.

## Risks and test signals
Risks include duplicate IDs inside one provider domain, DTS using an endpoint that the driver table does not expose, and accidental renumbering that breaks existing DTBs. Test signals are `dtbs_check`, successful preprocessing of SM8550 DTS includes, driver probe without unknown-node warnings, and bandwidth votes observed for UFS, USB, display, camera, and PCIe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8550-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8650-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8650-rpmh.h

## Purpose
This header defines SM8650 RPMh interconnect node IDs. It covers the SoC's A1NOC/A2NOC, QUP core, CNOC config, GEM_NOC, MC/LLCC, multimedia, CDSP, PCIe ANOC, and SNOC domains for device-tree bandwidth paths.

## Important APIs, types, and functions
The exported surface is macro constants such as `MASTER_QUP_3`, `SLAVE_I3C_IBI0_CFG`, `MASTER_UBWC_P_TCU`, `MASTER_UBWC_P`, `MASTER_GIC`, `MASTER_APSS_NOC`, and common storage/display/camera/video/PCIe endpoints. There are no callable functions.

## Control flow
Device-tree sources include the header and pass these numeric IDs to `interconnects` properties. The compiled DTB feeds those IDs to the SM8650 Qualcomm ICC provider, which maps them to NOC nodes and issues RPMh aggregate bandwidth requests.

## State and persistence
No state is stored here. The macro values are persistent firmware-facing ABI values once included in DTBs.

## Dependencies and integration points
The header must match SM8650 ICC driver node arrays and YAML binding expectations. It is consumed by DTS nodes for QUP/I3C/I2C, UFS, SDCC, USB, PCIe, GPU, display, camera, video, CDSP, modem, and system fabric clients.

## Risks and test signals
Risks include SM8550/SM8750 copy-paste drift, mismatched `MASTER_QUP_*` and `SLAVE_QUP_*` numbering, and missing new SM8650 endpoints in provider data. Test signals are `dtbs_check`, `make dt_binding_check` for Qualcomm ICC bindings, successful driver probe, and runtime bandwidth voting for high-traffic multimedia and storage paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8650-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8750-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8750-rpmh.h

## Purpose
This header provides SM8750 RPMh interconnect node identifiers for device tree. It represents newer SM8750 fabrics including SOCCP, EVA/video, UBWC, PCIe, multimedia, compute, memory, and system NOC endpoints.

## Important APIs, types, and functions
Only macros are exported. Important families include A1NOC/A2NOC IDs, `MASTER_SOCCP_AGGR_NOC`, `SLAVE_SOCCP`, CNOC config slaves, `MASTER_UBWC_P`, `SLAVE_UBWC_P`, `MASTER_VIDEO_EVA`, `MASTER_VIDEO_MVP`, `MASTER_CAMNOC_*`, `MASTER_PCIE_0`, and SNOC/GEM_NOC endpoints.

## Control flow
The macros are expanded during DTS preprocessing and become numeric cells in interconnect paths. The SM8750 interconnect provider later interprets them while building ICC paths and sending RPMh votes.

## State and persistence
The file has no state or persistence logic. Its constants become persistent DT ABI once DTBs are distributed.

## Dependencies and integration points
It depends on the matching Qualcomm SM8750 ICC provider implementation and device-tree schemas. Integration points include camera, EVA/video, display, PCIe, USB/storage, GPU, modem, SPSS, and system configuration nodes.

## Risks and test signals
Risks include introducing a new endpoint macro without a provider table entry, using an SM8650 ID on SM8750 DTS, and renumbering existing IDs. Test signals include DTS preprocessing, schema validation, ICC provider probe, and functional bandwidth votes for camera/video/display stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sm8750-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,x1e80100-rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,x1e80100-rpmh.h

## Purpose
This binding header defines RPMh interconnect IDs for Qualcomm X1E80100. It covers laptop-class fabrics including multiple PCIe and USB/USB4 aggregators, QUP, CNOC, GEM_NOC, MC/LLCC, multimedia, CDSP, LPASS, and SNOC paths.

## Important APIs, types, and functions
The API is the macro set. Notable endpoints include `MASTER_DDR_PERF_MODE`, `SLAVE_DDR_PERF_MODE`, `MASTER_PCIE_TCU`, `MASTER_GIC1`, `MASTER_GIC2`, `MASTER_PCIE_NORTH`, `MASTER_PCIE_SOUTH`, `MASTER_AGGRE_USB_NORTH`, `MASTER_AGGRE_USB_SOUTH`, `MASTER_USB4_0..2`, and `SLAVE_AGGRE_USB_*`.

## Control flow
DTS files include this header and emit numeric IDs in interconnect specifiers. During boot, the X1E80100 ICC provider maps those IDs to driver-side nodes for RPMh bandwidth voting and aggregate path management.

## State and persistence
No runtime state exists in this header. Values embedded into DTBs are stable platform ABI.

## Dependencies and integration points
It integrates with Qualcomm ICC/RPMh, device-tree schemas, and platform devices for PCIe, USB2/USB3/USB4, UFS, SDCC, QUP, display, camera, video, GPU, CDSP, LPASS, and memory controllers.

## Risks and test signals
Risks include PCIe north/south or USB north/south ID confusion, drift from provider table ordering, and endpoint omissions for high-speed laptop I/O. Test signals are `dtbs_check`, X1E80100 ICC provider probe, PCIe and USB4 throughput tests with nonzero ICC votes, and display/camera bandwidth validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,x1e80100-rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/amlogic,meson-g12a-gpio-intc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/amlogic,meson-g12a-gpio-intc.h

## Purpose
This header assigns GPIO interrupt IDs for the Amlogic Meson G12A GPIO interrupt controller binding. It maps GPIO banks to a contiguous IRQID space from GPIOAO through GPIOE.

## Important APIs, types, and functions
The exported API is `IRQID_*` macros: `IRQID_GPIOAO_0..11`, `IRQID_GPIOZ_0..15`, `IRQID_GPIOH_0..8`, `IRQID_BOOT_0..15`, `IRQID_GPIOC_0..7`, `IRQID_GPIOA_0..15`, `IRQID_GPIOX_0..19`, and `IRQID_GPIOE_0..2`.

## Control flow
DTS interrupt specifiers use these IDs instead of raw integers. The preprocessed DTB carries the numbers to the Meson GPIO interrupt controller driver, which maps the bank/line ID to hardware interrupt routing.

## State and persistence
There is no in-kernel state in this file. The IDs are stable DT binding values and persist in compiled board DTBs.

## Dependencies and integration points
It integrates with Amlogic pinctrl/GPIO interrupt-controller nodes and any peripheral DTS node that sources interrupts from Meson GPIO lines. It depends on the driver's hardware bank ordering matching this macro ordering.

## Risks and test signals
Risks include bank-order mismatch, off-by-one numbering around bank boundaries, and using G12A IDs on incompatible Meson variants. Test signals include GPIO interrupt smoke tests for each bank, `dtbs_check`, and edge/level interrupt validation through the Meson GPIO IRQ driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/amlogic,meson-g12a-gpio-intc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/apple-aic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/apple-aic.h

## Purpose
This header defines Apple AIC interrupt specifier constants for IRQ/FIQ selection and built-in per-CPU sources such as timers and PMUs.

## Important APIs, types, and functions
It includes the generic `irq.h` flags and exports `AIC_IRQ`, `AIC_FIQ`, timer IDs `AIC_TMR_HV_PHYS`, `AIC_TMR_HV_VIRT`, `AIC_TMR_GUEST_PHYS`, `AIC_TMR_GUEST_VIRT`, and PMU IDs `AIC_CPU_PMU_E` and `AIC_CPU_PMU_P`.

## Control flow
Apple SoC DTS files use these constants in interrupt specifiers. They are preprocessed into integers and consumed by the Apple AIC irqchip driver when it creates Linux IRQ mappings.

## State and persistence
The header is stateless. Values become stable DT ABI in compiled Apple platform DTBs.

## Dependencies and integration points
It depends on generic interrupt trigger flags from `irq.h` and integrates with Apple Silicon AIC/AIC2 interrupt-controller nodes, ARM timer nodes, and PMU descriptions.

## Risks and test signals
Risks include confusing IRQ and FIQ cells, mapping PMU E/P cores incorrectly, or applying AIC constants to a different controller binding. Test signals include DTS schema checks, timer interrupts, PMU overflow interrupts, and boot logs from the Apple AIC driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/apple-aic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/arm-gic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/arm-gic.h

## Purpose
This common header defines ARM GIC interrupt specifier constants for SPI/PPI and extended SPI/PPI interrupt types, plus CPU target mask helpers.

## Important APIs, types, and functions
The API includes `GIC_SPI`, `GIC_PPI`, `GIC_ESPI`, `GIC_EPPI`, `GIC_CPU_MASK_RAW(x)`, and `GIC_CPU_MASK_SIMPLE(num)`. It also imports generic trigger flags from `irq.h`.

## Control flow
DTS interrupt specifiers reference these macros in the interrupt-controller cell format. The preprocessed cells are interpreted by GIC irqchip drivers while mapping interrupts.

## State and persistence
There is no state. The constants are stable DT binding ABI shared by many ARM platforms.

## Dependencies and integration points
It integrates with ARM GICv2/GICv3/GICv4 bindings, platform DTS interrupt descriptions, and the generic IRQ trigger flag header. CPU masks are relevant for PPI affinity encodings in older GIC bindings.

## Risks and test signals
Risks include wrong cell type selection, invalid CPU masks, and mixing extended interrupt types with controllers that do not support them. Test signals include `dtbs_check`, interrupt-controller probe, timer/PPI delivery, SPI device interrupts, and affinity handling on SMP systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/arm-gic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/aspeed-scu-ic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/aspeed-scu-ic.h

## Purpose
This binding header names interrupt sources for Aspeed SCU interrupt controllers across AST2500, AST2600, and AST2700 generations.

## Important APIs, types, and functions
It exports numeric source IDs for VGA cursor/scratch changes and SoC-specific PCIe PERST/RCRST, LPC reset, and MSI events, such as `ASPEED_AST2500_SCU_IC_PCIE_RESET_LO_TO_HI`, `ASPEED_AST2600_SCU_IC0_PCIE_PERST_*`, and `ASPEED_AST2700_SCU_IC[0-3]_*`.

## Control flow
Board DTS files use these macros in interrupt specifiers for SCU interrupt-controller child events. The driver maps the source ID to a status bit or event line for the selected Aspeed generation.

## State and persistence
The file has no state. Values embedded in DTBs are hardware binding IDs.

## Dependencies and integration points
It integrates with Aspeed SCU syscon/interrupt-controller drivers and platform devices interested in VGA, PCIe reset, LPC reset, or MSI state changes.

## Risks and test signals
Risks include generation-specific ID reuse, inverted rising/falling reset semantics, and using an AST2700 IC bank macro with the wrong SCU interrupt-controller instance. Test signals include DTS validation, reset-edge interrupt tests, and driver logs for each SCU IC bank.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/aspeed-scu-ic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq-st.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq-st.h

## Purpose
This header defines STMicroelectronics syscfg interrupt selector constants and inversion flags for ST irqchip bindings.

## Important APIs, types, and functions
It exports `ST_IRQ_SYSCFG_EXT_0..2`, `ST_IRQ_SYSCFG_CTI_0..1`, `ST_IRQ_SYSCFG_PMU_0..1`, `ST_IRQ_SYSCFG_pl310_L2`, `ST_IRQ_SYSCFG_DISABLED`, and inversion flags `ST_IRQ_SYSCFG_EXT_1_INV`, `ST_IRQ_SYSCFG_EXT_2_INV`, `ST_IRQ_SYSCFG_EXT_3_INV`.

## Control flow
DTS nodes use the constants in syscfg interrupt routing properties. After preprocessing, the ST irqchip/syscfg code interprets the selector and optional inversion bits while configuring hardware routing.

## State and persistence
The header has no runtime state. Numeric selectors persist in compiled DTBs.

## Dependencies and integration points
It integrates with ST interrupt controller/syscfg drivers, external interrupt lines, CTI, PMU, and PL310 L2 interrupt routes.

## Risks and test signals
Risks include treating `ST_IRQ_SYSCFG_DISABLED` as a valid selector, confusing `EXT_3_INV` naming with the available `EXT_0..2` selectors, and incorrect polarity inversion. Test signals include DT validation, external interrupt edge tests, PMU/CTI interrupt delivery, and syscfg register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq-st.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq.h

## Purpose
This common header defines generic interrupt trigger and polarity flag constants used by many device-tree interrupt bindings.

## Important APIs, types, and functions
It exports `IRQ_TYPE_NONE`, `IRQ_TYPE_EDGE_RISING`, `IRQ_TYPE_EDGE_FALLING`, `IRQ_TYPE_EDGE_BOTH`, `IRQ_TYPE_LEVEL_HIGH`, and `IRQ_TYPE_LEVEL_LOW`. There are no functions or structures.

## Control flow
Other binding headers and DTS files include this header, then place the numeric flags in interrupt specifier cells. IRQ domain code later translates the values into Linux IRQ trigger type flags.

## State and persistence
The file has no state. Its values are fundamental DT ABI and must remain unchanged.

## Dependencies and integration points
It is a dependency for controller-specific headers such as ARM GIC, Apple AIC, and MIPS GIC. It integrates with irqdomain translation, interrupt-controller schemas, and every DTS interrupt specifier using standard flags.

## Risks and test signals
Risks include combining level and edge values incorrectly, assuming `IRQ_TYPE_NONE` selects a default edge, or changing constants that are globally ABI-stable. Test signals include `dtbs_check`, interrupt trigger configuration in `/proc/interrupts`/debugfs, and hardware tests for rising, falling, both-edge, high-level, and low-level interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irqc-rzg2l.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irqc-rzg2l.h

## Purpose
This binding header defines Renesas RZ/G2L family IRQC source IDs for NMI and IRQ0-IRQ7 lines.

## Important APIs, types, and functions
It exports `RZG2L_NMI` and `RZG2L_IRQ0` through `RZG2L_IRQ7`, with comments documenting that NMI maps to SPI0 and IRQ0-7 map to SPI1-8.

## Control flow
DTS files reference these constants in IRQC interrupt specifiers. The compiled numbers are translated by the RZ/G2L irqchip driver into GIC SPI routing and trigger configuration.

## State and persistence
No runtime state exists in the header. The mapping is persistent DT ABI.

## Dependencies and integration points
It integrates with Renesas RZ/G2L IRQC controller nodes, GIC parent interrupt routing, and board-level GPIO/peripheral interrupt declarations.

## Risks and test signals
Risks include off-by-one SPI mapping, using `RZG2L_NMI` for maskable IRQ semantics, and applying this map to an incompatible Renesas family. Test signals include DTS validation, NMI routing tests, IRQ0-7 edge/level tests, and irqdomain mapping traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/irqc-rzg2l.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mips-gic.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mips-gic.h

## Purpose
This small header defines MIPS GIC interrupt specifier type constants for shared and local interrupt sources.

## Important APIs, types, and functions
It includes generic `irq.h` flags and exports `GIC_SHARED` and `GIC_LOCAL`. There are no functions or data structures.

## Control flow
MIPS DTS interrupt specifiers use these constants to indicate whether an interrupt is a shared GIC source or a CPU-local source. The MIPS GIC irqchip consumes the resulting numeric cells during IRQ domain translation.

## State and persistence
The header is stateless. Its values persist in platform DTBs.

## Dependencies and integration points
It integrates with MIPS GIC interrupt-controller bindings, generic trigger flags, timer/per-CPU local interrupts, and shared device interrupts.

## Risks and test signals
Risks include mixing local and shared specifier formats and using generic ARM GIC constants by mistake. Test signals include DTS preprocessing, MIPS GIC probe, local timer interrupt delivery, and shared peripheral interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mips-gic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mvebu-icu.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mvebu-icu.h

## Purpose
This header defines Marvell MVEBU ICU interrupt group IDs for device-tree interrupt specifiers.

## Important APIs, types, and functions
It exports four group constants: `ICU_GRP_NSR`, `ICU_GRP_SR`, `ICU_GRP_SEI`, and `ICU_GRP_REI`.

## Control flow
DTS nodes use these values in the first interrupt specifier cell. The MVEBU ICU driver decodes the group and maps it to the correct interrupt parent/routing class.

## State and persistence
No state is present. The constants are stable DT binding values.

## Dependencies and integration points
It integrates with Marvell ICU irqchip code, parent interrupt controllers, and Armada/MVEBU platform device interrupt declarations.

## Risks and test signals
Risks include choosing the wrong security or error-interrupt group and mismatching device-tree group IDs with firmware routing. Test signals include `dtbs_check`, ICU probe, interrupt delivery for NSR/SR events, and platform-specific error interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/interrupt-controller/mvebu-icu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/common.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/common.h

## Purpose
This common LED binding header defines standardized LED color IDs, functions, trigger type values, and boost mode values for device-tree LED nodes.

## Important APIs, types, and functions
It exports trigger type macros `LEDS_TRIG_TYPE_EDGE` and `LEDS_TRIG_TYPE_LEVEL`, boost mode macros `LEDS_BOOST_OFF`, `LEDS_BOOST_ADAPTIVE`, `LEDS_BOOST_FIXED`, color IDs from `LED_COLOR_ID_WHITE` through `LED_COLOR_ID_LIME`, and function strings such as `LED_FUNCTION_STATUS`, `LED_FUNCTION_POWER`, `LED_FUNCTION_KBD_BACKLIGHT`, `LED_FUNCTION_WLAN`, and `LED_FUNCTION_WPS`.

## Control flow
DTS LED nodes include the header and use the constants in properties such as `color`, `function`, trigger-related properties, or driver-specific boost settings. LED class drivers and schema validation consume the resulting values.

## State and persistence
No runtime state exists. The string and numeric constants form shared DT ABI and influence stable LED names exposed to userspace.

## Dependencies and integration points
It integrates with LED class device naming, multicolor LED bindings, flash/torch/backlight drivers, netdev/activity triggers, and YAML schemas that restrict color/function values.

## Risks and test signals
Risks include creating nonstandard LED names, using obsolete function strings instead of standardized ones, assigning colors beyond `LED_COLOR_ID_MAX`, and changing values visible to userspace naming policy. Test signals include `dtbs_check`, LED class device names under `/sys/class/leds`, trigger behavior, multicolor LED registration, and board LED smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-lp55xx.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-lp55xx.h

## Purpose
This header defines charge-pump mode constants for TI/National LP55xx LED controller device-tree bindings.

## Important APIs, types, and functions
It exports `LP55XX_CP_OFF`, `LP55XX_CP_BYPASS`, `LP55XX_CP_BOOST`, and `LP55XX_CP_AUTO`.

## Control flow
LP55xx DTS nodes use these values in charge-pump configuration properties. The driver reads the numeric property and programs the chip's charge-pump behavior.

## State and persistence
The header has no state. The chosen mode persists as board configuration in the DTB and then as runtime chip register state after probe.

## Dependencies and integration points
It integrates with LP5521/LP5523/LP5562-style LED controller drivers and their device-tree schemas.

## Risks and test signals
Risks include selecting a mode unsupported by a specific chip or board power design, causing brightness/current issues. Test signals include `dtbs_check`, LP55xx probe, LED brightness tests, and power/current validation under boost and bypass modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-lp55xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-netxbig.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-netxbig.h

## Purpose
This header defines mode constants for LaCie/Seagate Netxbig LED device-tree bindings.

## Important APIs, types, and functions
It exports `NETXBIG_LED_OFF`, `NETXBIG_LED_ON`, `NETXBIG_LED_SATA`, `NETXBIG_LED_TIMER1`, and `NETXBIG_LED_TIMER2`.

## Control flow
Board DTS files use the constants to describe LED mode wiring or default behavior. The Netxbig LED driver converts the numeric mode into hardware control behavior.

## State and persistence
There is no header state. Mode choices persist in DTB data and become runtime LED state after driver probe.

## Dependencies and integration points
It integrates with the Netxbig LED driver, SATA activity indication, timer blink logic, and board-specific LED GPIO/register wiring.

## Risks and test signals
Risks include mismatching SATA/timer modes with physical LED wiring and using board-specific values outside the driver contract. Test signals include DTS validation, LED on/off tests, SATA activity indication, and timer blink behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-netxbig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-ns2.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-ns2.h

## Purpose
This header defines simple LED mode constants for Network Space v2 LED bindings.

## Important APIs, types, and functions
It exports `NS_V2_LED_OFF`, `NS_V2_LED_ON`, and `NS_V2_LED_SATA`.

## Control flow
DTS nodes use these constants in board LED mode properties. The NS2 LED driver maps the numeric value to off, steady on, or SATA activity behavior.

## State and persistence
The file has no state. DTB values persist as board configuration and driver-programmed LED behavior.

## Dependencies and integration points
It integrates with NS2 board LED support and storage activity indication.

## Risks and test signals
Risks include assigning SATA mode to a LED not wired for activity and confusing this board-specific binding with generic LED function strings. Test signals include LED mode smoke tests and SATA activity indication during I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-ns2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca9532.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca9532.h

## Purpose
This header defines child output type constants for PCA9532 LED/GPIO bindings.

## Important APIs, types, and functions
It exports `PCA9532_TYPE_NONE`, `PCA9532_TYPE_LED`, `PCA9532_TYPE_N2100_BEEP`, `PCA9532_TYPE_GPIO`, and `PCA9532_LED_TIMER2`.

## Control flow
DTS child nodes use these constants to classify each PCA9532 output. The driver uses the value to decide whether to register an LED, expose a GPIO, ignore a pin, or apply board-specific beep/timer behavior.

## State and persistence
No state lives in the header. Values persist in DTB configuration and affect runtime device registration.

## Dependencies and integration points
It integrates with PCA9532 LED controller support, GPIO registration, LED timer hardware, and legacy N2100 board beep behavior.

## Risks and test signals
Risks include classifying an output incorrectly, which can expose the wrong kernel interface or drive the wrong pin. Test signals include DTS validation, LED registration, GPIO line tests, beep output tests where applicable, and timer2 blink behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca9532.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca955x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca955x.h

## Purpose
This header defines output type constants for PCA955x LED/GPIO expander bindings.

## Important APIs, types, and functions
It exports `PCA955X_TYPE_NONE`, `PCA955X_TYPE_LED`, and `PCA955X_TYPE_GPIO`.

## Control flow
DTS child nodes reference these constants to describe output usage. The PCA955x driver uses the numeric type to register LEDs, GPIOs, or leave outputs unused.

## State and persistence
The header is stateless. The board's selected types persist in the DTB and determine runtime registration.

## Dependencies and integration points
It integrates with PCA955x I2C LED controller support, LED class registration, GPIO subsystem exposure, and board schemas.

## Risks and test signals
Risks include wrong LED/GPIO classification, creating userspace ABI differences, or driving pins unexpectedly. Test signals include `dtbs_check`, I2C probe, LED class entries, GPIO line toggling, and output electrical validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/leds-pca955x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/rt4831-backlight.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/leds/rt4831-backlight.h

## Purpose
This header defines Richtek RT4831 backlight binding constants for over-voltage protection level and LED channel enable masks.

## Important APIs, types, and functions
It exports OVP level values `RT4831_BLOVPLVL_17V`, `21V`, `25V`, and `29V`, plus channel bits `RT4831_BLED_CH1EN` through `RT4831_BLED_CH4EN` and aggregate `RT4831_BLED_ALLCHEN`.

## Control flow
Backlight DTS nodes use these constants in RT4831 properties. The RT4831 driver reads the resulting values and programs OVP and enabled current-sink channels.

## State and persistence
No state exists in the header. The DTB supplies persistent board policy, and the driver writes runtime chip registers during probe/resume.

## Dependencies and integration points
It integrates with RT4831 MFD/backlight support, LED string wiring, regulator/backlight power sequencing, and schema validation.

## Risks and test signals
Risks include selecting an unsafe OVP level for the panel string, enabling unwired channels, and assuming `ALLCHEN` is valid for every board. Test signals include DTS validation, backlight probe, brightness ramp tests, OVP fault testing, and channel-current measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/leds/rt4831-backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/mediatek,mt8188-gce.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/mediatek,mt8188-gce.h

## Purpose
This large binding header defines MediaTek MT8188 GCE/CMDQ constants: thread priorities, register subsystem IDs, hardware event IDs, sync tokens, handshake events, timeout tokens, and resource tokens used by command queue clients.

## Important APIs, types, and functions
The exported API is macro-only. Key groups are `CMDQ_THR_PRIO_*`, `SUBSYS_*`, event IDs for IMG/CAM/VPP/VDO/VDEC/VENC/WPE/DISP blocks (`CMDQ_EVENT_*`), synchronization tokens (`CMDQ_SYNC_TOKEN_*`), resource tokens such as `CMDQ_SYNC_RESOURCE_WROT0`, and output pin events.

## Control flow
MT8188 DTS and MediaTek multimedia drivers include the header to describe mailbox channels and command queue waits/signals. During preprocessing, symbolic events become numeric IDs that the GCE mailbox/CMDQ driver uses in command packets and event waits.

## State and persistence
The header has no state. Event and token numbers are hardware-facing ABI values embedded in DTBs and driver code; the actual state lives in GCE event registers, sync token state, and command queue threads.

## Dependencies and integration points
It integrates with the MediaTek CMDQ mailbox driver, display pipeline, image processing, camera, video decode/encode, VPP/VDO, WPE, MML, secure thread handling, and any client that waits for frame-done, start-of-frame, underrun, mutex, or handshake events.

## Risks and test signals
Risks include duplicate or wrong event IDs, sparse ranges hiding omissions, misuse of sync tokens as hardware events, and driver/DTS drift across MT8188 revisions. Test signals include DTS preprocessing, CMDQ mailbox probe, command queue wait/signal tests for display and camera, multimedia pipeline stress, timeout-token behavior, and event tracing during frame-done and underrun scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/mediatek,mt8188-gce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/qcom-ipcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/qcom-ipcc.h

## Purpose
This header defines Qualcomm IPCC mailbox client IDs and MPROC signal IDs for device-tree mailbox specifiers.

## Important APIs, types, and functions
It exports signal IDs `IPCC_MPROC_SIGNAL_GLINK_QMP`, `TZ`, `SMP2P`, and `PING`, plus client IDs including `IPCC_CLIENT_AOP`, `TZ`, `MPSS`, `LPASS`, `SLPI`, `CDSP`, `APSS`, `GPU`, `CAM`, `PCIE0..2`, `SPSS`, `NSP1`, `TME`, `WPSS`, and `GPDSP0/1`.

## Control flow
Qualcomm DTS mailbox users encode remote client and signal IDs with these macros. The IPCC mailbox driver translates the DT cells into register offsets/bits for interrupting or receiving notifications from remote processors.

## State and persistence
The header is stateless. Mailbox routing state is hardware/runtime state; IDs in DTBs are stable firmware-facing configuration.

## Dependencies and integration points
It integrates with Qualcomm IPCC, GLINK/QMP, TrustZone, SMP2P, remoteproc subsystems, AOP/CDSP/SLPI/MPSS/LPASS clients, and PCIe or multimedia remote agents.

## Risks and test signals
Risks include client ID gaps, using a client unsupported on a specific SoC, and mixing signal IDs across protocols. Test signals include `dtbs_check`, IPCC mailbox probe, remoteproc boot, SMP2P/GLINK communication, and interrupt delivery between APSS and remote clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/qcom-ipcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/tegra186-hsp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/tegra186-hsp.h

## Purpose
This header defines NVIDIA Tegra186 HSP mailbox specifier constants for doorbells, shared mailboxes, shared semaphores, arbitrated semaphores, master IDs, and shared-mailbox direction encoding.

## Important APIs, types, and functions
It exports mailbox type constants `TEGRA_HSP_MBOX_TYPE_DB`, `SM`, `SS`, `AS`, the `TEGRA_HSP_MBOX_TYPE_SM_128BIT` flag, doorbell master bits `TEGRA_HSP_DB_MASTER_CCPLEX` and `BPMP`, masks/flags for shared mailbox direction, and helper macros `TEGRA_HSP_SM_RX(x)` and `TEGRA_HSP_SM_TX(x)`.

## Control flow
DTS mailbox specifiers use these constants to identify mailbox kind, master, index, and direction. The Tegra HSP mailbox driver decodes the cells and binds clients such as BPMP IPC to the correct HSP hardware primitive.

## State and persistence
No state is held in the header. Runtime state lives in HSP registers and mailbox framework channels; DTB values persist board/SoC wiring.

## Dependencies and integration points
It integrates with Tegra HSP mailbox drivers, BPMP communication, CCPLEX firmware channels, and shared mailbox/semaphore hardware.

## Risks and test signals
Risks include wrong TX/RX flag use on unidirectional mailboxes, incorrect doorbell master bit, and masking indexes beyond `TEGRA_HSP_SM_MASK`. Test signals include DTS validation, BPMP IPC operation, mailbox loopback or ping tests, and driver decode traces for each mailbox type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/mailbox/tegra186-hsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/omap3-isp.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/media/omap3-isp.h

## Purpose
This header defines OMAP3 ISP PHY type constants for camera/media device-tree bindings.

## Important APIs, types, and functions
It exports `OMAP3ISP_PHY_TYPE_COMPLEX_IO` and `OMAP3ISP_PHY_TYPE_CSIPHY`.

## Control flow
OMAP3 camera endpoint or ISP nodes use these macros to describe the physical receiver type. The OMAP3 ISP driver reads the numeric property and configures the correct PHY path.

## State and persistence
The header has no state. The selected PHY type persists in board DTBs and affects runtime ISP configuration.

## Dependencies and integration points
It integrates with OMAP3 ISP media driver, V4L2 async endpoint parsing, CSI/CCP2 receiver configuration, and camera sensor graph bindings.

## Risks and test signals
Risks include selecting the wrong PHY type for the board wiring, leading to no camera stream or bad lane setup. Test signals include `dtbs_check`, media graph enumeration, sensor stream-on, and captured frame validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/omap3-isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/tda1997x.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/media/tda1997x.h

## Purpose
This header defines NXP TDA1997x HDMI receiver media binding constants for video port pin groups, audio DAI format, channel layout, and audio clock selection.

## Important APIs, types, and functions
It exports VP36 and VP24 register/group indexes, pin-group option bits `TDA1997X_VP_OUT_EN`, `TDA1997X_VP_HIZ`, `TDA1997X_VP_SWP`, color-lane group macros such as `TDA1997X_R_CR_CBCR_3_0` and `TDA1997X_G_Y_11_8`, audio formats `TDA1997X_I2S16`, `I2S32`, `SPDIF`, `OBA`, `DST`, HBR variants, layouts `TDA1997X_LAYOUT0/1`, and clocks `TDA1997X_ACLK_16FS..512FS`.

## Control flow
DTS files use these constants to configure the receiver's parallel video output and audio bus. The TDA1997x driver consumes the numeric values while programming port control and audio interface registers.

## State and persistence
The file is stateless. Pin/audio choices persist in DTB board configuration and become runtime register settings after probe.

## Dependencies and integration points
It integrates with the TDA1997x V4L2 subdevice driver, media endpoint graph, audio DAI configuration, and board-specific parallel bus wiring.

## Risks and test signals
Risks include a visible macro typo: swapped group macros use `TDA1997X_VP_SWAP`, while the option bit defined above is `TDA1997X_VP_SWP`; preprocessing any `_S` macro should verify whether this is intentional or a compile-time break. Other risks are wrong pin group order, Hi-Z misconfiguration, and audio clock/layout mismatch. Test signals include header self-preprocessing, `dtbs_check`, driver probe, HDMI video capture, pin-swap validation, and audio capture for each configured DAI format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/tda1997x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/tvp5150.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/media/tvp5150.h

## Purpose
This header defines TI TVP5150 analog video decoder input and output mode constants for device-tree bindings.

## Important APIs, types, and functions
It exports input selectors `TVP5150_COMPOSITE0`, `TVP5150_COMPOSITE1`, and `TVP5150_SVIDEO`, plus output modes `TVP5150_NORMAL` and `TVP5150_BLACK_SCREEN`.

## Control flow
Board DTS files use these constants to select hardware input routing and output behavior. The TVP5150 driver reads the values and programs decoder input/output registers.

## State and persistence
The header is stateless. Input/output choices persist in the DTB and become runtime decoder state when the driver configures the chip.

## Dependencies and integration points
It integrates with the TVP5150 V4L2 subdevice driver, media graph endpoints, analog composite/S-video board wiring, and capture pipeline configuration.

## Risks and test signals
Risks include selecting the wrong physical connector, forcing black-screen output unexpectedly, and mismatched media graph links. Test signals include `dtbs_check`, media graph enumeration, input switching tests, and captured analog video validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/tvp5150.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/video-interfaces.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/media/video-interfaces.h

## Purpose
This common media binding header defines video bus type constants, CSI-2 C-PHY line order encodings, and parallel pixel-clock sample edge constants.

## Important APIs, types, and functions
It exports `MEDIA_BUS_TYPE_CSI2_CPHY`, `CSI1`, `CCP2`, `CSI2_DPHY`, `PARALLEL`, `BT656`, C-PHY line order constants `MEDIA_BUS_CSI2_CPHY_LINE_ORDER_ABC` through `CBA`, and pixel clock sample constants `MEDIA_PCLK_SAMPLE_FALLING_EDGE`, `RISING_EDGE`, and `DUAL_EDGE`.

## Control flow
Media endpoint DTS nodes include the header and use these constants in bus-type, lane-order, and pclk properties. V4L2 fwnode parsers and media drivers convert the numeric values into endpoint bus configuration.

## State and persistence
The header has no state. Values persist in DTBs and control runtime media bus setup.

## Dependencies and integration points
It integrates with generic video-interface schemas, V4L2 fwnode endpoint parsing, CSI-2 C-PHY/D-PHY receivers, parallel/BT.656 capture drivers, and sensor/display bridge endpoints.

## Risks and test signals
Risks include mismatched bus type between sensor and receiver, wrong C-PHY trio order, and incorrect pixel sampling edge causing unstable images. Test signals include `dtbs_check`, media graph validation, endpoint parser logs, sensor stream-on, and captured frame integrity under the configured bus mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/video-interfaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/xilinx-vip.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/media/xilinx-vip.h

## Purpose
This header defines Xilinx Video IP AXI4-Stream video format codes for device-tree media bindings.

## Important APIs, types, and functions
It exports `XVIP_VF_*` format constants from `XVIP_VF_YUV_422` through `XVIP_VF_CUSTOM4`, including RGB/RGBA, YUV/YUVA/YUVD variants, mono sensor, and custom formats. `XVIP_VF_RBG` is spelled as present in the binding.

## Control flow
Xilinx VIP DTS nodes use these constants to describe stream formats. The Xilinx video pipeline drivers parse the numeric value and configure format negotiation or hardware register programming.

## State and persistence
No state exists in the header. Format selections persist in DTBs and affect runtime media pipeline configuration.

## Dependencies and integration points
It integrates with Xilinx V4L2/video IP drivers, AXI4-Stream video components, media graph endpoint configuration, and format negotiation.

## Risks and test signals
Risks include format-code mismatch with Xilinx IP documentation, the `RBG` spelling causing user confusion, and selecting custom formats without driver support. Test signals include `dtbs_check`, media pipeline enumeration, format negotiation, stream-on tests, and pixel format validation on captured or generated frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/media/xilinx-vip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt6893-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt6893-memory-port.h

## Purpose
This header defines MT6893 multimedia IOMMU/M4U port IDs by larb for display, MDP, video decode/encode, image, camera, CCU, and IPE/FDVT blocks. Comments document 16GB IOVA partitioning across display, vcodec, camera/MDP, and CCU regions.

## Important APIs, types, and functions
The exported macros are `M4U_PORT_L*_*` constants for larbs 0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 16, 17, 18, 19, and 20. They use a MediaTek M4U ID helper and include domain suffixes such as `_MDP` and `_DISP` for some duplicated functional ports.

## Control flow
DTS IOMMU specifiers reference these macros for device ports. The MediaTek IOMMU/SMI driver decodes the larb and port portions to attach the correct hardware master and enforce the intended DMA address region.

## State and persistence
No state exists here. The IOMMU attachment and fault state live in runtime drivers and hardware; macro values persist in DTBs.

## Dependencies and integration points
It includes `mtk-memory-port.h` and integrates with MediaTek SMI larb, M4U/IOMMU, display, MDP, VDEC/VENC, camera, CCU, and IPE drivers.

## Risks and test signals
This file uses `MTK_M4U_DOM_ID`, while the included shared header in this tree defines `MTK_M4U_ID`; unless another include defines the DOM helper, DTS preprocessing will fail. Other risks include wrong larb-to-domain partitioning, null larb references, and duplicated port names mapped to the wrong 4GB window. Test signals include direct header preprocessing, `dtbs_check`, IOMMU attach logs, SMI larb probe, and DMA/fault tests for display, codec, camera, and CCU clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt6893-memory-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8188-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8188-memory-port.h

## Purpose
This header defines MT8188 memory/IOMMU port IDs across many software-indexed SMI larbs. It documents non-linear larb numbering, two MM IOMMU hardware blocks, and suggested 16GB IOVA partitioning for display, vcodec, camera/MDP, and CCU regions.

## Important APIs, types, and functions
It exports `SMI_L*_ID` software larb indexes and hundreds of `M4U_PORT_L*_*` constants built with `MTK_M4U_ID`, plus `IFR_IOMMU_PORT_PCIE_0` for infra IOMMU. Ports cover VDO/VPP display, MDP, WPE, IMG, camera raw/CAMSV/CCU, VDEC, VENC, and related fake/reserved engines.

## Control flow
MT8188 DTS nodes use these constants in `iommus` specifiers. The MediaTek IOMMU and SMI drivers decode IDs into larb/port pairs, attach devices to the correct IOMMU instance, and apply the DMA address-region policy described in the comments.

## State and persistence
The header has no runtime state. DTB constants persist across boots; runtime state lives in IOMMU page tables, SMI larb power state, and fault registers.

## Dependencies and integration points
It includes `mtk-memory-port.h` and integrates with MT8188 display/video/image/camera pipelines, VDO/VPP IOMMU instances, PCIe infra IOMMU, and SMI larb drivers.

## Risks and test signals
Risks include software larb reindexing drift from hardware names, assigning a port to the wrong IOMMU instance, crossing documented 4GB IOVA boundaries, and duplicate/reserved fake-engine use. Test signals include `dtbs_check`, IOMMU attach traces per larb, SMI power-domain tests, multimedia DMA stress, IOMMU fault injection, and PCIe infra IOMMU validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8188-memory-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8189-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8189-memory-port.h

## Purpose
This header defines MediaTek MT8189 memory/IOMMU port IDs for display, MDP, video, WPE, image, camera, CCU, APU, and infra PCIe clients.

## Important APIs, types, and functions
It exports software larb IDs `SMI_L0_ID` through `SMI_L20_ID`, port macros named `M4U_Lx_Py_*` using `MTK_M4U_ID`, named workload ports such as `M4U_PORT_WFD_HEAP`, APU ports `M4U_L0_APU_DATA/CODE/SECURE/VLM`, and `IFR_IOMMU_PORT_PCIE_0`.

## Control flow
DTS nodes place these constants in IOMMU specifier cells. MediaTek IOMMU code decodes the larb and port values to bind each hardware master and route DMA through the intended translation domain.

## State and persistence
No state is held in the header. The selected IDs persist in DTBs; runtime mappings, faults, and page-table state live in the IOMMU drivers and hardware.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8189 display, MDP, VDEC/VENC, camera, WPE/IPE/FDVT, APU, and PCIe IOMMU consumers.

## Risks and test signals
Risks include sparse software larb numbering, incorrect port suffix interpretation, and cross-subsystem DMA routed through the wrong domain. Test signals include DTS validation, larb probe logs, IOMMU attach/fault tests per multimedia block, APU DMA tests, and PCIe IOMMU smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8189-memory-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8365-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8365-larb-port.h

## Purpose
This header defines MT8365 SMI larb IDs and M4U port IDs for display, camera, MDP, VENC, and VDEC clients.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB3_ID` and `M4U_PORT_*` constants built with `MTK_M4U_ID`, including display OVL/RDMA/WDMA, camera IMGI/IMG2O/LSCI, MDP RDMA/WROT/WDMA, VENC ports, and hardware VDEC external ports.

## Control flow
MT8365 DTS nodes use the constants in `iommus` properties. The MediaTek IOMMU driver decodes each ID into larb and port values for SMI/IOMMU attachment.

## State and persistence
The file has no state. DTB port selections persist; runtime state is in IOMMU mappings and SMI hardware.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8365 SMI larb, display, camera, MDP, VENC, VDEC, and IOMMU drivers.

## Risks and test signals
Risks include assigning a port to the wrong larb, missing VDEC external port coverage, and DTS values drifting from driver larb data. Test signals include `dtbs_check`, IOMMU attach logs, multimedia DMA stress, and IOMMU fault decoding that reports expected larb/port pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8365-larb-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2701-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2701-larb-port.h

## Purpose
This header defines MT2701 M4U larb port IDs using explicit larb port offsets for display, VDEC, camera, MDP, VENC, and JPGDEC clients.

## Important APIs, types, and functions
It exports `LARB0_PORT_OFFSET` through `LARB3_PORT_OFFSET`, helper macros `MT2701_M4U_ID_LARB0..3(port)`, and `MT2701_M4U_PORT_*` constants for display OVL/RDMA/WDMA, VDEC MC/PP/VLD/MV, camera IMGI/IMG2O, MDP RDMA/WDMA/WROT, VENC, and JPEG decode write DMA.

## Control flow
DTS nodes use the port macros in IOMMU specifiers. The MT2701 IOMMU driver receives flat IDs derived from larb offsets and maps them to M4U port hardware.

## State and persistence
No state exists in the header. The flat IDs persist in DTBs; runtime state is in M4U/IOMMU configuration and fault registers.

## Dependencies and integration points
It integrates with the older MT2701 MediaTek IOMMU binding style, SMI larb hardware, and display/video/camera/MDP/JPEG drivers.

## Risks and test signals
Risks include offset arithmetic errors, flat ID collisions between larbs, and mismatches with newer `MTK_M4U_ID` style bindings. Test signals include DTS preprocessing, IOMMU probe, DMA tests for every larb, and fault reports matching the expected flat port ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2701-larb-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2712-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2712-larb-port.h

## Purpose
This header defines MT2712 larb IDs and M4U port IDs for display, VDEC, CAM, VENC, MDP, and video output/write channels.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB6_ID` and `M4U_PORT_*` constants using `MTK_M4U_ID`, including display, VDEC external, camera, VENC, MDP RDMA/WROT, VDO, NR, TVD, and write channel ports.

## Control flow
Device-tree `iommus` specifiers reference these macros. The MT2712 IOMMU/SMI drivers decode the larb and port fields to attach each multimedia master to translation hardware.

## State and persistence
The header has no runtime state. DTB IDs are persistent board/SoC configuration; runtime state lives in IOMMU page tables and SMI larb registers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT2712 display/video/camera/MDP pipelines and MediaTek IOMMU drivers.

## Risks and test signals
Risks include mixed display/video port naming, wrong larb for video output channels, and port collisions from manual additions. Test signals include `dtbs_check`, IOMMU attach logs, display/camera/video DMA stress, and fault decoding by larb/port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2712-larb-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt6795-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt6795-larb-port.h

## Purpose
This header defines MT6795 larb and M4U port IDs for display, video decode, camera, video encode, and MJC motion/processing clients.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB5_ID` and `M4U_PORT_*` constants for display OVL/RDMA/WDMA, VDEC, camera IMGI/IMG2O/LSCI, VENC stream/current/reference ports, and MJC read/write DMA ports.

## Control flow
MT6795 DTS uses these macros in IOMMU specifiers. MediaTek IOMMU logic decodes `MTK_M4U_ID` values into larb/port identifiers for SMI and M4U programming.

## State and persistence
No state is stored here. DTB port IDs are persistent; runtime DMA translation and faults are managed by the driver.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT6795 display, VDEC, camera, VENC, MJC, SMI, and IOMMU code.

## Risks and test signals
Risks include legacy port naming drift, wrong VENC set assignment, and MJC port misrouting. Test signals include DTS validation, larb attach traces, multimedia DMA tests, and IOMMU fault reports matching the named client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt6795-larb-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8167-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8167-larb-port.h

## Purpose
This header defines MT8167 larb IDs and M4U port IDs for display, video encode, image/camera, and video decode clients.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB2_ID` and `M4U_PORT_*` constants for display OVL/RDMA/WDMA, MDP, VENC, camera/image ports, and VDEC external ports.

## Control flow
DTS `iommus` properties use these macros. The MT8167 IOMMU driver decodes the resulting IDs to associate each device with SMI larb and port hardware.

## State and persistence
The header is stateless. Port IDs persist in DTBs; runtime state is controlled by MediaTek IOMMU and SMI drivers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8167 display, MDP, VENC, camera/image, VDEC, SMI, and IOMMU support.

## Risks and test signals
Risks include wrong larb assignment across compact three-larb layout and incomplete VDEC port coverage. Test signals include `dtbs_check`, SMI larb probe, DMA stress for each multimedia block, and fault decode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8167-larb-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8173-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8173-larb-port.h

## Purpose
This header defines MT8173 larb IDs and M4U port IDs for display, VDEC, camera, VENC, and alternate VENC port sets.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB5_ID` and `M4U_PORT_*` constants, including display OVL/RDMA/WDMA, VDEC external ports, camera image ports, VENC RCPU/REC/BSDMA/current/reference ports, and `_SET2` VENC aliases.

## Control flow
MT8173 DTS nodes reference the constants in IOMMU specifiers. The MediaTek IOMMU driver splits `MTK_M4U_ID` values into larb/port fields to program SMI and M4U hardware.

## State and persistence
No header state exists. DTB IDs persist and runtime translation state is held by the IOMMU subsystem.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8173 display, video decode/encode, camera, SMI larb, and IOMMU drivers.

## Risks and test signals
Risks include confusing base VENC ports with `_SET2` ports, port collision during additions, and DTS/driver table mismatch. Test signals include DTS validation, VENC/VDEC DMA tests, display/camera streaming, and IOMMU fault reports with expected larb/port IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8173-larb-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8183-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8183-larb-port.h

## Purpose
This header defines MT8183 larb IDs and M4U port IDs for display, VDEC, VPU/IPU, VENC, camera, WPE/DPE/MFB/RSC, and CCU clients.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB7_ID` and `M4U_PORT_*` constants using `MTK_M4U_ID`. Ports include display OVL/RDMA/WDMA/MDP, VDEC, image IPU, camera IPU, VENC, extensive camera larb5/6 ports, and `M4U_PORT_CCU0/1`.

## Control flow
DTS files reference these constants in IOMMU specifiers. The MediaTek IOMMU driver decodes larb/port fields to configure translation for each multimedia and camera master.

## State and persistence
The file is stateless. DTB port IDs are persistent; runtime state lives in SMI larbs, IOMMU page tables, and fault tracking.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8183 display, VDEC, VENC, VPU/IPU, camera, CCU, SMI, and IOMMU drivers.

## Risks and test signals
Risks include tab/spacing inconsistency hiding macro additions, camera larb6 port count approaching the 5-bit port field limit, and wrong IPU/camera larb split. Test signals include `dtbs_check`, multimedia and camera stream tests, CCU DMA tests, and fault decode validation for high-numbered camera ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8183-larb-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8186-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8186-memory-port.h

## Purpose
This header defines MT8186 IOMMU port IDs for display, MDP, VDEC, VENC/JPEG, WPE, image, camera, CCU, and IPE/FDVT clients. Comments document 16GB IOVA partitioning across display, vcodec, camera/MDP, and CCU.

## Important APIs, types, and functions
It exports `IOMMU_PORT_L*_*` macros built with `MTK_M4U_ID` across larbs 0, 1, 2, 4, 7, 8, 9, 11, 13, 14, 16, 17, 19, and 20. It includes reserved/fake ports and separate camera A/B larb variants.

## Control flow
MT8186 DTS nodes use the macros in IOMMU specifiers. The MediaTek IOMMU/SMI stack decodes the IDs into larb and port, then attaches masters to the configured DMA translation domain.

## State and persistence
The header has no state. DTB IDs persist; runtime state lives in IOMMU mappings, SMI power/clock state, and fault registers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8186 display, MDP, VDEC/VENC, WPE/image/camera, CCU, IPE, SMI, and IOMMU drivers.

## Risks and test signals
Risks include wrong IOVA region assignment, fake/reserved port misuse, and confusing `IOMMU_PORT_*` naming with older `M4U_PORT_*` consumers. Test signals include `dtbs_check`, IOMMU attach logs, DMA stress per subsystem, SMI larb suspend/resume tests, and fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8186-memory-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8192-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8192-larb-port.h

## Purpose
This header defines MT8192 M4U port IDs for multimedia IOMMU clients across display, MDP, VDEC/VENC, WPE, image, camera, CCU, and IPE/FDVT blocks. Comments describe 16GB IOVA region partitioning.

## Important APIs, types, and functions
It exports `M4U_PORT_L*_*` constants using `MTK_M4U_ID` for larbs 0, 2, 4, 5, 7, 8, 9, 11, 13, 14, 16, 17, 19, and 20. Names identify display, codec, image, camera, CCU, IPE, fake, and reserved ports.

## Control flow
MT8192 DTS uses these macros in `iommus` properties. Runtime MediaTek IOMMU code decodes the larb/port fields and manages DMA translation for each SMI master.

## State and persistence
No state exists in the header. IDs are persistent DT configuration; runtime state is in page tables and SMI/IOMMU registers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8192 display, MDP, VDEC/VENC, WPE, image, camera, CCU, IPE/FDVT, SMI, and IOMMU drivers.

## Risks and test signals
Risks include duplicated functional ports across MDP/DISP domains, boundary-sensitive IOVA mapping, and DTS using an undefined larb. Test signals include `dtbs_check`, SMI/IOMMU probe, multimedia pipeline DMA tests, CCU camera tests, and fault log larb/port verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8192-larb-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8195-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8195-memory-port.h

## Purpose
This header defines MT8195 multimedia and infra IOMMU port IDs. It spans VDO/VPP display, MDP, WPE, image, camera, CCU, VDEC/VENC/JPEG, and infra PCIe/USB clients, with comments documenting two MM IOMMUs and 16GB IOVA partitioning.

## Important APIs, types, and functions
It exports many `M4U_PORT_L*_*` macros built with `MTK_M4U_ID` for software larbs, plus `IOMMU_PORT_INFRA_*` macros built with `MTK_IFAIOMMU_PERI_ID` for PCIe and SSUSB read/write ports.

## Control flow
MT8195 DTS nodes use the constants in IOMMU specifiers. MediaTek MM IOMMU drivers decode larb/port values for multimedia masters, while infra IOMMU consumers use peri IDs for PCIe/USB clients.

## State and persistence
There is no header state. Port IDs persist in DTBs; runtime mapping, fault, and SMI state lives in the IOMMU and SMI drivers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8195 VDO/VPP, display, MDP, WPE, IMG, CAM, CCU, VDEC/VENC/JPEG, PCIe, USB, SMI, MM IOMMU, and infra IOMMU code.

## Risks and test signals
Risks include wrong software larb reindexing, assigning a port to the wrong MM IOMMU, confusing infra peri IDs with MM larb IDs, and crossing documented 4GB boundaries. Test signals include DTS validation, MM and infra IOMMU attach logs, display/video/camera DMA stress, PCIe/USB DMA tests, and IOMMU fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8195-memory-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mtk-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mtk-memory-port.h

## Purpose
This shared MediaTek memory binding header defines helper macros for packing and unpacking larb/port IDs used by many MediaTek M4U/IOMMU port headers.

## Important APIs, types, and functions
It exports `MTK_LARB_NR_MAX`, `MTK_M4U_ID(larb, port)`, `MTK_M4U_TO_LARB(id)`, `MTK_M4U_TO_PORT(id)`, and `MTK_IFAIOMMU_PERI_ID(port)`. The packing uses 5 bits for the port and supports larb IDs up to 31.

## Control flow
SoC-specific headers include this file and build concrete port macros. DTS preprocessing emits packed IDs; MediaTek IOMMU drivers decode them with the inverse helpers or equivalent logic.

## State and persistence
No state exists. The packing format is stable DT ABI and is embedded in all dependent DTBs.

## Dependencies and integration points
It is a dependency for MediaTek larb/memory-port headers and integrates with SMI larb drivers, M4U/IOMMU code, and infra IOMMU per-port IDs.

## Risks and test signals
Risks include port values above 31 truncating in `MTK_M4U_TO_PORT`, larb values above `MTK_LARB_NR_MAX`, and SoC headers using helper names not defined here. Test signals include preprocessing every dependent header, static scans for port values over 31, `dtbs_check`, and IOMMU fault decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mtk-memory-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/nvidia,tegra264.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/nvidia,tegra264.h

## Purpose
This header defines NVIDIA Tegra264 SMMU stream IDs and memory controller client IDs for device-tree memory/interconnect/IOMMU bindings.

## Important APIs, types, and functions
It exports `TEGRA264_SID(x)` and stream ID macros for AON, APE, BPMP, DCE, EQOS, GPCDMA, display, host1x, ISP, FSI, PVA, SDMMC0, MGBE, security engines, PSC, UFS, RCE, VI, VIC, and XUSB devices. It also exports `TEGRA264_MEMORY_CLIENT_*` IDs for host1x, VIC, VI, NVDEC, BPMP, display, UFS, DLA/PVA-like accelerators, PCIe, MGBE, SDMMC, and USB-related clients.

## Control flow
Tegra264 DTS nodes use SIDs in IOMMU specifiers and memory client IDs in memory controller properties. The SMMU and memory controller drivers decode the values to program stream matching, isolation, and bandwidth/fault accounting.

## State and persistence
The header has no state. SIDs and client IDs persist in DTBs; runtime state lives in the SMMU, memory controller, and client drivers.

## Dependencies and integration points
It integrates with Tegra264 SMMU, host1x/display, camera/VI/ISP/RCE, BPMP, networking, storage, USB, security engines, and memory controller drivers.

## Risks and test signals
Risks include SID shift misuse from `TEGRA264_SID(x)`, assigning unshifted values in DTS, and memory-client ID drift from hardware manuals. Test signals include `dtbs_check`, SMMU probe and stream table logs, DMA tests per client class, memory-controller fault reporting, and BPMP/firmware compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/nvidia,tegra264.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra114-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra114-mc.h

## Purpose
This header defines Tegra114 memory controller software group IDs and reset IDs for memory clients.

## Important APIs, types, and functions
It exports `TEGRA_SWGROUP_*` IDs for PTC, DC/DCB, EPP, G2, MPE, VI, AFI, AVPC, NV, HC, PPCS, SATA, VDE, and MPCORELP, plus reset IDs `TEGRA114_MC_RESET_*` for AVPC, display, EPP/2D/3D, HC/HDA, ISP, CPU clusters, MPE, PPCS, VDE, and VI.

## Control flow
Tegra114 DTS uses these constants in memory-controller/IOMMU and reset specifiers. The Tegra MC driver maps IDs to SWGROUP registers and reset controls.

## State and persistence
The header is stateless. DTB values persist; runtime isolation, reset, and fault state is in MC hardware and drivers.

## Dependencies and integration points
It integrates with Tegra114 memory controller, SMMU/SWGROUP configuration, reset controller users, display, video, SATA, host, and CPU-related clients.

## Risks and test signals
Risks include confusing SWGROUP IDs with reset IDs, wrong client reset line, and compatibility drift with Tegra124/210 headers that share names. Test signals include DTS validation, MC probe, client reset tests, DMA isolation tests, and memory fault logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra114-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra124-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra124-mc.h

## Purpose
This header defines Tegra124 memory controller SWGROUP IDs, reset IDs, and memory client IDs for device tree.

## Important APIs, types, and functions
It exports `TEGRA_SWGROUP_*` IDs, `TEGRA124_MC_RESET_*` reset controls, and many `TEGRA124_MC_*` memory client IDs such as display, AFI, AVPC, HDA, host1x, MSENC, SATA, VDE, CPU, ISP, XUSB, TSEC, GPU, SDMMC, VIC, and displayD clients.

## Control flow
DTS nodes use SWGROUPs for memory isolation, reset IDs for MC-driven resets, and memory client IDs for MC client configuration. Tegra MC drivers decode the constants to program hardware tables and reset bits.

## State and persistence
No state exists here. IDs persist in DTBs; runtime MC state includes resets, arbitration, fault reporting, and SMMU/SWGROUP configuration.

## Dependencies and integration points
It integrates with Tegra124 MC/SMMU, reset controller, display, host1x, HDA, SATA, VDE, ISP, XUSB, TSEC, GPU, SDMMC, and VIC drivers.

## Risks and test signals
Risks include sparse memory client IDs, mixing reset and client namespaces, and using shared `TEGRA_SWGROUP_*` names from another Tegra generation incorrectly. Test signals include DTS validation, MC probe, reset assertions/deassertions, DMA from major clients, and MC fault decode correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra124-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra186-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra186-mc.h

## Purpose
This header defines Tegra186 SMMU stream IDs and memory controller client IDs for device-tree memory/IOMMU configuration.

## Important APIs, types, and functions
It exports SIDs including `TEGRA186_SID_INVALID`, `PASSTHROUGH`, host1x, CSI, VIC, VI, ISP, NVDEC, NVENC, NVJPG, display, TSEC, SE, GPU, AFI, HDA, ETR, APE, SCE, BPMP, AON, SDMMC, XUSB, SATA, and APEDMA-related IDs. It also exports `TEGRA186_MEMORY_CLIENT_*` IDs for MC fault/accounting clients.

## Control flow
Tegra186 DTS nodes use SIDs in IOMMU specifiers and memory client IDs in MC-related properties. The SMMU and MC drivers decode the values during device attach, stream setup, and fault reporting.

## State and persistence
The header is stateless. DTB IDs persist across boots; runtime state is held by SMMU context, MC registers, and client drivers.

## Dependencies and integration points
It integrates with Tegra186 SMMU, memory controller, host1x/display, camera, video, security engines, storage, USB, BPMP, AON, and DMA clients.

## Risks and test signals
Risks include using `PASSTHROUGH` unintentionally, mismatched SID/client ID namespaces, and firmware-reserved IDs changing behavior. Test signals include DTS validation, SMMU attach logs, DMA tests for each client class, MC fault injection, and BPMP/AON communication tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra186-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra194-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra194-mc.h

## Purpose
This header defines Tegra194 SMMU stream IDs and memory controller client IDs, including virtualization-capable host1x/security-engine stream IDs and a large set of MC clients.

## Important APIs, types, and functions
It exports `TEGRA194_SID_*` values for core engines, GPU, AFI/HDA/ETR/EQOS/UFS/AON/SDMMC/XUSB/SATA/APE/SCE, GPCDMA, RCE/VI/ISP falcons, BPMP, host1x contexts/VMs, SE VMs, NVDLA/PVA/NVENC/PCIe/XUSB VFs, and additional VM/server IDs. It also exports `TEGRA194_MEMORY_CLIENT_*` IDs from low legacy clients through MIU, NVL, DLA, PVA, RCE, PCIe, and extended codec clients.

## Control flow
DTS uses SIDs for IOMMU stream matching and memory client IDs for memory controller configuration or fault identification. Tegra SMMU/MC drivers decode them during device attach, context isolation, and fault reporting.

## State and persistence
No state lives in the header. The IDs persist in DTBs; runtime state exists in SMMU stream tables, MC registers, virtualization contexts, and firmware-coordinated clients.

## Dependencies and integration points
It integrates with Tegra194 SMMU, memory controller, host1x virtualization, display, camera/RCE/VI/ISP, GPU, NVDLA/PVA, PCIe, XUSB, UFS, EQOS, BPMP, AON, SCE, APE, and security engine drivers.

## Risks and test signals
Risks include altering firmware-sensitive IDs such as BPMP, confusing host1x context IDs with VM IDs, passthrough misuse, and sparse MC client IDs hiding omissions. Test signals include DTS validation, SMMU attach logs, virtualization context tests, BPMP boot, PCIe/XUSB/UFS DMA, accelerator DMA, and MC fault decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra194-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra20-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra20-mc.h

## Purpose
This header defines Tegra20 memory controller reset IDs and memory client IDs for early Tegra device-tree bindings.

## Important APIs, types, and functions
It exports reset IDs `TEGRA20_MC_RESET_*` for AVPC, display, EPP, 2D/3D, HC, ISP, CPU, MPE, PPCS, VDE, and VI. It also exports `TEGRA20_MC_*` memory client IDs for display, EPP, G2, MPE, VI, AVPC, host1x, CPU, PPCS, texture, VDE, ISP, and read/write variants.

## Control flow
Tegra20 DTS uses these constants in memory-controller reset and client specifiers. The Tegra20 MC driver maps IDs to reset bits and memory client registers.

## State and persistence
The header is stateless. DTB IDs persist; runtime state includes memory client arbitration/faults and reset-control state.

## Dependencies and integration points
It integrates with Tegra20 MC, reset controller, display, host1x, 2D/3D, VI/ISP, VDE, MPE, PPCS, and CPU memory clients.

## Risks and test signals
Risks include mixing reset IDs and memory client IDs, sparse client numbering, and old-generation naming differences from later Tegra headers. Test signals include DTS validation, MC probe, reset tests for display/VDE/VI, DMA smoke tests, and MC fault decode checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra20-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra210-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra210-mc.h

## Purpose
This header defines Tegra210 memory controller SWGROUP IDs, reset IDs, and memory client IDs for DT memory/SMMU/reset bindings.

## Important APIs, types, and functions
It exports `TEGRA_SWGROUP_*` IDs for PTC, display, AFI, AVPC, HDA, host, NVENC, SATA, CPU, ISP, XUSB, TSEC, GPU, SDMMC, VIC, VI, NVDEC, APE, NVJPG, SE, AXIAP, ETR, and related groups. It also exports `TEGRA210_MC_RESET_*` reset IDs and `TEGRA210_MC_*` memory clients for display, AFI, AVPC, HDA, host1x, NVENC, SATA, CPU, ISP, XUSB, TSEC, GPU, SDMMC, VIC, VI, NVDEC, APE, NVJPG, SE, AXIAP, and ETR read/write clients.

## Control flow
Tegra210 DTS nodes reference these constants in SMMU/memory-controller/reset specifiers. The Tegra MC/SMMU and reset drivers decode the numeric cells to program SWGROUP isolation, reset bits, and memory client tracking.

## State and persistence
No state is stored in the header. IDs persist in DTBs; runtime state lives in MC registers, SMMU/SWGROUP configuration, reset controls, and fault reporting.

## Dependencies and integration points
It integrates with Tegra210 memory controller, SMMU, reset controller, display, host1x, storage, USB, GPU, media, security, audio, and CPU clients.

## Risks and test signals
Risks include namespace confusion between SWGROUP, reset, and memory client constants, sparse client ID gaps, and generation drift from Tegra124. Test signals include `dtbs_check`, MC/SMMU probe, reset operations, DMA from display/GPU/storage/USB/media clients, and MC fault decode accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra210-mc.h -->
