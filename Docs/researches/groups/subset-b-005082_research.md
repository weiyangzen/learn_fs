# Research: subset-b-005082

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qcs8300.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qcs8300.c

## Purpose
This file is the Qualcomm QCS8300 TLMM pin controller description consumed by the shared `pinctrl-msm` core. It enumerates QCS8300 pins, pin groups, mux functions, GPIO register layout, special SD/UFS groups, eGPIO-capable pads, QUP I3C mode offsets, and GPIO-to-PDC wake interrupt mappings. Runtime behavior is intentionally thin: the driver binds to `qcom,qcs8300-tlmm` and delegates almost all pinctrl, GPIO, and interrupt operations to `msm_pinctrl_probe()`.

## Important APIs, Types, And Functions
The file builds static tables for `struct pinctrl_pin_desc`, `struct pinfunction`, `struct msm_pingroup`, `struct msm_gpio_wakeirq_map`, and `struct msm_pinctrl_soc_data`. `PINGROUP()` is the central macro: for each GPIO it names the pinctrl group, supplies up to 11 alternate functions plus GPIO mode, and records register offsets and bit positions. QCS8300 differs from many older TLMM descriptions by carrying eGPIO register bits (`egpio_enable`, `egpio_present`) and declaring `.egpio_func = 11`, so the last mux slot is the eGPIO function for selected groups. `SDC_QDSD_PINGROUP()` models fixed SD card pads without GPIO/IRQ bits, while `UFS_RESET()` models the UFS reset output-only special group. `QUP_I3C()` and the QUP I3C offset constants describe I3C mode registers for selected QUP instances.

## Control Flow
Static initialization constructs the pin, function, group, and wake map tables. At `arch_initcall()` time `qcs8300_pinctrl_init()` registers a `platform_driver` named `qcs8300-tlmm`. OF matching on `qcom,qcs8300-tlmm` calls `qcs8300_pinctrl_probe()`, which passes `qcs8300_pinctrl` to the common MSM pinctrl core. From that point, mux selection, bias/drive configuration, GPIO direction/value operations, IRQ programming, wake IRQ mapping, and debugfs exposure are handled by `pinctrl-msm.c` using this file's data.

## State And Persistence
There is no mutable driver-private state in this file. All tables are `static const` and persist for the module lifetime. Hardware state lives in TLMM registers at 0x1000-byte GPIO strides and in special SD/UFS registers; the common core writes those registers in response to pinctrl, GPIO, and irqchip requests. Wake behavior depends on the static `qcs8300_pdc_map`. The eGPIO mode is data-driven by the group function slot and eGPIO present/enable bits.

## Dependencies And Integration Points
The driver depends on Linux platform driver and OF matching infrastructure plus `pinctrl-msm.h`. It integrates with device tree `pinctrl-*` states, the gpiolib provider registered by the MSM core, irqchip and PDC wake interrupt plumbing, serial/audio/display/camera/storage consumers named in the mux tables, SDHCI through `sdc1_*` groups, and UFS through `ufs_reset`. The `MODULE_DEVICE_TABLE(of, ...)` entry allows module autoloading for the compatible string.

## Risks And Test Signals
Risk is concentrated in data fidelity. A wrong mux slot changes a peripheral's selected function; a wrong register offset or bit index can affect unrelated pins; and a bad PDC mapping breaks suspend wake without breaking normal interrupts. The `ngpios = 134` boundary is important because the table also includes UFS/SD special groups beyond GPIO numbering. eGPIO pads from 110 through 132 need explicit validation because they rely on the extra mux function index and eGPIO status bits. Test signals include successful probe on a QCS8300 DT, pinctrl state application for QUP/I3C, audio, display, camera, SD, and UFS reset consumers, GPIO IRQ delivery and wake from mapped pads, and suspend/resume tests that verify PDC wake mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qcs8300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qdf2xxx.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qdf2xxx.c

## Purpose
This is an ACPI-only Qualcomm QDF2xxx TLMM client for server-style systems where firmware owns pin muxing. It deliberately exposes only GPIO and GPIO interrupt behavior through the shared MSM pinctrl core, avoiding a static SoC mux table because UEFI is expected to configure pin control. The driver dynamically builds pin and group descriptors from ACPI device properties.

