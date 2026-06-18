# subset-b-005078 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5018.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5018.c

Purpose: IPQ5018 TLMM pin controller description for the Qualcomm `pinctrl-msm` core. It does not implement GPIO logic itself; it declares the SoC pin, function, group, register-bit, and OF-match data consumed by `msm_pinctrl_probe()`.

Important APIs, types, and tables: `PINGROUP()` builds `struct msm_pingroup` entries with one GPIO group, 10 mux slots, 0x1000 register stride, mux bit 2, pull bit 0, drive bit 6, OE bit 9, input/output value bits 0/1, and two-bit interrupt detection. `ipq5018_pins[]` exposes GPIO 0-46, `DECLARE_MSM_GPIO_PINS()` creates one-pin arrays, `enum ipq5018_functions` assigns `msm_mux_*` IDs, function group arrays list legal pins, `ipq5018_functions[]` maps names through `MSM_PIN_FUNCTION()`/`MSM_GPIO_PIN_FUNCTION()`, and `ipq5018_groups[]` contains 47 pingroups. `ipq5018_pinctrl` reports 47 GPIOs.

Control flow: `arch_initcall(ipq5018_pinctrl_init)` registers `ipq5018_pinctrl_driver`. OF matching on `qcom,ipq5018-tlmm` invokes `ipq5018_pinctrl_probe()`, which delegates all setup to `msm_pinctrl_probe(pdev, &ipq5018_pinctrl)`. Module exit unregisters the platform driver.

State and persistence: all SoC metadata is static const data. Runtime pin state, GPIO state, IRQ handling, and register writes live in the common `pinctrl-msm` implementation and TLMM hardware registers, not in this file.

Dependencies and integration: depends on Linux platform/OF module infrastructure and `pinctrl-msm.h`. Device trees must use the compatible string and mux function names declared here. The table integrates BLSP, QSPI/SDC1, PCIe wake/clock, audio, MDIO/MDC, PWM, QDSS, LED, EUD, WCI/XFEM, and related TLMM functions.

Risks: table-only drivers are sensitive to off-by-one GPIO counts, wrong mux enum ordering, wrong group membership, and mismatched register bit definitions. Pins with repeated or alternative audio/QDSS functions need board-level validation because the common core trusts these tables. No reserved GPIO list is present, so ownership restrictions must come from DT or consumers.

Test signals: build coverage should catch missing enum/function/group symbols. Runtime signals include successful probe for `qcom,ipq5018-tlmm`, pinctrl debugfs listing 47 GPIO groups, GPIO direction/value changes through gpiolib, interrupt delivery on TLMM GPIOs, and peripheral smoke tests for BLSP, PCIe wake, QSPI/SDC1, MDIO/MDC, audio, PWM, and QDSS routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5018.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5210.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5210.c

Purpose: IPQ5210 TLMM pinctrl data driver. It publishes 54 GPIO pins and their mux alternatives to the shared Qualcomm MSM pinctrl core.

Important APIs, types, and tables: `PINGROUP()` creates `struct msm_pingroup` rows with the modern 0x1000-per-GPIO register layout and standard TLMM bit assignments. `ipq5210_pins[]` covers GPIO 0-53. The function enum and `ipq5210_functions[]` expose PON/GPN optics signals, QUP serial engines, audio primary/secondary clocks, PCIe, QSPI/SDC, PWM, QRNG, QDSS, MDIO/MDC master/slave lanes, LEDs, PPS, and test outputs. Group arrays define the legal pins per function, including broad `gpio_groups[]`. `ipq5210_groups[]` has indexed entries `[0]` through `[53]`, and `ipq5210_tlmm` sets `.ngpios = 54`.

Control flow: `arch_initcall(ipq5210_tlmm_init)` registers the platform driver named `ipq5210-tlmm`. A matching device tree node with `qcom,ipq5210-tlmm` calls `ipq5210_tlmm_probe()`, which passes `ipq5210_tlmm` to `msm_pinctrl_probe()`. Removal is the generic platform-driver unregister path through `module_exit()`.

