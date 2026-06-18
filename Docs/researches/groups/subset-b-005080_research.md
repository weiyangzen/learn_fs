# Research: subset-b-005080

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8916.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8916.c

## Purpose
This file is the Qualcomm MSM8916 TLMM pin controller description. It does not implement a new pinctrl algorithm; it supplies the common `pinctrl-msm` core with the MSM8916 pin list, mux-function catalog, function-to-group mappings, per-group register offsets/bit fields, GPIO count, and OF/platform-driver binding for `qcom,msm8916-pinctrl`. The described hardware covers 122 GPIO pingroups plus SDC1, SDC2, and QDSD non-GPIO pin groups.

## Important APIs, Types, And Functions
The main exported contract is `static const struct msm_pinctrl_soc_data msm8916_pinctrl`, which points at `msm8916_pins`, `msm8916_functions`, and `msm8916_groups`, and declares `.ngpios = NUM_GPIO_PINGROUPS` with `NUM_GPIO_PINGROUPS` equal to 122. `msm8916_pinctrl_probe()` delegates directly to `msm_pinctrl_probe(pdev, &msm8916_pinctrl)`. `msm8916_pinctrl_of_match` binds the compatible string, and `msm8916_pinctrl_driver` registers through an `arch_initcall`.

The file relies on the shared `pinctrl-msm.h` data types: `struct msm_pingroup` supplies group name/pins, mux selector list, GPIO control registers, interrupt registers, and bit positions; `struct msm_pinctrl_soc_data` is consumed by the common Qualcomm pinctrl, GPIO, and IRQ code. Local `PINGROUP()` rows describe each GPIO group with 10 mux choices including GPIO mode, register offsets at `0x1000 * id` plus fixed offsets for IO and interrupt registers, mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, and two-bit interrupt detection. `SDC_PINGROUP()` rows describe storage-card and QDSD pins with no GPIO/IRQ support and only pull/drive fields.

## Control Flow
At boot or module load, `msm8916_pinctrl_init()` registers the platform driver early. When device-tree matching creates a platform device, probe hands the immutable SoC table to the common core. From that point, all runtime behavior is in `pinctrl-msm.c`: pinctrl state selection indexes into `msm8916_functions` and the `funcs` arrays embedded in each `PINGROUP`; GPIO requests use the first 122 groups; IRQ setup uses each group's interrupt register offsets and detection/polarity bits; SDC and QDSD groups can be configured for bias/drive but have mux and interrupt fields disabled with `-1`.

## State And Persistence
This source file defines only static, read-only SoC description tables. It stores no runtime state, has no persistent storage, and performs no direct MMIO. Hardware state is created later by the common driver when clients apply pinctrl states or GPIO/IRQ operations. That hardware state persists in TLMM registers until another pinctrl operation, reset, or power transition rewrites it. The only lifetime action in this file is platform-driver registration and unregistration.

## Dependencies And Integration Points
The file depends on Linux module, OF, platform-device, and pinctrl infrastructure plus the local `pinctrl-msm` core. It integrates with device tree via `qcom,msm8916-pinctrl`, with board DTS pin states through function and group names such as BLSP I2C/SPI/UART, CCI/camera clocks, MI2S, codec, QDSS trace, SD write protect, WLAN/test, PMIC/power, SDC, and QDSD groups. It does not provide a wakeirq map, reserved GPIO list, tile list, or SoC-specific PM callbacks; the generic core defaults apply.

## Risks And Test Signals
Risk is concentrated in table correctness. A wrong function enum order, `MSM_PIN_FUNCTION()` table entry, or `PINGROUP()` mux position changes the numeric selector programmed into TLMM. Incorrect register offsets or bit positions can break GPIO direction, bias, drive strength, or IRQ routing across a whole bank. The `.ngpios` value must stay at 122 so the non-GPIO SDC/QDSD groups are not exposed as GPIOs. Test signals include successful probe from the compatible string, expected GPIO chip size of 122, DTS pinctrl states resolving every named function/group, BLSP and camera pins switching to non-GPIO modes, GPIO IRQ polarity/edge tests, and storage-card pull/drive configuration without GPIO exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8916.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8917.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8917.c

