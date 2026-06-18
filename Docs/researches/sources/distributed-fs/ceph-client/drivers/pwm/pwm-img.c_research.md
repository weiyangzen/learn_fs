<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-img.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-img.c

Purpose: implements the Imagination Technologies Pistachio PWM DAC controller with four channels, per-channel timebase/duty registers, shared divider control, peripheral PDM mux clearing, runtime PM, and sleep-state save/restore.

Important APIs/types/functions: `struct img_pwm_chip` stores `sys` and `pwm` clocks, MMIO base, peripheral syscon regmap, period bounds, SoC max timebase, and suspend shadows. `img_pwm_config()`, `img_pwm_enable()`, `img_pwm_disable()`, and `img_pwm_apply()` are the PWM operations. PM callbacks are `img_pwm_runtime_suspend/resume()` and system `img_pwm_suspend/resume()`.

Control flow: probe maps the PWM block, looks up the `img,cr-periph` syscon, enables runtime PM, validates the PWM clock rate, computes min/max period bounds, and registers four PWMs. Apply rejects inverted polarity, validates period range, computes divider and timebase among no-div, /8, /64, and /512 modes, writes channel config under runtime PM, and enables the channel by setting `PWM_CTRL_CFG` plus clearing the peripheral PDM-control bit.

State and persistence: runtime state is in channel config registers and `PWM_CTRL_CFG`; the driver keeps min/max period metadata and suspend shadow copies. Runtime suspend disables both clocks. System suspend forces a resume if necessary, snapshots all channel config and control registers, then suspends clocks; resume restores registers and PDM mux state for enabled channels.

Dependencies and integration: depends on OF/platform probing, clk, regmap syscon, runtime PM autosuspend, PWM core, and Pistachio match data. It integrates with SoC pin/peripheral routing through the syscon phandle.

Risks and test signals: no `.get_state()` means consumers cannot read back actual rounded state through this driver. PM ordering is delicate because register reads/writes need clocks. Test period min/max boundaries, each divider bucket, PDM mux clearing after enable and resume, autosuspend behavior, and removal when runtime PM is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-img.c -->