## Important APIs, Types, And Functions
`qdf2xxx_pinctrl_probe()` is the core function. It reads `num-gpios` and a `gpios` byte array from device properties, validates them against `MAX_GPIOS` (256), allocates `struct msm_pinctrl_soc_data`, `struct pinctrl_pin_desc`, `struct msm_pingroup`, and persistent GPIO names with device-managed memory, then calls `msm_pinctrl_probe()`. The generated groups use the same register bit layout as classic MSM TLMM GPIOs: 0x10000-byte GPIO register stride, mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, and interrupt detection/polarity/target fields.

## Control Flow
At `arch_initcall()` the `qdf2xxx-pinctrl` platform driver is registered. ACPI matching uses the `QCOM8002` ID. Probe first requires a sane total GPIO count, then requires a non-empty approved GPIO list no larger than the total. It initializes all pin numbers and group pin pointers so the array indices remain valid for the MSM core, but only GPIOs named in the `gpios` property receive names, `npins = 1`, register offsets, and GPIO/IRQ bit metadata. Finally it passes the generated SoC data to `msm_pinctrl_probe()`.

## State And Persistence
Unlike the other files in this work item, the SoC data is allocated at probe time and is owned by devres. Names are allocated once because pinctrl/gpiolib store pointers to them. There is no persistent on-disk state and no custom remove path. Hardware state is whatever firmware and later GPIO/IRQ requests program into TLMM registers; the driver does not expose mux functions or pin configuration states beyond GPIO semantics.

## Dependencies And Integration Points
The file depends on ACPI/device-property APIs, platform driver registration, pinctrl descriptors, and `pinctrl-msm.h`. It integrates with firmware through `num-gpios` and `gpios` properties, with gpiolib through the MSM core, and with ACPI enumeration through `QCOM8002`. It intentionally does not use OF matching and does not define static `struct pinfunction` arrays.

## Risks And Test Signals
The main risk is property correctness. If firmware reports too many GPIOs, omits the approved list, or includes GPIO numbers outside the allocated range, probe can fail or write out of bounds; the code validates counts but trusts each `gpios[i]` value to be less than `num_gpios`. Another subtle risk is sparse GPIO exposure: unnamed/unavailable GPIOs still occupy array slots, so consumers must request only approved GPIO numbers. Test signals include ACPI enumeration, missing/invalid property failure messages, successful `gpiochip` registration with the expected sparse lines, GPIO direction/value operations, IRQ configuration from approved GPIOs, and confirmation that no pin mux states are required for boot because firmware already configured them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qdf2xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qdu1000.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qdu1000.c

## Purpose
This file describes the Qualcomm QDU1000 TLMM pin controller for the shared MSM pinctrl core. It provides the static pin inventory, mux functions, per-pin mux group table, special SD card groups, and QUP/I3C metadata for a large industrial/networking-oriented SoC. It binds to `qcom,qdu1000-tlmm` and uses a register base offset of `0x100000` for normal GPIO groups.

## Important APIs, Types, And Functions
The important data types are `struct pinctrl_pin_desc`, `struct pinfunction`, `struct msm_pingroup`, and `struct msm_pinctrl_soc_data`. `PINGROUP()` defines ordinary GPIO groups with ten function slots including GPIO mode, `REG_BASE + REG_SIZE * id` register placement, and the standard MSM TLMM GPIO/IRQ bit positions. `SDC_QDSD_PINGROUP()` describes the four fixed `sdc1_*` groups at the end of the table. `UFS_RESET()` exists in the file but the visible group table for this variant uses SD special groups, not a UFS reset group. `QUP_I3C()` is available for QUP I3C mode/offset metadata used by the common pinctrl code where matching function data is present.

## Control Flow
The module registers `qdu1000_tlmm_driver` at `arch_initcall()`. OF matching on `qcom,qdu1000-tlmm` invokes `qdu1000_tlmm_probe()`, which delegates directly to `msm_pinctrl_probe(pdev, &qdu1000_tlmm)`. The MSM core then consumes `.pins`, `.functions`, `.groups`, and `.ngpios = 151` to register pinctrl, pinmux, pinconf, GPIO, and irqchip interfaces. There are no local runtime callbacks beyond probe and driver unregister.