## Purpose
This file describes the Qualcomm MSM8917/MSM8937 TLMM pin controller for the common Qualcomm `pinctrl-msm` implementation. It enumerates 134 GPIO pingroups and 13 storage/QDSD pin groups, maps a large set of alternate functions onto those groups, and registers a platform driver matching `qcom,msm8917-pinctrl`.

## Important APIs, Types, And Functions
`msm8917_pinctrl` is the central `struct msm_pinctrl_soc_data`; it references 147 `PINCTRL_PIN()` descriptors, 163 function entries, all pingroups, and `.ngpios = 134`. `msm8917_pinctrl_probe()` is a thin wrapper over `msm_pinctrl_probe()`. `msm8917_pinctrl_of_match`, `MODULE_DEVICE_TABLE()`, and `msm8917_pinctrl_driver` provide OF autoloading and platform binding.

Local `PINGROUP()` entries build `struct msm_pingroup` records with 10 mux slots, GPIO control at `0x1000 * id`, IO at `+0x4`, interrupt config/status at `+0x8/+0xc`, mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, and KPSS interrupt target value 4. `SDC_PINGROUP()` covers SDC1 clock/command/data/rclk, SDC2, and QDSD pins by giving them pull/drive fields but disabling mux, GPIO, and IRQ fields. The function catalog includes BLSP1-8 I2C/SPI/UART/UIM, QDSS trace/CTI, CCI/camera controls, MI2S/audio, PMIC power lines, sensor interrupts, UIM/SIM, WLAN/coexistence, and manufacturing/test functions.

## Control Flow
`arch_initcall(msm8917_pinctrl_init)` registers the platform driver early. A matched device probes by passing the static SoC table to the common MSM pinctrl core. Pinctrl consumers later select named functions and groups from DTS; the core looks up the function's group list, finds the target `msm_pingroup`, then writes the mux selector index and electrical fields. GPIO and IRQ consumers are limited to the first 134 groups, while the trailing SDC/QDSD groups are available for pin configuration only.

## State And Persistence
All state in this file is immutable static data. Runtime state, locks, GPIO chips, irqdomains, and MMIO mappings are owned by `pinctrl-msm.c` after probe. The TLMM register contents produced from these tables persist in hardware until reset or another pinctrl/GPIO/IRQ operation changes them. No file-backed persistence or driver-private mutable state is present here.

## Dependencies And Integration Points
The driver depends on the Linux platform bus, OF matching, module metadata, and the shared Qualcomm pinctrl core. It integrates with MSM8917 and MSM8937 board device trees through `qcom,msm8917-pinctrl`; downstream device nodes depend on the exact group/function spelling. Because no wakeirq map, reserved GPIO array, tile data, or `pull_no_keeper` override is supplied, the common core uses baseline behavior for wake routing, GPIO exposure, and bias options.

## Risks And Test Signals
The dense mux table is the primary risk. MSM8917 has many reused BLSP, QDSS, PMIC, and test functions, so off-by-one enum/table mistakes can program the wrong alternate function while still compiling. The GPIO count must exclude SDC and QDSD groups. Register offsets assume one 4 KiB TLMM window per GPIO; a bad offset causes broad GPIO, IRQ, or bias failures. Test signals include probe and module alias matching, 134 exported GPIOs, successful resolution of SDC1 RCLK and QDSD groups, BLSP1-8 bus bring-up from DTS pinctrl states, GPIO interrupt tests for level and both-edge modes, and suspend/resume validation for pins expected to retain or restore TLMM state through the common core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8917.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8953.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8953.c

## Purpose
This file is the Qualcomm MSM8953 TLMM pin controller data provider. It describes the SoC's pins, mux functions, function group memberships, GPIO register layout, and SDC/QDSD electrical groups for the shared `pinctrl-msm` core, then registers an OF platform driver for `qcom,msm8953-pinctrl`.

## Important APIs, Types, And Functions
`msm8953_pinctrl` is the only SoC data object consumed outside the file. It contains 155 pin descriptors, 201 function entries, the full pingroup table, and `.ngpios = 142`. `msm8953_pinctrl_probe()` delegates to `msm_pinctrl_probe()`, while `msm8953_pinctrl_of_match` and `msm8953_pinctrl_driver` provide device-tree and platform-driver integration.

