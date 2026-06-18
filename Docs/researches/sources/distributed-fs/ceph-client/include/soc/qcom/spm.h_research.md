# sources/distributed-fs/ceph-client/include/soc/qcom/spm.h

Purpose: declares Qualcomm Subsystem Power Manager low-power mode selection for CPU idle paths.

Important APIs/types/functions: defines `enum pm_sleep_mode` with standby, retention, standalone power collapse, power collapse, and count values, forward-declares `struct spm_driver_data`, and exports `spm_set_low_power_mode()`.

Control flow: cpuidle or platform code selects a low-power mode and calls `spm_set_low_power_mode()` on driver data; the implementation updates SPM sequence/register programming for the next idle entry.

State and persistence: mode selection persists in SPM driver/hardware configuration until changed. The header owns no state.

Dependencies and integration: implemented in `drivers/soc/qcom/spm.c` and consumed by `drivers/cpuidle/cpuidle-qcom-spm.c`.

Risks: choosing an unsupported or wrong mode can break CPU idle, wakeup latency, or power-collapse resume. Test signals include cpuidle state transitions, suspend/resume, power measurements, and wakeup-source validation.
