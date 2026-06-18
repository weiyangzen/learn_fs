# subset-b-005077 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-apq8064.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-apq8064.c

## Purpose
Describes the Qualcomm APQ8064 TLMM pin controller for the shared `pinctrl-msm` core. The file is almost entirely static SoC data: 90 GPIO pins, six SD-card pins, function names/group membership, register offsets, bit positions, and the OF platform-driver binding for `qcom,apq8064-pinctrl`.

## Important APIs, Types, and Functions
The important data objects are `apq8064_pins[]`, `enum apq8064_functions`, the many `*_groups[]` function-to-group lists, `apq8064_functions[]`, `apq8064_groups[]`, and `apq8064_pinctrl`. `PINGROUP()` builds each GPIO `struct msm_pingroup` with APQ mux function IDs, `0x1000 + 0x10 * id`-style register spacing, and interrupt target programming. `SDC_PINGROUP()` describes non-GPIO SDC1/SDC3 clock, command, and data groups with no mux or interrupt support. `apq8064_pinctrl_probe()` delegates to `msm_pinctrl_probe()`.

## Control Flow
`arch_initcall(apq8064_pinctrl_init)` registers a platform driver early. Device-tree matching on `qcom,apq8064-pinctrl` calls probe, and probe passes `apq8064_pinctrl` to the common Qualcomm MSM pinctrl implementation. Runtime pinctrl, pinmux, pinconf, GPIO, and IRQ operations are implemented by the common core using the static tables in this file.

## State and Persistence Behavior
The file owns no mutable runtime state. The static pin/function/group tables persist for the lifetime of the kernel image. Pin state persists in TLMM hardware registers after the common core writes mux, pull, drive, output, and interrupt bits. The SD-card groups deliberately disable unsupported GPIO and IRQ fields with `-1` bit positions.

## Dependencies and Integration Points
Depends on `linux/module.h`, OF/platform-driver support, and `pinctrl-msm.h`. It integrates with APQ8064 board device trees, the Linux pinctrl and gpiolib/irqchip paths exposed by `pinctrl-msm`, APQ GSBI/I2C/SPI/UART functions, HDMI, Riva wireless functions, TSIF, Slimbus, MI2S, USB HSIC, and SDC consumers.

## Risks
Primary risk is table correctness. Mux function ordering in `PINGROUP()` is the hardware selector value, so reordering `enum apq8064_functions` or a group's function list can configure the wrong peripheral. Register offsets differ from newer 0x1000-per-GPIO layouts and include separate interrupt target registers, so copying newer macros into this file would break IRQ routing. SDC groups are not GPIOs; exposing them as normal GPIO/IRQ groups would be wrong.

## Test Signals
Useful signals include successful probe for `qcom,apq8064-pinctrl`, 96 pin descriptors with 90 GPIOs exposed, expected pin names/groups in pinctrl debugfs, APQ8064 board DT states applying for GSBI, HDMI, SDC, and Riva functions, GPIO IRQ routing to KPSS, and no invalid group/function errors during boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-apq8064.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-apq8084.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-apq8084.c

## Purpose
Provides the APQ8084 TLMM SoC description for the shared Qualcomm MSM pinctrl driver. It covers 147 GPIO-capable groups plus six dedicated SDC1/SDC2 pins and exposes a large APQ8084 function set for BLSP, camera, HDMI/eDP, PCIe, SATA, audio, SD, and debug pins.

## Important APIs, Types, and Functions
Key objects are `apq8084_pins[]`, `enum apq8084_functions`, function group arrays such as `blsp_i2c*_groups`, `cci_*_groups`, `hdmi_*_groups`, `pci_*_groups`, `sdc*_groups`, `apq8084_functions[]`, `apq8084_groups[]`, and `apq8084_pinctrl`. `PINGROUP()` emits each GPIO `struct msm_pingroup` with eight possible alternate-function slots, standard mux/pull/drive/output bits, IRQ bits, and `0x1000 + 0x10 * id` register spacing. `SDC_PINGROUP()` describes SDC1 and SDC2 control registers without GPIO or interrupt semantics.

## Control Flow
The driver registers at `arch_initcall()` time. When OF creates a platform device compatible with `qcom,apq8084-pinctrl`, `apq8084_pinctrl_probe()` calls `msm_pinctrl_probe(pdev, &apq8084_pinctrl)`. All dynamic behavior is then handled by the common Qualcomm pinctrl core.

## State and Persistence Behavior
This file has only static const-like SoC description data. The common core allocates runtime driver state and writes hardware registers when clients select pin states or use GPIO/IRQ APIs. The `.ngpios = NUM_GPIO_PINGROUPS` value intentionally exposes only the first 147 groups as GPIOs; the SDC entries remain pinctrl-only groups for pull/drive configuration.