The `PINGROUP()` macro creates a `struct msm_pingroup` for each GPIO with GPIO mode plus nine alternate-function slots. GPIO control registers use `0x1000 * id`, IO is `+0x4`, interrupt configuration/status are `+0x8/+0xc`, mux selection starts at bit 2, pull at bit 0, drive at bit 6, and IRQ target routing uses KPSS value 4. `SDC_QDSD_PINGROUP()` describes QDSD, SDC1 including RCLK, and SDC2 groups with pull/drive controls and no mux/GPIO/IRQ bits. The function set is broad: BLSP I2C/SPI/UART variants, CCI and camera reset/standby/LDO controls, MI2S and codec signals, QDSS tracing, UIM/SIM, TSENS/test/DAC calibration, GP clocks, and power-management pins.

## Control Flow
The file's runtime path is intentionally small. `msm8953_pinctrl_init()` registers the platform driver via `arch_initcall`; probe passes the static table to the common Qualcomm driver. Later, pinctrl state changes, GPIO requests, and IRQ configuration are handled by `pinctrl-msm.c`, which interprets the MSM8953 table to choose groups, selector indexes, offsets, and bit positions. The non-GPIO storage/QDSD groups participate only in pin configuration paths because their mux and IRQ fields are disabled.

## State And Persistence
There is no mutable state in this source file. All arrays are static SoC description data. The common driver allocates and owns runtime pinctrl/GPIO/IRQ state after probe. Hardware register values derived from these tables are volatile TLMM state, not persisted by this file; they remain active until another driver operation or hardware reset modifies them.

## Dependencies And Integration Points
This driver depends on the Linux module, OF, platform-device, pinctrl, GPIO, and IRQ integration supplied by the common `pinctrl-msm` code. It is integrated through board DTS nodes compatible with `qcom,msm8953-pinctrl` and through consumer pinctrl states naming functions and groups. The file does not provide wakeirq, reserved GPIO, or tile metadata, so it relies on common defaults for those optional `struct msm_pinctrl_soc_data` fields.

## Risks And Test Signals
MSM8953 has the largest function table in this work item, so the risk profile is dominated by generated-data accuracy. Misordered function enums or `MSM_PIN_FUNCTION()` rows can silently remap DTS functions to wrong mux selector values. A wrong `.ngpios` value could expose SDC/QDSD groups as GPIOs or hide real GPIOs. Electrical bit positions for SDC/QDSD are fragile because those groups use compact shared registers rather than per-GPIO windows. Test signals include successful probe, 142 exported GPIOs, DTS function lookup for BLSP/camera/audio/QDSS states, interrupt handling on GPIO groups, SDC1 RCLK and QDSD pull/drive programming, and build coverage that catches missing group arrays for every function table entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8953.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8960.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8960.c

## Purpose
This file supplies the Qualcomm MSM8960 TLMM pin controller description to the shared MSM pinctrl core. It covers 152 GPIO pingroups plus six SDC1/SDC3 groups, exposes older MSM8960-era mux functions such as GSBI, PMIC bus, HDMI, HSIC, SD card, and audio/camera signals, and binds to `qcom,msm8960-pinctrl`.

## Important APIs, Types, And Functions
`msm8960_pinctrl` is the `struct msm_pinctrl_soc_data` instance used by the common core. It references 158 pins, 104 functions, `msm8960_groups`, and `.ngpios = NUM_GPIO_PINGROUPS` where the macro is 152. `msm8960_pinctrl_probe()` calls `msm_pinctrl_probe()`. The driver is registered by `msm8960_pinctrl_init()` through `arch_initcall` and removed by `msm8960_pinctrl_exit()`.

This file differs from newer 4 KiB-window TLMM descriptions. `PINGROUP()` has 12 mux slots and uses compact offsets: control at `0x1000 + 0x10 * id`, IO at `+0x4`, interrupt config at `+0x8`, status at `+0xc`, and a separate `.intr_target_reg = 0x400 + 0x4 * id`. The explicit target register matters because `struct msm_pingroup` otherwise defaults interrupt target routing to the interrupt config register. `SDC_PINGROUP()` disables mux/GPIO/IRQ fields and configures SDC pull/drive bits at compact offsets `0x20a0` and `0x20a4`.

