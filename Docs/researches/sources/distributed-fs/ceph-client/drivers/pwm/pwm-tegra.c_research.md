# sources/distributed-fs/ceph-client/drivers/pwm/pwm-tegra.c

## Purpose

`pwm-tegra.c` drives NVIDIA Tegra PWM controllers. Tegra20 has four channels sharing a clock; Tegra186/Tegra194 expose one channel and can adjust clock rate through OPP. Registers contain enable, 8-bit duty, and 13-bit scale.

## APIs, control flow, and state

`struct tegra_pwm_chip` stores clock, reset, cached clock rate, min period, MMIO, and SoC data. `tegra_pwm_config()` rounds duty to 8-bit units, enforces min period, sets OPP rate for one-channel variants, computes scale, resumes runtime PM for register writes, and writes the channel register. Enable/disable set `PWM_ENABLE` and manage runtime PM. Runtime PM gates clock and pinctrl states.

Cached clock rate/min period are software state; active outputs hold runtime PM refs.

## Dependencies and integration points

The driver depends on Tegra OPP helpers, runtime PM, pinctrl PM states, reset controls, clocks, OF match data, and the PWM core.

## Risks and test signals

Live reconfiguration and disable are abrupt. Duty greater than period is not explicitly clamped before shifting. No `.get_state` exists. Test all SoC variants, OPP rate selection, min-period rejection, runtime PM/pinctrl, reset handling, and duty boundary inputs.
