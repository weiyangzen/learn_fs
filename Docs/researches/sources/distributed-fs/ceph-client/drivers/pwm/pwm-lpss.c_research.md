<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.c

Purpose: implements the shared Intel LPSS PWM core used by both PCI and platform front-ends. It programs LPSS PWM registers with an enable bit, software-update bit, base-unit field, and on-time divider.

Important APIs/types/functions: exported board descriptors `pwm_lpss_byt_info`, `pwm_lpss_bsw_info`, `pwm_lpss_bxt_info`, and `pwm_lpss_tng_info` define clock rate, npwm, base-unit constraints, and bypass behavior. `struct pwm_lpss_chip` is allocated by `devm_pwm_lpss_probe()`. Core functions include `pwm_lpss_prepare()`, `pwm_lpss_prepare_enable()`, `pwm_lpss_wait_for_update()`, `pwm_lpss_apply()`, `pwm_lpss_get_state()`, and `pwm_lpss_remove()`.

Control flow: front-ends call `devm_pwm_lpss_probe()` with MMIO base and boardinfo; it allocates a PWM chip, stores base/info, sets ops, and registers the chip. Apply computes base-unit and on-time fields from requested state, handles fixed/bypass variants, writes the register with software-update, waits for update completion when required, and enables/disables the PWM. Get-state decodes the register to report enabled, period, duty, and normal polarity.

State and persistence: each channel state is hardware register state at `PWM_SIZE` spacing. The driver stores base and immutable boardinfo only. `pwm_lpss_remove()` is provided for front-ends that need explicit teardown.

Dependencies and integration: depends on PWM core, IO accessors, exported symbol namespace `PWM_LPSS`, PCI/platform wrappers, and Intel LPSS clock assumptions embedded in boardinfo.

Risks and test signals: timing math is boardinfo-sensitive, especially base-unit ranges and bypass mode. Test Bay Trail/Braswell/Broxton/Tangier descriptors, update timeout behavior, disabled readback, 0/100% duty, and probe/remove from both PCI and platform front-ends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-lpss.c -->