State and persistence: no mutable driver-private state is defined here. Static mux and register metadata persist for the module lifetime; runtime state is in common pinctrl/gpio/irq data and TLMM registers.

Dependencies and integration: includes `<linux/of.h>`, `<linux/platform_device.h>`, and `pinctrl-msm.h`. It integrates with pinctrl DT bindings, gpiolib, and the msm TLMM IRQ path. Board DTS must choose function names from the table and respect pins with empty mux alternatives.

Risks: optical/PON and QUP mappings are dense and easy to misroute if DT uses a legal function on the wrong physical board pin. The table contains explicit empty pingroups such as 24, 25, 29, and 32, so consumers should not assume every GPIO supports a peripheral mux. Incorrect `.nfuncs = 10` or mux ordering would program the wrong function field without local validation.

Test signals: compile and module alias generation; boot log probe for `qcom,ipq5210-tlmm`; pinctrl debugfs reports 54 groups and expected functions; GPIO line direction/value tests; interrupt tests on representative pins; peripheral validation for QUP SE0-SE5, PON/GPN loss/tx signals, QSPI/SDC, PCIe wake/clock request, MDIO/MDC, PWM/LED, PPS, and QDSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5332.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5332.c

Purpose: IPQ5332 TLMM pinctrl description for the shared MSM pinctrl driver. The file is static SoC data for GPIO muxing, GPIO mode, pin configuration, and GPIO IRQ register layout.

Important APIs, types, and tables: `PINGROUP()` defines 10 mux slots per GPIO and modern TLMM offsets: control at `REG_SIZE * id`, IO at `+0x4`, interrupt config/status at `+0x8/+0xc`, mux/pull/drive/OE bits at 2/0/6/9, and two-bit detection. `ipq5332_pins[]` and matching `gpioN_pins[]` describe GPIO 0-52. The function enum and `ipq5332_functions[]` cover BLSP, audio primary/secondary, PCIe0-2, QSPI/SDC, MDIO/MDC, PWM, QDSS A/B, WCI/WSI, PTA, MAC, core voltage, TRNG/PRNG, and test/debug functions. `ipq5332_groups[]` has 53 pingroups and `ipq5332_pinctrl` sets `.ngpios = 53`.

Control flow: `ipq5332_pinctrl_init()` is registered as an `arch_initcall`, making TLMM available early. The platform driver matches `qcom,ipq5332-tlmm`; probe calls `msm_pinctrl_probe()` with the static SoC data.

State and persistence: the file stores no runtime state. Persistent hardware effects are register writes performed by the common core when consumers request mux/config/IRQ operations. The static arrays must remain valid for the driver lifetime.

Dependencies and integration: uses `pinctrl-msm.h` macros and `struct msm_pinctrl_soc_data`. It is consumed by device tree pinctrl states and GPIO users, and indirectly by interrupt consumers through the common TLMM irqchip support.

Risks: IPQ5332 has many overlapping mux choices on audio, BLSP, PCIe, and QDSS pins; wrong mux slot order can silently select a different peripheral. GPIO 43 has a ninth-slot `gcc_plltest`, making it an example where late mux positions matter. Empty placeholders `_` rely on the `msm_mux__` sentinel being valid in the common core.

Test signals: successful kernel build, module OF table for `qcom,ipq5332-tlmm`, probe without resource errors, pinctrl debugfs showing 53 GPIOs, gpiolib line tests, IRQ edge/level tests, and board smoke tests for PCIe0-2 wake/clock pins, QSPI/SDC, BLSP buses, MDIO/MDC, audio, WCI/WSI, PWM, and QDSS trace/CTI pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5332.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5424.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5424.c

Purpose: IPQ5424 TLMM static pinctrl table for the Qualcomm MSM pinctrl core. It maps 50 GPIOs to serial, PCIe, audio, QSPI/SDC, debug, test, WCI, and QDSS functions.