## State And Persistence
All pin data is immutable static storage. Runtime state, including selected muxes, bias, drive strength, GPIO direction/value, and interrupt configuration, is stored in TLMM hardware registers and managed by `pinctrl-msm.c`. The file has no wake IRQ map, so wake integration is limited to what the common core and platform interrupt wiring can infer without a GPIO-to-PDC table in this descriptor.

## Dependencies And Integration Points
The driver depends on OF platform matching and `pinctrl-msm.h`. It integrates with device tree pinctrl consumers for QUP serial engines, QSPI, qlink, Ethernet interrupt pins, PCIe clock request pins, PPS/GPS, debug/trace (`qdss_*`), SDHCI via `sdc1_*`, USB-related signals, and multiple timing/test functions. The `MODULE_DEVICE_TABLE(of, ...)` line provides module aliasing for the TLMM compatible.

## Risks And Test Signals
Most risk is table correctness: QDU1000 exposes many similarly named QUP, QSPI, qlink, DDR PXI, and debug functions, so copy/paste errors can silently route a signal to the wrong pad. The `.ngpios = 151` value excludes the special SD groups at indices 151-154; off-by-one mistakes here could expose non-GPIO pads as GPIOs. The `REG_BASE` offset must match the SoC memory map. Test signals include successful probe, pinctrl state selection for representative QUP/QSPI/qlink/SD consumers, gpiolib line count of 151, GPIO IRQ programming on normal pads, and SD card/eMMC signaling on the special `sdc1_*` groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-qdu1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sa8775p.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sa8775p.c

## Purpose
This is the Qualcomm SA8775P TLMM pin controller data driver. It describes a 150-GPIO automotive SoC pin controller, including alternate functions for QUP, camera, display, audio, Ethernet/Sail, debug, test, and storage signals; eGPIO-capable pads; UFS reset; SD card pads; and a GPIO-to-PDC wake interrupt map. Probe delegates to the shared MSM pinctrl implementation.

## Important APIs, Types, And Functions
`PINGROUP()` defines the ordinary GPIO groups with ten function slots, `REG_BASE` of `0x100000`, `REG_SIZE` of `0x1000`, eGPIO presence/enable bits, and a four-bit interrupt target field (`intr_target_width = 4`). `SDC_QDSD_PINGROUP()` and `UFS_RESET()` describe nonstandard storage pads. The static arrays `sa8775p_pins`, `sa8775p_functions`, `sa8775p_groups`, and `sa8775p_pdc_map` are collected in `sa8775p_pinctrl`, where `.ngpios = 150`, `.wakeirq_map` is supplied, and `.egpio_func = 9` marks the mux index used for eGPIO on selected high-numbered pads.

## Control Flow
The driver is registered during `arch_initcall()` as `sa8775p-tlmm`. A matching DT node with `qcom,sa8775p-tlmm` calls `sa8775p_pinctrl_probe()`, which passes the static descriptor to `msm_pinctrl_probe()`. All operations after probe use the MSM common path: pin group enumeration, mux function lookup, pin configuration register writes, GPIO chip operations, irqchip setup, and wake IRQ translation through the PDC map. Module exit unregisters the platform driver.

## State And Persistence
The file carries no mutable local state. Static tables persist for the module lifetime. Hardware state persists in TLMM registers and PDC wake configuration until reset or reprogramming by the common core. eGPIO status is represented through the eGPIO bit fields in each group and the `.egpio_func` index. Wake state depends entirely on the static map from GPIO numbers to PDC interrupt numbers.

## Dependencies And Integration Points
The driver depends on Linux OF/platform infrastructure and `pinctrl-msm.h`. It integrates with DT pinctrl consumers for QUP serial engines, camera CCI/MCLK, display hotplug and vsync, MI2S/audio, SAIL/EMAC/OSPI/SGMII signals, trace/debug signals, USB test pins, UFS reset, and SDHCI. It also integrates with suspend wake through the `sa8775p_pdc_map`.

