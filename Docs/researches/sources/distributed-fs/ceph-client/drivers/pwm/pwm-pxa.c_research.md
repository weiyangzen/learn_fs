<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-pxa.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-pxa.c

Purpose: provides PWM support for Intel/Marvell PXA and compatible PWM blocks, including platform-ID and OF variants with one or two channels depending on device data.

Important APIs/types/functions: `struct pxa_pwm_chip` stores clock, MMIO base, and selected channel offset. `pxa_pwm_config()` computes prescaler, period count, and duty count, then writes `PWMCR`, `PWMDCR`, and `PWMPCR`. `pxa_pwm_apply()` manages enable/disable and normal polarity. Probe selects channel/resource based on platform data, ID flags, or OF compatible.

Control flow: probe resolves whether the device exposes a secondary PWM, maps the proper MMIO resource, gets the clock, sets ops, and registers one PWM instance. Apply rejects inverted polarity, disables output when requested, or enables the clock, configures registers, and sets the enable bit.

State and persistence: runtime state is hardware register state and clock enable. The driver has no get-state, no software cache, and no suspend/resume handling.

Dependencies and integration: depends on platform device IDs, optional OF matching for `marvell,pxa250-pwm` and `marvell,pxa270-pwm`, clk framework, MMIO, and PWM core.

Risks and test signals: channel/resource selection varies by platform ID and can map the wrong resource if board data is inconsistent. Test primary and secondary PWM IDs, OF compatibles, prescaler/count limits, disable clock balance, polarity rejection, and legacy board-file probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-pxa.c -->