Important APIs, types, and tables: `PINGROUP()` uses the modern 0x1000 register stride and standard TLMM bit positions. `ipq5424_pins[]` lists GPIO 0-49 and `DECLARE_MSM_GPIO_PINS()` creates one-pin group arrays. The function enum and `ipq5424_functions[]` include I2C/SPI/UART names, PTA functions with uppercase identifiers, PCIe0-3, MDIO/MDC master/slave, audio primary/secondary, CXC, WCI, QDSS, PWM, QSPI, SDC, and test functions. `ipq5424_groups[]` has 50 entries, with several intentionally blank GPIOs. `ipq5424_pinctrl` advertises `.ngpios = 50`.

Control flow: the platform driver is registered at `arch_initcall`. A DT node compatible with `qcom,ipq5424-tlmm` triggers `ipq5424_pinctrl_probe()`, which delegates to `msm_pinctrl_probe()`.

State and persistence: no local mutable state. Static metadata persists in the module image; actual mux/config state persists in TLMM registers and common `pinctrl-msm` objects.

Dependencies and integration: depends on Linux OF/platform driver APIs and `pinctrl-msm.h`. Integration is through device-tree pinctrl states naming the functions/groups here, gpiolib line registration, and TLMM GPIO IRQ support from the common core.

Risks: this newer table mixes regular lowercase function names with uppercase `PTA0_0`, `PTA0_1`, `PTA0_2`, `PTA10`, and `PTA11`, so DT binding/name matching must be checked carefully. Multiple blank/reserved-looking GPIOs still appear in `.ngpios`; consumers can request them as GPIO unless constrained externally. PCIe0-3 and audio duplicate function alternatives increase the chance of board DTS selecting the wrong pad.

Test signals: kernel build catches enum/function inconsistencies; probe for `qcom,ipq5424-tlmm`; debugfs shows 50 groups; GPIO direction/value and IRQ tests; peripheral tests for SPI0/SPI1/SPI10/SPI11, UART0/1, I2C, PCIe0-3 wake/clock, MDIO/MDC, QSPI/SDC, audio, PWM, WCI, and QDSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq5424.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq6018.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq6018.c

Purpose: IPQ6018 pinctrl/TLMM SoC description for 80 GPIOs. It lets the common MSM pinctrl driver expose GPIO, mux, pinconf, and GPIO IRQ services for IPQ6018 boards.

Important APIs, types, and tables: `PINGROUP()` describes a 0x1000-per-GPIO register map with 10 mux choices and standard TLMM bit fields. `ipq6018_pins[]` covers GPIO 0-79. The function enum and generated `ipq6018_functions[]` include QPIC, WCI20-23, MAC variants, audio TX/RX and SoundWire, LPASS PCM/PDM/audio, BLSP0-5, PCIe0 reset/wake/clock, SD card/write protect, MDIO/MDC, PTA, PWM banks, PRNG/TRNG, QDSS A/B, and debug/test signals. `ipq6018_groups[]` has 80 entries; `ipq6018_pinctrl` sets `.ngpios = 80`.

Control flow: `arch_initcall(ipq6018_pinctrl_init)` registers `ipq6018-pinctrl`. Matching `qcom,ipq6018-pinctrl` invokes `ipq6018_pinctrl_probe()`, which calls the common `msm_pinctrl_probe()`.

State and persistence: all state in this file is static descriptor data. Runtime state and persistence are in TLMM registers and common msm pinctrl/gpio/irq data structures.

Dependencies and integration: uses OF/platform/module APIs and `pinctrl-msm.h`. It integrates with DT pin states for networking, QPIC flash, BLSP serial buses, LPASS/audio, PCIe, SD detect/write-protect, QDSS, and GPIO IRQ consumers.

Risks: large mux tables have high transcription risk. Several early GPIOs multiplex QPIC with MAC/WCI/QDSS, so wrong DTS states can disrupt boot media or networking. Audio/SoundWire pins require value-before-OE and mux sequencing from the common core; this file must provide correct mux slots. License string differs from SPDX (`GPL v2` vs `GPL-2.0`), which is conventional in older drivers but still worth preserving intentionally.

