<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-pca9685.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-pca9685.c

Purpose: implements PWM support for the NXP PCA9685 I2C 16-channel, 12-bit PWM/LED controller, exposing 16 per-channel PWMs plus an all-channels pseudo-channel.

Important APIs/types/functions: `struct pca9685` stores regmap, mutex, prescale, and active-channel bitmap. `pca9685_round_waveform_tohw/fromhw()`, `pca9685_read_waveform()`, `pca9685_write_waveform()`, `pca9685_pwm_request()`, `pca9685_pwm_free()`, and sleep-mode helpers implement the PWM waveform API. Regmap callbacks define readable/writeable/volatile registers.

Control flow: probe creates an I2C regmap, resets MODE registers, selects output driver behavior, reads or programs prescale, enables runtime PM, and registers 17 PWM entries. Request marks a channel active and prevents unsafe prescaler changes. Waveform write may change global prescale only when no other active channel conflicts, enters sleep for prescale programming, then writes four LED registers or all-channel registers. Free clears active tracking and can allow sleep/prescale changes.

State and persistence: hardware registers store mode, prescale, and on/off counts. Software tracks active channels and cached prescale to enforce global-frequency constraints. Runtime suspend enters chip sleep mode; resume leaves sleep.

Dependencies and integration: depends on I2C, regmap, runtime PM, mutexes, OF/ACPI/I2C IDs, PWM waveform API, and optional all-channel semantics encoded as channel index 16.

Risks and test signals: prescale is global, so changing one channel can disturb others unless correctly blocked. Test multi-channel period conflicts, all-channel pseudo-PWM behavior, sleep/resume, full-on/full-off LED bits, regmap errors, and request/free active bitmap handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-pca9685.c -->