## Control Flow
The platform driver is registered early. When OF matching finds `qcom,msm8960-pinctrl`, probe hands the SoC table to `pinctrl-msm.c`. Consumer pinctrl states resolve names such as GSBI buses, HDMI DDC/CEC/hotplug, HSIC, SDC2/4/5 alternate functions, MI2S/I2S, GP clocks/PDM, and camera clocks to function entries and GPIO groups. GPIO and IRQ operations apply only to the 152 GPIO pingroups; the SDC1/SDC3 groups are configured as non-GPIO electrical groups.

## State And Persistence
The source contains only static table data and no direct register writes. Runtime state is allocated by the common core after probe. TLMM register values, including the older separate interrupt-target registers, persist in hardware until changed by pinctrl/GPIO/IRQ operations or reset. The module registration state is transient and controlled by the platform-driver lifecycle.

## Dependencies And Integration Points
It depends on Linux OF/platform/module APIs, `linux/pinctrl/pinmux.h`, and the shared Qualcomm pinctrl implementation. Integration is through `qcom,msm8960-pinctrl` device-tree nodes and DTS pinctrl states using MSM8960-specific names. The explicit `.intr_target_reg` entries integrate with the common IRQ code path that supports older SoCs with separate interrupt-routing registers. No wakeirq map, reserved GPIO list, or tile data is supplied.

## Risks And Test Signals
The main risk is that MSM8960 uses a different register layout from the 8916/8917/8953/8976 style. Accidentally treating interrupt target routing as part of `intr_cfg_reg`, or changing the `0x10 * id` compact stride, would break GPIO IRQ routing broadly. The 12-entry mux arrays must match the enum and function table exactly. Test signals include probe with 152 GPIOs, GPIO IRQ routing to KPSS through `.intr_target_reg`, GSBI and HDMI pinctrl states working, SDC1/SDC3 pull/drive writes at the compact offsets, and regression builds that catch missing function group declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8976.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8976.c

## Purpose
This file is the Qualcomm MSM8976 TLMM pin controller description. It defines 145 GPIO pingroups and 13 SDC/QDSD groups, maps MSM8976-specific mux functions to those groups, and registers a platform driver for `qcom,msm8976-pinctrl` that delegates all behavior to the common `pinctrl-msm` core.

## Important APIs, Types, And Functions
`msm8976_pinctrl` is the central `struct msm_pinctrl_soc_data` with 158 pins, 95 functions, the group table, and `.ngpios = 145`. `msm8976_pinctrl_probe()` calls `msm_pinctrl_probe()`. `REG_BASE` and `REG_SIZE` make the GPIO register layout explicit: each `PINGROUP()` uses base plus `0x1000 * id`, with IO at `+0x4`, interrupt config/status at `+0x8/+0xc`, mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, and two-bit interrupt detection. `SDC_QDSD_PINGROUP()` covers SDC1 including RCLK, SDC2, and QDSD electrical-only groups.

The function table includes BLSP I2C/SPI/UART, QDSS trace and trace-control signals, GP clocks, CCI0/CCI1 I2C, camera clock, MI2S and slimbus audio, UIM, SD write protect, MIPI DSI, TSENS/touch-related pins, codec signals, WLAN/WCSS, and SDC3.

## Control Flow
The file registers its platform driver with `arch_initcall`. Probe is a single handoff to the shared MSM pinctrl implementation. At runtime, pinctrl state application selects a function and group by name, then the common core programs the mux selector index and pin configuration bits from the MSM8976 table. GPIO and IRQ users are constrained by `.ngpios = 145`; the trailing SDC/QDSD groups are reachable only through pin configuration paths with mux and interrupt fields disabled.

## State And Persistence
This file has no mutable state. It provides static arrays of pin, function, and group metadata. The common core maintains runtime pinctrl devices, GPIO chips, and IRQ domains. The actual TLMM state is hardware register state that survives until another operation or reset changes it; this file does not save or restore it directly.

