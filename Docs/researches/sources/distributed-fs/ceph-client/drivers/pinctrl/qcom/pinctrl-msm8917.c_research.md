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
