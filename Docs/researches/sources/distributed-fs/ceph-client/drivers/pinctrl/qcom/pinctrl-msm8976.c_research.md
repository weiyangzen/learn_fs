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