## Dependencies And Integration Points
The driver depends on `pinctrl-msm.h`, the platform bus, OF matching, module infrastructure, and pinctrl/GPIO/IRQ handling in the common Qualcomm driver. It integrates with board device trees via `qcom,msm8976-pinctrl` and with consumers through function/group names. Optional `struct msm_pinctrl_soc_data` features such as wakeirq maps, tiles, reserved GPIOs, and custom GPIO function numbers are not used here.

## Risks And Test Signals
Because the file is table-driven, small data mistakes cause runtime hardware misconfiguration rather than local code failures. The function enum order must match `msm8976_functions` and each group's mux list. The `.ngpios` boundary must remain below the SDC/QDSD pin descriptors. QDSS and audio/camera functions share many pins, so DTS validation should cover real board states rather than compile-only checks. Test signals include successful probe, 145 exported GPIOs, BLSP, camera, audio, QDSS, UIM, and SDC pinctrl states resolving and programming expected registers, GPIO IRQ edge/level behavior, and storage/QDSD pull/drive configuration without GPIO exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8976.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8994.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8994.c

## Purpose
This file describes the Qualcomm MSM8994/MSM8992 TLMM pin controller for the shared `pinctrl-msm` core. It defines 146 GPIO pingroups, 10 SDC groups for SDC1/2/3, a 129-entry function table, and an OF platform driver matching both `qcom,msm8992-pinctrl` and `qcom,msm8994-pinctrl`.

## Important APIs, Types, And Functions
`msm8994_pinctrl` is the `struct msm_pinctrl_soc_data` consumed by `msm_pinctrl_probe()`. It references 156 pins, `msm8994_functions`, `msm8994_groups`, and `.ngpios = NUM_GPIO_PINGROUPS` with 146 GPIO groups. `msm8994_pinctrl_probe()` is the handoff to the common core; `msm8994_pinctrl_of_match` provides dual compatible support for MSM8992 and MSM8994; the platform driver is registered through `arch_initcall`.

Local `PINGROUP()` rows have 12 mux slots, compact per-GPIO offsets at `0x1000 + 0x10 * id`, IO/config/status offsets at `+0x4/+0x8/+0xc`, mux bit 2, pull bit 0, drive bit 6, output-enable bit 9, and KPSS interrupt target value 4. `SDC_PINGROUP()` rows cover SDC1 RCLK/CLK/CMD/DATA, SDC2, and SDC3 with electrical controls only. The function catalog includes BLSP I2C/SPI/UART/UIM instances 1-12, camera master clocks and CCI I2C, QDSS tracing/CTI, HDMI receive, MDP vsync, audio reference, TSIF, PCIe, modem/LTE/GSM, and other SoC integration signals.

## Control Flow
During early init, the driver registers with the platform bus. A matched device probes by passing `msm8994_pinctrl` to `pinctrl-msm.c`. Thereafter, the common core handles all pinctrl, GPIO, and IRQ operations using these tables. Consumer pinctrl states select group/function names from DTS; GPIO operations use groups 0-145; SDC groups participate only in pin configuration because mux and IRQ fields are disabled.

## State And Persistence
All state defined here is immutable table data. Runtime device state is in the common MSM pinctrl driver. TLMM hardware register values produced from the tables persist until later pinctrl/GPIO/IRQ writes or reset. The file does not keep software state across calls beyond platform-driver registration.

## Dependencies And Integration Points
The file depends on Linux module, OF, platform-device, and the local Qualcomm pinctrl core. It integrates through two compatible strings, allowing one data table to serve both MSM8992 and MSM8994 device trees. It does not specify wakeirq maps, reserved GPIOs, tiles, or special bias flags. Downstream integration is through exact function and group names in board DTS files, especially high-fanout BLSP and camera/QDSS/SDC functions.

## Risks And Test Signals
The shared MSM8992/MSM8994 compatible coverage increases the risk of SoC-variant mismatch if a board's TLMM differs from this table. The compact `0x10 * id` register stride differs from newer 4 KiB-per-GPIO descriptions, so offset mistakes can break whole GPIO ranges. Function selector ordering must stay synchronized across enum, function table, and each `PINGROUP()` mux list. Test signals include successful binding for both compatible strings, 146 exported GPIOs, BLSP1-12 pinctrl state coverage, camera and QDSS mux validation, SDC1/2/3 pull/drive programming, and GPIO IRQ routing/polarity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-msm8994.c -->
