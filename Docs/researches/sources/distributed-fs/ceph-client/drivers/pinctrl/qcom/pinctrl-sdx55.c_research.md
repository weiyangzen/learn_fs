# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-sdx55.c

## Purpose
Provides the Qualcomm SDX55 TLMM pin controller description for the shared `pinctrl-msm` driver. The file is almost entirely static SoC data: 108 GPIO pins, four SD/eMMC pseudo-pins, mux function names, function-to-group membership arrays, per-pin register layout, and the platform-driver binding for `qcom,sdx55-pinctrl`.

## Important APIs, Types, And Functions
`sdx55_pins[]` declares pins 0-107 plus `SDC1_RCLK`, `SDC1_CLK`, `SDC1_CMD`, and `SDC1_DATA`. `DECLARE_MSM_GPIO_PINS()` creates one-pin arrays consumed by `PINCTRL_PINGROUP`. `enum sdx55_functions` and `sdx55_functions[]` expose mux selectors through `FUNCTION(...)`. `PINGROUP()` fills `struct msm_pingroup` entries for normal GPIOs with a 0x1000 register stride and standard Qualcomm bit positions. `SDC_PINGROUP()` models SD controller pads with pull/drive fields but no mux, GPIO, or interrupt control. `sdx55_pinctrl` is the `struct msm_pinctrl_soc_data` passed to `msm_pinctrl_probe()`.

## Control Flow
At `arch_initcall`, `sdx55_pinctrl_init()` registers the platform driver. Device tree match creates a platform device, `sdx55_pinctrl_probe()` calls `msm_pinctrl_probe(pdev, &sdx55_pinctrl)`, and the shared driver registers pinctrl, pinmux, pinconf, GPIO, and IRQ handling from these tables. Runtime requests select a function by name, then the shared driver uses the group entry to program mux, pull, drive, output enable, value, and interrupt bits in the TLMM register block.

## State And Persistence
This file has no mutable local state. Persistent state is the hardware TLMM register content programmed by the common driver. The only durable contract here is the static mapping between Linux pin/group/function names and SDX55 register offsets. `ngpios = 108`, so pins 108-111 are non-GPIO SDC groups and are intentionally outside gpiolib.

## Dependencies And Integration Points
Depends on `pinctrl-msm.h`, Linux platform driver matching, and device-tree states referencing group/function names such as BLSP UART/I2C/SPI, UIM, QDSS, QLINK, SPMI, PCIe, EMAC PPS, TSENS, and SD controller pads. Interrupt fields target KPSS with value 3. Unlike later SDX parts, there is no wakeirq map in this file.

## Risks
The array has sparse designated entries: GPIO groups 0-107 and SDC entries 109-112, leaving index 108 empty even though `SDC1_RCLK` pin number is 108. That is intentional only if the shared core tolerates empty groups between valid entries. Wrong SDC offsets or pull/drive bit positions can silently break eMMC/SD signal integrity. Absence of a wake map means suspend wake support depends on other firmware paths or is unavailable. Because all pin mux alternatives are positional integer arrays, a mismatched function enum/order would program the wrong mux value.

## Test Signals
Useful signals are boot probe on `qcom,sdx55-pinctrl`, `/sys/kernel/debug/pinctrl` showing 112 pins and expected group/function names, GPIO loopback for pins below 108, interrupt trigger tests on TLMM-backed GPIOs, BLSP/UIM/QDSS/PCIe/EMAC pin-state application from device tree, and SD/eMMC operation with pull/drive changes. Source size reviewed: 1007 lines.