Test signals: compile coverage and module device table for `qcom,ipq6018-pinctrl`; boot probe; debugfs showing 80 GPIOs; QPIC boot/flash access, BLSP UART/I2C/SPI, PCIe0 reset/wake, SD card detect/write protect, MDIO/MDC, LPASS/audio, PWM, QDSS, GPIO value/direction, and representative GPIO interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq6018.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq8064.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq8064.c

Purpose: IPQ8064 pinctrl data driver for an older Qualcomm IPQ TLMM layout. It describes 69 GPIO-capable groups plus three SDC3-only pin groups.

Important APIs, types, and tables: unlike newer IPQ drivers, the file uses `IPQ_MUX_*` function IDs and a `PINGROUP()` with 0x10 GPIO register stride starting at control offset `0x1000`, IO `0x1004`, interrupt config/status `0x1008/0x100c`, and a separate interrupt target register at `0x400 + 0x4 * id`. Interrupt detection width is one bit and ack-high is enabled. `SDC_PINGROUP()` describes SDC3 clock/cmd/data groups with mux/OE/IRQ fields disabled. `ipq8064_pins[]` lists GPIO 0-68 plus SDC3_CLK/CMD/DATA pins 69-71, but `.ngpios = NUM_GPIO_PINGROUPS` limits GPIO registration to 69.

Control flow: `ipq8064_pinctrl_init()` registers the platform driver early. Matching `qcom,ipq8064-pinctrl` calls `ipq8064_pinctrl_probe()`, delegating to `msm_pinctrl_probe()`.

State and persistence: static const data only. Runtime hardware state persists in the older TLMM register block and common pinctrl/gpio/irq structures.

Dependencies and integration: uses `pinctrl-msm.h`, platform/OF APIs, and the common msm core. Function coverage includes GSBI buses, PCIe control pins, RGMII/MDIO, NAND/SDC1, SDC3 dedicated groups, USB FS/HSIC, TSIF, MI2S/audio, NSS SPI, SATA/SPDIF, SSBI/SPMI, PDM, and PS_HOLD.

Risks: this file is structurally different from the newer REG_SIZE drivers; copying modern offsets or interrupt width would break IPQ8064. SDC3 groups are not GPIOs and have disabled IRQ/OE fields, so generic code paths must respect negative bit positions. `.npins` is 72 while `.ngpios` is 69, which is intentional and should not be “fixed” casually.

Test signals: build and OF alias for `qcom,ipq8064-pinctrl`; debugfs should expose GPIO groups and SDC3 groups distinctly; GPIO and IRQ tests on GPIO 0-68; SDC3 pinconf validation; board tests for GSBI serial, NAND/SDC1/SDC3, PCIe control, MDIO/RGMII, USB, SATA/SPDIF, and PS_HOLD behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq8064.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq8074.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq8074.c

Purpose: IPQ8074 TLMM pinctrl table for 70 GPIOs, consumed by the common Qualcomm MSM pinctrl core.

Important APIs, types, and tables: `PINGROUP()` uses 0x1000 register stride and standard mux/pull/drive/OE/value/IRQ bit assignments with 10 mux slots. `ipq8074_pins[]` lists GPIO 0-69. The enum/function table includes QPIC, BLSP0-5, MAC address/sideband signals, WCI2A-D, PCM/audio, QDSS A/B, PCIe0/1 reset/wake/clock, LDO update/enable, SD card/write-protect, MDIO/MDC, PTA, PWM, PRNG/TRNG, CXC, LED, and test functions. `ipq8074_groups[]` maps all 70 pingroups and `ipq8074_pinctrl` sets `.ngpios = 70`.

Control flow: `arch_initcall(ipq8074_pinctrl_init)` registers the `ipq8074-pinctrl` platform driver. Device-tree compatible `qcom,ipq8074-pinctrl` selects this driver; probe delegates to `msm_pinctrl_probe()`.

State and persistence: static SoC data only. Pin ownership, mux state, interrupt state, and GPIO values are handled by common pinctrl/gpiolib/irqchip code and hardware registers.

