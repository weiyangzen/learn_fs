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