## Risks And Test Signals
This file is data-heavy and regression-prone. The four-bit interrupt target width is a notable SoC-specific detail; omitting it would target interrupts incorrectly. The eGPIO block covers pads 126-148 plus selected debug behavior and must match hardware mux numbering. `.ngpios = 150` separates GPIO-capable pads from UFS/SD special groups. Wake tests should cover mapped and unmapped GPIOs because normal GPIO IRQs can work even when PDC wake mapping is wrong. Test signals include probe and GPIO count, pinctrl state application for QUP/camera/display/audio/storage/Ethernet consumers, UFS reset behavior at `0x1a2000`, SD `sdc1_*` drive/pull configuration, GPIO IRQ handling, and suspend wake from representative PDC-mapped GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sa8775p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sar2130p.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sar2130p.c

## Purpose
This file is the Qualcomm SAR2130P TLMM descriptor for `pinctrl-msm`. It defines GPIO pins, functions, pin groups, SD card special pads, and a dense GPIO-to-PDC wake map for the `qcom,sar2130p-tlmm` compatible. The SoC has 156 GPIO-capable pads and four additional SD card groups in the group array.

## Important APIs, Types, And Functions
The driver uses the standard MSM pinctrl data types: `struct pinctrl_pin_desc`, `struct pinfunction`, `struct msm_pingroup`, `struct msm_gpio_wakeirq_map`, and `struct msm_pinctrl_soc_data`. `PINGROUP()` supplies ten mux slots including GPIO, standard GPIO register offsets at `REG_SIZE * id`, eGPIO present/enable bit locations, and interrupt field positions with `intr_target_kpss_val = 4`. `SDC_QDSD_PINGROUP()` describes the `sdc1_rclk`, `sdc1_clk`, `sdc1_cmd`, and `sdc1_data` fixed-function groups. `sar2130p_tlmm_probe()` is the only local probe function and simply delegates to `msm_pinctrl_probe()`.

## Control Flow
During `arch_initcall()`, `sar2130p_tlmm_init()` registers `sar2130p-tlmm`. OF matching uses `qcom,sar2130p-tlmm`, with `.data = &sar2130p_tlmm` in the match entry, although the probe passes the same static object directly. Once probed, pinctrl, pinmux, pinconf, GPIO, and IRQ behavior is entirely driven by the common MSM core using the SAR2130P tables. Exit unregisters the platform driver.

## State And Persistence
There is no dynamic state in this file. Static tables persist for the lifetime of the module or built-in driver. Runtime pin, GPIO, and interrupt state persists in TLMM/PDC hardware and is modified by the common core. The wake map defines which GPIOs can be translated to PDC wake interrupts during suspend.

## Dependencies And Integration Points
The file depends on OF platform driver infrastructure and `pinctrl-msm.h`. Its function table integrates pinctrl states for QUP instances, CCI I2C, QDSS trace/debug, USB PHY/test pins, display hotplug, audio/I2S, phase flags, GCC test clocks, and SDHCI through the fixed SD card groups. The wake map integrates with the Qualcomm PDC wake IRQ mechanism used by suspend/resume.

## Risks And Test Signals
Risks are dominated by table accuracy. SAR2130P has many numbered phase flags and QDSS GPIO functions; a function/group mismatch can be hard to detect unless that exact peripheral is enabled. The group array contains indices 156-159 for SD pads while `.ngpios = 156`, so GPIO exposure must stop before the SD special groups. The wake map is large and nonmonotonic, making suspend wake validation important. Test signals include successful probe on the compatible, `gpiochip` line count of 156, representative QUP/CCI/audio/display/USB pinctrl states, SD card pad configuration, GPIO IRQ operation, and suspend wake tests across several mapped GPIO ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sar2130p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7180.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7180.c

## Purpose
This file describes the Qualcomm SC7180 TLMM pin controller. It is a static data driver for `pinctrl-msm`, but unlike several newer flat-register variants it also models TLMM tiles (`north`, `south`, `west`) and a wake IRQ dual-edge erratum. It defines 120 GPIO-capable pads, UFS reset, SD card pads for `sdc1` and `sdc2`, alternate functions, and a GPIO-to-PDC wake map.

