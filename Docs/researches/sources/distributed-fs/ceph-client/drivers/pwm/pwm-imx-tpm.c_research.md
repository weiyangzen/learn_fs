<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx-tpm.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx-tpm.c

Purpose: supports the NXP i.MX TPM PWM block, where the counter and period register are shared by all channels and each channel has its own mode/status and compare value.

Important APIs/types/functions: `struct imx_tpm_pwm_chip` tracks clock, MMIO base, mutex, `user_count`, `enable_count`, and cached `real_period`. `pwm_imx_tpm_round_state()` computes prescale/MOD/CnV values and the actual hardware state. `pwm_imx_tpm_apply_hw()` serializes shared counter updates, polarity, duty, and enable-count logic. `request/free`, `get_state`, and PM suspend/resume complete the PWM core interface.

Control flow: probe maps registers, enables the clock, reads `PWM_IMX_TPM_PARAM_CHAN` for channel count, initializes the mutex, counts already enabled channels, and registers the chip. Apply rounds the requested state, locks, rejects period changes when more than one user exists or when an active counter would need a prescale change, updates prescale/MOD/CnV, waits for latched values, refuses polarity changes on active channels, then updates channel mode bits and starts/stops the shared counter based on `enable_count`.

State and persistence: `real_period` is a software cache because the shared period is not per-channel. `user_count` and `enable_count` coordinate shared resources. Hardware registers hold actual channel status. Suspend refuses if any channel is enabled, zeros `real_period` so resume forces reprogramming, disables the clock, and switches pinctrl to sleep; resume selects default pinctrl and reenables the clock.

Dependencies and integration: depends on platform/OF, clk, pinctrl PM states, mutexes, MMIO, jiffies timeouts, and PWM core. Its behavior is constrained by TPM hardware latching semantics.

Risks and test signals: shared period semantics can surprise consumers; period/prescale changes should be tested with multiple requested channels. Busy-wait latching is timeout-sensitive and uses `real_period` for timeout sizing. Test active polarity rejection, suspend `-EBUSY`, enabled-channel count after bootloader state, very small periods, and register latch timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-imx-tpm.c -->
