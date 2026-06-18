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
