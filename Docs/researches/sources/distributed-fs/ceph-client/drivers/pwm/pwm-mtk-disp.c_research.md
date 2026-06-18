<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mtk-disp.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-mtk-disp.c

Purpose: provides MediaTek display backlight PWM support. The hardware is a single display PWM with display-specific clocking, optional commit register behavior, and high-width/period fields suited to panel brightness control.

Important APIs/types/functions: `struct mtk_disp_pwm` stores base address, main/MM clocks, SoC data, and enabled state. `struct mtk_pwm_data` describes register offsets and whether the SoC has commit bits or blended clock behavior. `mtk_disp_pwm_apply()`, `mtk_disp_pwm_get_state()`, and `mtk_disp_pwm_update_bits()` implement behavior.

Control flow: probe maps registers, gets clocks, stores SoC data, and registers one PWM. Apply rejects unsupported polarity, enables clocks before programming, computes clock divider and high/period fields, writes display PWM registers and optional commit bits, toggles enable, and disables clocks if the output is off. Get-state enables clocks as needed, reads divider/period/high fields, and reconstructs period/duty.

State and persistence: hardware registers hold PWM configuration. The driver tracks whether clocks/output are currently enabled to avoid unnecessary clock toggles. No system PM restore is implemented in this file.

Dependencies and integration: depends on platform/OF, clk framework, MMIO, PWM core, and MediaTek display subsystem clock topology.

Risks and test signals: display backlight users are sensitive to glitches during duty updates and clock gating. Test all SoC data variants, commit behavior, enable/disable clock balance, divider limits, 0% duty, get-state when disabled, and panel brightness ramping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mtk-disp.c -->
