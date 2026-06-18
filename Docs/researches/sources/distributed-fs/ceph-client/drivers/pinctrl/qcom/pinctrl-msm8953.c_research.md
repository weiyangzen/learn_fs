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