## Dependencies and Integration Points
Depends on the generic pinctrl framework through `pinctrl-msm.h`, OF matching, and platform-driver registration. Integration points include APQ8084 device-tree pinctrl nodes and peripheral drivers for BLSP UART/I2C/SPI/UIM, camera CCI and MCLK, HDMI/eDP, PCIe, SATA, SD/eMMC, MI2S/Slimbus/SPDIF, HSIC, GCC clocks, and miscellaneous test/debug functions.

## Risks
The APQ8084 table is dense and selector-sensitive. Incorrect enum values, missing `NA` placeholders, wrong group names, or bad SDC register offsets can silently program unrelated pins. Because the GPIO register stride and interrupt fields are encoded in macros, macro drift from other Qualcomm TLMM generations is a common maintenance hazard. GPIO count must remain 147 so the six SDC pins are not exported as GPIO lines.

## Test Signals
Probe should bind to `qcom,apq8084-pinctrl`, debugfs should show 153 pins and 147 GPIO groups, and DT pin states should resolve for BLSP1-12, camera CCI/MCLK, display, PCIe/SATA, SDC1/2/3/4, and audio groups. Functional testing should include GPIO IRQs, drive/pull changes on SDC pins, and peripheral boot logs free of pinctrl lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-apq8084.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-eliza.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-eliza.c

## Purpose
Defines the QTI Eliza TLMM pin controller data for the shared MSM pinctrl core. It describes 186 pins/groups, including a UFS reset group, eGPIO-capable GPIO muxing, PDC wake interrupt mapping, and a modern 0x1000-per-GPIO register layout.

## Important APIs, Types, and Functions
Important objects include `eliza_pins[]`, per-GPIO pin arrays created by `DECLARE_MSM_GPIO_PINS`, `enum eliza_functions`, function group arrays, `eliza_functions[]`, `eliza_groups[]`, `eliza_pdc_map[]`, and `eliza_tlmm`. `PINGROUP()` provides 12 function slots: GPIO mode, ten named TLMM mux slots, and an eGPIO slot. It also records `egpio_present`, `egpio_enable`, wakeup bits, interrupt target value `3`, and per-group register offsets computed from `REG_SIZE * id`. `UFS_RESET()` models the reset pin as a non-interrupt group with output control only. `eliza_tlmm_probe()` calls `msm_pinctrl_probe()`.

## Control Flow
`arch_initcall(eliza_tlmm_init)` registers the `eliza-tlmm` platform driver. OF matching on `qcom,eliza-tlmm` invokes probe, which hands the static `eliza_tlmm` data to the common driver. The common driver then parses device-tree pin states and uses the group metadata to service pinmux, pinconf, GPIO, IRQ, wakeirq, and eGPIO requests.

## State and Persistence Behavior
No local mutable state is maintained. Persistent data is the static pin/function/group table and PDC wake map. Runtime state lives in the common MSM pinctrl device structures and in TLMM/PDC hardware registers. `.egpio_func = 11` marks the virtual eGPIO function number used by the common core to mux ownership away from TLMM when requested. The UFS reset group persists as hardware output state, not as a GPIO IRQ-capable line.

## Dependencies and Integration Points
Depends on `pinctrl-msm.h`, OF platform matching, the generic pinctrl framework, and the common Qualcomm GPIO/IRQ/wakeirq implementation. It integrates with Eliza board device trees, QUP serial engines, camera CCI/MCLK, display/HDMI/DP signals, PCIe clock requests, QSPI, UIM, USB, SDC, QDSS trace/debug pins, PDC wake interrupts, and UFS reset control.

## Risks
Function selector ordering is critical because `PINGROUP()` encodes hardware mux values by array index. eGPIO is represented as a virtual mux state, so `.egpio_func`, `egpio_present`, and `egpio_enable` must stay aligned with the common core expectations. Wake-capable GPIOs depend on `eliza_pdc_map[]`; stale GPIO-to-PDC mappings can break suspend wake without obvious pinmux errors. Non-GPIO UFS reset must not be treated like a normal interrupt-capable GPIO.

## Test Signals
Expected signals are successful binding to `qcom,eliza-tlmm`, debugfs showing 186 pins/groups and eGPIO-capable functions, pinctrl state resolution for QUP/camera/display/PCIe/QSPI/UIM/USB/SDC users, working UFS reset toggling, GPIO IRQ routing including wake from suspend for entries in `eliza_pdc_map[]`, and no invalid function selector warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-eliza.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-glymur.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-glymur.c