## Important APIs, Types, And Functions
`sc7180_tiles` and the `NORTH`, `SOUTH`, `WEST` enum name the register regions used by group descriptors. `PINGROUP(id, _tile, ...)` supplies a tile plus standard MSM register offsets and mux/config/IRQ bit positions. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` place special storage groups in the south tile. The data tables are `sc7180_pins`, `sc7180_functions`, `sc7180_groups`, `sc7180_pdc_map`, and `sc7180_pinctrl`. The SoC descriptor sets `.tiles`, `.ntiles`, `.ngpios = 120`, `.wakeirq_map`, and `.wakeirq_dual_edge_errata = true`.

## Control Flow
`sc7180_pinctrl_init()` registers the platform driver at `arch_initcall()`. A DT node with `qcom,sc7180-pinctrl` calls `sc7180_pinctrl_probe()`, which hands `sc7180_pinctrl` to `msm_pinctrl_probe()`. The platform driver also supplies `.pm = &msm_pinctrl_dev_pm_ops`, so system power management is handled by the shared MSM code. Runtime operations are data-driven by the common pinctrl, pinconf, gpiolib, irqchip, and wakeirq logic.

## State And Persistence
All local data is static and immutable. Hardware state is split across the TLMM tile register regions and persists until reset or reconfiguration. The common core tracks runtime state, applies pinctrl states, and handles suspend/resume with the PM ops. Wake IRQ behavior uses the static PDC map plus the dual-edge erratum flag, which changes how dual-edge wake handling is treated by the common code.

## Dependencies And Integration Points
The driver depends on OF platform matching and `pinctrl-msm.h`. It integrates with SC7180 device tree pinctrl clients including QUP I2C/UART, QSPI, MI2S, LPASS external signals, display hotplug/vsync, UIM, GPS/PPS, WLAN/QLINK, USB PHY, UFS reset, and SDHCI `sdc1`/`sdc2`. It integrates with suspend wake through PDC mappings and with power management through `msm_pinctrl_dev_pm_ops`.

## Risks And Test Signals
Tile assignment is a key risk: a correct mux function with the wrong tile points the common core at the wrong MMIO region. The dual-edge wake erratum flag is another SoC-specific behavior that should not be dropped during refactors. `.ngpios = 120` must exclude UFS and SD special groups at indices 119-126 as GPIO lines where appropriate. Test signals include successful probe, line count, pinctrl states across all three tiles, UFS reset and both SD controller pad groups, GPIO IRQs, suspend/resume with PM ops, and dual-edge wake testing on representative PDC-mapped GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7180.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7280-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7280-lpass-lpi.c

## Purpose
This file describes the SC7280/SM8350 LPASS LPI audio pin controller, separate from the main TLMM controller. It exposes 15 low-power audio GPIOs and their audio-specific mux functions to the shared `pinctrl-lpass-lpi` core. The functions cover SoundWire TX/RX/WSA signals, DMIC clocks/data, I2S1/I2S2, and quad MI2S signals.

## Important APIs, Types, And Functions
The file uses `enum lpass_lpi_functions`, `struct pinctrl_pin_desc`, `struct lpi_pingroup`, `struct lpi_function`, and `struct lpi_pinctrl_variant_data` from `pinctrl-lpass-lpi.h`. `LPI_PINGROUP()` entries define each GPIO's slew register index or `LPI_NO_SLEW` plus up to four mux functions. `LPI_FUNCTION()` binds each function name to the corresponding group array. `sc7280_lpi_data` is the variant descriptor passed through OF match data to the generic `lpi_pinctrl_probe()`.

## Control Flow
The module uses `module_platform_driver(lpi_pinctrl_driver)`. OF matching accepts both `qcom,sc7280-lpass-lpi-pinctrl` and `qcom,sm8350-lpass-lpi-pinctrl`, each with `.data = &sc7280_lpi_data`. Probe and remove are not local functions; they are `lpi_pinctrl_probe` and `lpi_pinctrl_remove` from the LPI common driver. Once bound, the LPI core exposes pinctrl and GPIO behavior based on the variant data.

## State And Persistence
The file itself has only immutable static tables. Runtime mux, GPIO, and low-power audio pad state is held in LPASS LPI hardware and managed by the common LPI pinctrl core. The slew entries distinguish pads with programmable slew from pads marked `LPI_NO_SLEW`.

## Dependencies And Integration Points
The driver depends on platform driver registration, gpiolib headers, module infrastructure, and `pinctrl-lpass-lpi.h`. It integrates with audio DT nodes that select SoundWire, DMIC, and I2S pinctrl states on SC7280 and SM8350-class LPASS blocks. It is independent from `pinctrl-sc7280.c`, which describes the main TLMM controller.

## Risks And Test Signals
Risk is in function-to-pad mapping and the shared compatible data. A wrong group list can swap audio data/clock/word-select routing and produce silent audio failures. Reusing the SC7280 data for SM8350 should be validated against both SoCs. Pads with `LPI_NO_SLEW` should not expose unsupported slew programming. Test signals include module autoload for both compatibles, pinctrl state selection for SoundWire TX/RX/WSA, DMIC1-3, I2S1/I2S2, quad MI2S, GPIO fallback operation on the 15 pins, and audio capture/playback across suspend or low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7280-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7280.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7280.c

## Purpose
This file describes the Qualcomm SC7280 main TLMM pin controller for `pinctrl-msm`. It enumerates 176 GPIO-capable pads, high-numbered eGPIO-capable pads, UFS reset, SD card special groups for `sdc1` and `sdc2`, alternate function tables, and GPIO-to-PDC wake IRQ mappings. It is the main SoC pinctrl companion to the separate SC7280 LPASS LPI audio pinctrl file.

## Important APIs, Types, And Functions
The primary tables are `sc7280_pins`, `sc7280_functions`, `sc7280_groups`, `sc7280_pdc_map`, and `sc7280_pinctrl`. `PINGROUP()` supplies ten mux slots, standard 0x1000-byte GPIO register spacing, eGPIO bit positions, and IRQ field locations. `SDC_QDSD_PINGROUP()` and `UFS_RESET()` model non-GPIO storage pads. The SoC descriptor sets `.ngpios = 176`, `.wakeirq_map`, `.nwakeirq_map`, and `.egpio_func = 9`. The platform driver also attaches `.pm = &msm_pinctrl_dev_pm_ops`.

## Control Flow
The driver registers at `arch_initcall()` as `sc7280-pinctrl`. A DT node compatible with `qcom,sc7280-pinctrl` invokes `sc7280_pinctrl_probe()`, which calls `msm_pinctrl_probe()` with the static SC7280 descriptor. The MSM core then registers the pin controller, GPIO chip, irqchip, wake IRQ handling, and PM behavior. Local code only handles platform driver registration and unregister.

## State And Persistence
All source-level data is immutable. Hardware state is stored in TLMM registers and controlled by the shared MSM core. eGPIO-capable pads from the high-numbered group range use the eGPIO present/enable bits and mux function index 9. Wake behavior persists through the PDC mapping table and common suspend/resume handling.

## Dependencies And Integration Points
The file depends on OF platform matching, module infrastructure, and `pinctrl-msm.h`. It integrates with DT consumers for QUP serial engines, QSPI, camera, display, audio-adjacent TLMM pins, QDSS trace/debug, USB, UFS reset, SDHCI `sdc1` and `sdc2`, and general GPIO users. Runtime power management and suspend/resume are handled through the common MSM PM ops.

## Risks And Test Signals
SC7280 has many mux aliases and eGPIO-capable high pads, so function ordering and `.egpio_func = 9` are high-risk data points. `.ngpios = 176` must exclude UFS and SD special groups at indices 175-182 from normal GPIO exposure as intended by the common core. The wake map is large enough that single-entry mistakes can produce suspend-only regressions. Test signals include successful probe with 176 GPIO lines, pinctrl state selection for QUP/QSPI/camera/display/UFS/SD clients, eGPIO mode validation on pads 144-174, GPIO IRQ operation, suspend wake from representative PDC-mapped GPIOs, and resume behavior through `msm_pinctrl_dev_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sc7280.c -->