Dependencies and integration: depends on `pinctrl-msm.h` and Linux OF/platform infrastructure. Integrates with board DTS pinctrl nodes for flash, serial, networking sideband, audio, PCIe, LED/PWM, QDSS, and GPIO interrupt consumers.

Risks: QPIC is present on many low GPIOs and overlaps with serial/WCI/MAC/QDSS functions, so DTS mistakes can affect storage or networking. Several function names use `NA` placeholders rather than `_`, so enum/table consistency with `IPQ_MUX_NA`/common handling is important. LDO update/enable pins on PCIe-adjacent groups should be validated on real hardware to avoid power sequencing regressions.

Test signals: build and module table; successful probe for `qcom,ipq8074-pinctrl`; debugfs reports 70 GPIOs; GPIO and IRQ tests; QPIC access, BLSP buses, PCIe0/1 reset/wake, MDIO/MDC, SD card/write protect, audio/PCM, LED/PWM, QDSS, MAC/WCI sideband, and LDO update/enable board tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq8074.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq9574.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq9574.c

Purpose: IPQ9574 TLMM static descriptor for 65 GPIOs, including a reserved GPIO entry for QFPROM LDO control.

Important APIs, types, and tables: `PINGROUP()` is the modern Qualcomm TLMM descriptor macro with 0x1000 stride and standard bit definitions. `ipq9574_pins[]` covers GPIO 0-64. The enum and `ipq9574_functions[]` cover SDC/QSPI, BLSP0-5, PCIe0-3, audio/PDM/WSA, QDSS A/B, MDIO/MDC, MAC, CXC, WCI, PTA/PWM, DDR PHY, TRNG/PRNG, and test/debug functions. `ipq9574_groups[]` maps 65 pingroups. `ipq9574_reserved_gpios[] = { 59, -1 }` marks GPIO59 reserved, and `ipq9574_pinctrl` passes that list to the common core.

Control flow: `arch_initcall(ipq9574_pinctrl_init)` registers the platform driver named `ipq9574-tlmm`. OF compatible `qcom,ipq9574-tlmm` probes through `ipq9574_pinctrl_probe()` and `msm_pinctrl_probe()`.

State and persistence: no local mutable state. Reserved GPIO metadata persists as static data; actual hardware state is maintained in TLMM registers and common core structures.

Dependencies and integration: uses Linux OF/platform/module support and `pinctrl-msm.h`. The reserved GPIO integration is important for the common core to deny or hide GPIO59 from generic consumers while keeping pin metadata available.

Risks: GPIO59 is reserved for QFPROM LDO regulator control; exposing or repurposing it can affect fuse/QFPROM operation. PCIe0-3, SDC/QSPI, audio, BLSP, and QDSS mappings overlap heavily, so DTS pinctrl states need board-level review. The common core trusts the sentinel-terminated reserved list; omitting `-1` would be unsafe.

Test signals: build and module OF table; probe on `qcom,ipq9574-tlmm`; debugfs/gpiolib should reflect 65 GPIO groups with GPIO59 reserved behavior; attempted GPIO59 consumer request should fail or be blocked as expected; GPIO/IRQ tests on non-reserved lines; board smoke for SDC/QSPI, BLSP, PCIe0-3, MDIO/MDC, audio/PDM/WSA, PWM/PTA/WCI, and QDSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq9574.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-kaanapali.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-kaanapali.c

Purpose: Kaanapali TLMM pinctrl data driver. It is a large static SoC descriptor for 218 GPIO-capable lines plus special UFS reset and SDC2/QDSD groups, with eGPIO and wake IRQ metadata.