## Purpose
Provides TLMM pinctrl data for QTI Glymur-family SoCs, including a Mahua variant that shares the pin/function/group tables but uses a different PDC wakeirq map. The file defines GPIO groups, UFS reset, SDC2 control groups, eGPIO support, and OF matching for both `qcom,glymur-tlmm` and `qcom,mahua-tlmm`.

## Important APIs, Types, and Functions
Core objects are `glymur_pins[]`, `enum glymur_functions`, function group arrays, `glymur_functions[]`, `glymur_groups[]`, `glymur_pdc_map[]`, `mahua_pdc_map[]`, `glymur_tlmm`, and `mahua_tlmm`. `PINGROUP()` records GPIO mux options, eGPIO bits, pull/drive/output fields, and IRQ/wakeup fields using `REG_SIZE * id` spacing. `SDC_QDSD_PINGROUP()` adds SDC2 clock, command, and data pinconf-only groups. `UFS_RESET()` adds an output-only UFS reset group. `glymur_tlmm_probe()` uses `of_device_get_match_data()` so the matching compatible chooses the correct `struct msm_pinctrl_soc_data`.

## Control Flow
The platform driver registers during `arch_initcall()`. On probe, the OF match entry supplies either `glymur_tlmm` or `mahua_tlmm`; a missing match data pointer returns `-ENODEV`. Valid probe data is passed to `msm_pinctrl_probe()`, after which common MSM code handles runtime pinctrl, GPIO, IRQ, wakeirq, and eGPIO behavior.

## State and Persistence Behavior
The file has no writable private state. Static tables persist in kernel memory, while actual pin state persists in TLMM registers and PDC wake routing. Glymur and Mahua share all pin and mux metadata but intentionally differ in wakeirq mappings, so wake state behavior is variant-specific despite a common group table. `.egpio_func = 11` identifies the virtual eGPIO function slot.

## Dependencies and Integration Points
Depends on OF match data, platform-driver registration, `pinctrl-msm.h`, and the common Qualcomm pinctrl implementation. It integrates with board DT compatibles, QUP serial engines, camera/CCI, display/eDP, audio I2S, PCIe, QSPI, USB debug/PHY sideband pins, SDC2, UFS reset, QDSS trace, WCN switch controls, PDC wake interrupts, and GPIO consumers.

## Risks
The dual-compatible design makes wakeirq-map selection the highest-risk area: using the Glymur map on Mahua or vice versa can produce broken or wrong wake sources while normal GPIO use still works. Table index drift is also hazardous because `eliza`/`hawi`-style eGPIO slot assumptions are reused here. The `.ngpios = 251` value excludes the UFS and SDC-only groups from GPIO export; changing it would misrepresent non-GPIO groups. The file contains many `msm_mux__` placeholder uses, so generated names and placeholder enum entries must remain consistent.

## Test Signals
Test both compatibles. Probe should pick non-null match data, debugfs should expose the expected GPIO count plus UFS/SDC pinctrl-only groups, and DT states should resolve for QUP, display, camera, PCIe, USB, QSPI, SDC2, and UFS reset. Suspend/resume wake testing should cover GPIOs present in both `glymur_pdc_map[]` and `mahua_pdc_map[]`, especially entries that differ between variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-glymur.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-hawi.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-hawi.c

## Purpose
Defines the QTI Hawi TLMM SoC description for the common Qualcomm MSM pinctrl driver. It describes 227 GPIO-capable lines plus UFS reset and three SDC2 control groups, with modern eGPIO and PDC wakeirq support.

## Important APIs, Types, and Functions
Key objects are `hawi_pins[]`, `enum hawi_functions`, the function group arrays, `hawi_functions[]`, `hawi_groups[]`, `hawi_pdc_map[]`, and `hawi_tlmm`. `PINGROUP()` creates GPIO groups with 12 function slots, 0x1000 register spacing, mux/pull/drive/output fields, eGPIO present/enable fields, and IRQ/wakeup routing fields. `UFS_RESET()` models the UFS reset output group. `SDC_QDSD_PINGROUP()` creates SDC2 clock, command, and data pinconf-only groups. `hawi_tlmm_probe()` delegates to `msm_pinctrl_probe()`.

## Control Flow
`arch_initcall(hawi_tlmm_init)` registers the platform driver. OF matching on `qcom,hawi-tlmm` invokes probe, which passes `hawi_tlmm` to the common pinctrl implementation. Runtime mux/config/GPIO/IRQ operations are driven by device-tree pinctrl states and common `pinctrl-msm` callbacks using Hawi's static metadata.

