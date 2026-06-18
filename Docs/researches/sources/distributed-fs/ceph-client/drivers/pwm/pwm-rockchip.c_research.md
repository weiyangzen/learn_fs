# sources/distributed-fs/ceph-client/drivers/pwm/pwm-rockchip.c

## Purpose

`pwm-rockchip.c` supports several Rockchip PWM register layouts through variant data. It exposes one PWM per instance and handles early RK2928, RK3288-style, VOP PWM, and RK3328 locked-update hardware.

## APIs, control flow, and state

`struct rockchip_pwm_data` supplies register offsets, prescaler, polarity support, lock support, and enable mask. `get_state()` enables APB and PWM clocks, reads period/duty/control, and reconstructs polarity. `rockchip_pwm_config()` computes 32-bit ticks, optionally locks updates, writes period/duty, adjusts polarity, and unlocks. `rockchip_pwm_apply()` enables clocks, reads current state, disables for live polarity changes on non-locking variants, configures, toggles enable, then disables temporary clocks.

Hardware registers are the source of truth; active outputs keep the functional clock enabled.

## Dependencies and integration points

It binds Rockchip compatibles using OF match data, supports optional named `pwm` and `pclk` clocks, and uses MMIO plus the PWM core.

## Risks and test signals

If `clk_enable(pc->clk)` fails after `pclk` succeeds in `get_state()` or `apply`, `pclk` appears leaked. Non-locking polarity changes cause an output gap. Overlarge periods saturate to `U32_MAX`. Test each compatible, boot-enabled clock retention, polarity paths, separate/shared pclk, and clock failure injection.