Important APIs, types, and tables: `PINGROUP()` creates 12-function GPIO groups; slot 0 is GPIO and slot 11 is eGPIO, with `.egpio_enable = 12`, `.egpio_present = 11`, wakeup-present/enabled interrupt bits, and modern 0x1000 GPIO register stride. `SDC_QDSD_PINGROUP()` models non-GPIO SDC2 pins with disabled mux/OE/IRQ fields. `UFS_RESET()` models a reset line with separate control and IO offsets. `kaanapali_pins[]` contains GPIO 0-216 plus `UFS_RESET`, `SDC2_CLK`, `SDC2_CMD`, and `SDC2_DATA`. `kaanapali_functions[]`, group arrays, and `kaanapali_groups[]` cover camera, QUP/I2C/SPI/UART, QSPI, SDC, UIM, USB, display sync, GNSS, DDR BIST/PXI, QDSS, qlink, coex UART, navigation GPIOs, phase flags, and extensive eGPIO groups. `kaanapali_pdc_map[]` maps many GPIOs to PDC wake IRQs. `kaanapali_tlmm` sets `.ngpios = 218`, wake map fields, and `.egpio_func = 11`.

Control flow: `arch_initcall(kaanapali_tlmm_init)` registers `kaanapali-tlmm`. Compatible `qcom,kaanapali-tlmm` probes through `msm_pinctrl_probe()` using `kaanapali_tlmm`.

State and persistence: this file is static descriptor data. eGPIO mode, wake IRQ routing, UFS reset, SDC pin settings, and regular mux/pinconf state persist in TLMM/PDC hardware and common driver objects.

Dependencies and integration: depends on `pinctrl-msm.h`, OF/platform APIs, and common msm support for wakeirq maps and eGPIO fields. It integrates with PDC wakeup, gpiolib, pinctrl DT states, and storage/display/camera/serial subsystems.

Risks: this is a high-blast-radius table: 221 pin descriptors, 217 GPIO pingroup entries, special UFS/SDC groups, and a long PDC map. Off-by-one errors around `.ngpios = 218` versus special groups 217-220 would break GPIO registration or special pinctrl groups. eGPIO slot position must remain aligned with `.egpio_func = 11`. Wake IRQ map mistakes cause suspend/resume failures that compile tests cannot catch.

Test signals: build and probe for `qcom,kaanapali-tlmm`; debugfs shows GPIO and special groups; eGPIO-capable lines can enter/leave eGPIO mode; wake-from-suspend tests on representative `kaanapali_pdc_map` entries; UFS reset and SDC2 pinconf validation; GPIO/IRQ tests; camera, QUP, QSPI, USB, UIM, display sync, qlink, GNSS/coex, and QDSS board tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-kaanapali.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-lpass-lpi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-lpass-lpi.c

Purpose: reusable Qualcomm LPASS LPI GPIO/pinctrl implementation. Unlike the IPQ TLMM files, this file contains active runtime logic for muxing, pinconf, GPIO operations, debugfs display, probe, and remove for LPASS low-power island pin controllers.

Important APIs, types, and functions: `struct lpi_pinctrl` stores device, pinctrl device, gpio chip, descriptor, TLMM/slew MMIO bases, two optional clocks (`core`, `audio`), a mutex, an `ever_gpio` bitmap, and variant data. `lpi_gpio_read()`/`lpi_gpio_write()` compute register offsets either by `LPI_TLMM_REG_OFFSET * pin` or predefined per-group offsets. `lpi_gpio_pinctrl_ops`, `lpi_gpio_pinmux_ops`, and `lpi_gpio_pinconf_ops` connect the implementation to pinctrl. `lpi_gpio_set_mux()` validates requested function membership, prevents first-GPIO-output glitches by mirroring input state to output, then writes the function field. `lpi_config_get()` and `lpi_config_set()` handle generic bias, input enable, output level, drive strength, and slew rate configs. GPIO callbacks wrap those pinconf helpers. `lpi_pinctrl_probe()` and `lpi_pinctrl_remove()` are exported for variant drivers.

Control flow: a variant platform driver matches DT and calls `lpi_pinctrl_probe()`. Probe allocates state, obtains match data, validates `npins <= MAX_NR_GPIO`, maps TLMM and optionally slew resources, enables optional clocks, fills pinctrl/gpio descriptors, registers pinctrl, creates one generic group per pin, then registers a sleeping gpiochip. Remove destroys the mutex, disables clocks, and removes generic groups.

State and persistence: runtime state includes enabled clocks, MMIO mappings, pinctrl/gpio registrations, mutex, and `ever_gpio` glitch-prevention bitmap. Hardware pin state persists in LPASS registers. Devm resources cover most cleanup; explicit remove handles clocks, mutex, and generic groups.