## State and Persistence Behavior
The file contains only static tables and no local mutable state. Pin configuration, GPIO output, interrupt, wakeup, UFS reset, and eGPIO ownership state persist in hardware registers managed by the common core. `.ngpios = 227` exposes only real GPIO pingroups; UFS and SDC2 groups remain pinctrl-only.

## Dependencies and Integration Points
Depends on platform-driver/OF support and `pinctrl-msm.h`. It integrates with Hawi device trees, QUP and I2C hub serial engines, camera CCI/MCLK, DP/display sync, PCIe clock/reset pins, QSPI, UIM, USB, navigation/RFFE/coexistence pins, SDC2, UFS reset, QDSS/debug pins, PDC wake IRQs, and Linux GPIO consumers.

## Risks
Hawi's dense function table contains many similarly named split functions, such as QUP lane variants and display sync outputs; wrong group membership or enum ordering would be hard to diagnose at runtime. PDC wake mapping must match silicon and board wiring. The UFS reset and SDC groups use reduced capability macros, so generic GPIO assumptions would be incorrect. eGPIO selector value `11` must remain synchronized with the final function slot in `PINGROUP()`.

## Test Signals
Validate successful probe for `qcom,hawi-tlmm`, expected pin and GPIO counts in debugfs, DT pinctrl selection for QUP/I2C hub, camera, DP/display, PCIe, QSPI, UIM, USB, SDC2, and UFS reset, GPIO IRQ operation, and suspend wake for GPIOs in `hawi_pdc_map[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-hawi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq4019.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq4019.c

## Purpose
Describes the Qualcomm IPQ4019/QCA TLMM pin controller for the common MSM pinctrl core. It exposes 100 GPIO pins and their alternate functions for networking-oriented IPQ4019 peripherals such as BLSP, Ethernet, Wi-Fi, LED, QPIC, SDIO, JTAG, I2S, and PCIe.

## Important APIs, Types, and Functions
Important data includes `ipq4019_pins[]`, per-pin arrays from `DECLARE_QCA_GPIO_PINS`, `enum ipq4019_functions`, the function group arrays, `ipq4019_functions[]`, `ipq4019_groups[]`, and `ipq4019_pinctrl`. `PINGROUP()` creates each `struct msm_pingroup` with 15 function slots, 0x1000-per-pin register spacing, open-drain bit `12`, mux/pull/drive/output fields, and two-bit interrupt detection. `QCA_PIN_FUNCTION()` maps function enum values to group lists. `ipq4019_pinctrl_probe()` calls `msm_pinctrl_probe()`.

## Control Flow
At `arch_initcall()` time the platform driver is registered. A device-tree node compatible with `qcom,ipq4019-pinctrl` probes through `ipq4019_pinctrl_probe()`, which hands `ipq4019_pinctrl` to the common Qualcomm driver. The common core then provides the runtime pinmux, pinconf, GPIO, and IRQ behavior.

## State and Persistence Behavior
No driver-local mutable state exists. Static tables persist in kernel memory; runtime pin configuration and interrupt state persist in TLMM registers. `.ngpios = 100` exposes all listed pins as GPIOs. `.pull_no_keeper = true` tells the common core this SoC lacks keeper-bias support, changing how generic pinconf bias requests are interpreted.

## Dependencies and Integration Points
Depends on `pinctrl-msm.h`, platform-device and OF infrastructure, generic pinctrl, GPIO, and IRQ support. It integrates with IPQ4019 board DTs and consumers for MDIO/MDC, RGMII/RMII, Wi-Fi control pins, BLSP I2C/SPI/UART, LED functions, QPIC NAND, SDIO, I2S/SPDIF/audio PWM, JTAG, PCIe, PMU, PRNG ROSC, and test-monitor functions.

## Risks
Many high-numbered pins are present but have only `NA` functions, so accidental function assignment can expose unsupported muxes. `pull_no_keeper = true` is SoC-specific and must not be removed if generic bias keeper requests are invalid in hardware. Open-drain bit support is encoded in the IPQ-specific macro and differs from some APQ/MSM files. As in other table-driven Qualcomm pinctrl drivers, enum and function-list ordering directly affect hardware selector values.

## Test Signals
Expected signals include binding to `qcom,ipq4019-pinctrl`, 100 pins/GPIOs in debugfs, correct muxing for Ethernet, Wi-Fi, BLSP, LED, QPIC, SDIO, JTAG, and I2S groups, GPIO IRQ tests including dual-edge detection, open-drain behavior on relevant pins, and no keeper-bias configuration errors from board DT pin states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-ipq4019.c -->