Dependencies and integration: uses bitfield helpers, clocks, gpiolib, pinctrl generic helpers, pinconf generic DT parsing, `pinctrl-utils`, and `pinctrl-lpass-lpi.h` variant data. Integrates with DT resources/clocks and variant-specific pin/function/group tables.

Risks: `lpi_config_set()` defaults drive strength to 2 mA and bias disable for every call, so partial config calls can rewrite fields unless consumers submit complete states. `LPI_GPIO_DS_TO_VAL(v)` assumes valid even mA strengths; unusual values can underflow or encode unexpected drive. Slew-rate register selection depends on variant flags. The `ever_gpio` bitmap caps variants at 32 pins. Concurrent register updates rely on the local mutex, but value-before-OE writes include an unlocked value register write before the config lock.

Test signals: build and symbol export coverage; probe with and without separate slew resource; optional clock enable/disable paths; DT pinconf parsing; mux membership rejection; GPIO direction/get/set; bias/drive/slew readback; first GPIO output transition without glitches; debugfs formatting; remove/unbind cleanup; suspend/resume or audio low-power island tests for clock and register retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-lpass-lpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-lpass-lpi.h -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-lpass-lpi.h

Purpose: public local header for LPASS LPI pinctrl variant drivers and the shared `pinctrl-lpass-lpi.c` implementation. It defines register offsets, masks, encoding helpers, table-construction macros, variant flags, data structures, and exported probe/remove prototypes.

Important APIs, types, and macros: register constants describe LPASS TLMM and slew registers: `LPI_GPIO_CFG_REG`, `LPI_GPIO_VALUE_REG`, pull/function/drive/OE/value masks, `LPI_SLEW_RATE_CTL_REG`, `LPI_SLEW_RATE_MASK`, and `LPI_TLMM_REG_OFFSET`. Bias constants encode disable, pull-down, keeper, and pull-up. `LPI_GPIO_DS_TO_VAL(v)` converts mA drive strength to hardware field value. `LPI_FUNCTION(fname)` creates `struct lpi_function` entries indexed by `LPI_MUX_*`. `LPI_PINGROUP()` and `LPI_PINGROUP_OFFSET()` create `struct lpi_pingroup` entries with GPIO plus four alternate muxes, optional slew offset, and optional predefined pin offset. `LPI_FLAG_SLEW_RATE_SAME_REG` and `LPI_FLAG_USE_PREDEFINED_PIN_OFFSET` control implementation behavior.

Control flow: the header itself has no runtime flow. Variant drivers include it to build static `pins`, `groups`, and `functions` arrays, fill `struct lpi_pinctrl_variant_data`, and call `lpi_pinctrl_probe()`/`lpi_pinctrl_remove()` from their platform driver callbacks.

State and persistence: no mutable state. The structures define immutable variant data consumed by the runtime implementation. Register constants define how persistent hardware state is encoded.

Dependencies and integration: includes `<linux/array_size.h>`, `<linux/bits.h>`, and `../core.h`, and forward-declares `platform_device` and `pinctrl_pin_desc`. It is tightly coupled to `pinctrl-lpass-lpi.c` and to LPASS variant files that define `LPI_MUX_*` enums and group arrays matching these macros.

Risks: macro-generated arrays rely on enum names and group arrays being present and correctly ordered. `LPI_PINGROUP()` fixes `.nfuncs = 5`; variants needing more mux options require a header change. `LPI_GPIO_DS_TO_VAL(v)` has no local validation and assumes implementation-side constraints. Flag misuse can make register offsets wrong or make the implementation require a missing slew resource.

Test signals: compile coverage from all LPASS LPI variant drivers; sparse/build warnings for pointer types; probe tests for variants with same-register slew and separate slew resources; pinconf read/write tests validating masks and drive/slew encodings; mux tests confirming `LPI_FUNCTION()` indices match `LPI_MUX_*` enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-lpass-lpi.h -->
