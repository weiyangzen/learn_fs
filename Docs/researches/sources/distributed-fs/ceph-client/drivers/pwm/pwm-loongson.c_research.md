<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-loongson.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-loongson.c

Purpose: drives Loongson PWM registers for a single-channel counter with duty, period, control, polarity inversion, and enable/output-control bits.

Important APIs/types/functions: `struct pwm_loongson_ddata` stores MMIO base, clock frequency, and suspend shadow registers. `pwm_loongson_config()`, `pwm_loongson_set_polarity()`, `pwm_loongson_enable()`, `pwm_loongson_disable()`, `pwm_loongson_apply()`, and `pwm_loongson_get_state()` implement the PWM behavior. Probe supports OF and ACPI IDs and reads `clock-frequency`, defaulting to 50 MHz.

Control flow: probe maps MMIO, reads clock frequency from firmware properties, and registers one PWM. Apply optionally changes polarity, disables when needed, computes period/duty counts from the configured frequency, writes duty and period, and enables output/counter. Suspend saves duty/period/control and disables the PWM; resume restores the saved registers.

State and persistence: hardware registers hold runtime state. The driver shadows `duty`, `period`, and `ctrl` across system sleep only. There is no clock framework integration; the frequency property is assumed static.

Dependencies and integration: depends on platform bus, ACPI/OF matching, device properties, MMIO access, PM sleep ops, and PWM core.

Risks and test signals: wrong `clock-frequency` directly skews all periods and duty cycles. Control bit `OE` is active-low by hardware comment, so enable/disable polarity deserves hardware validation. Test OF and ACPI probe, suspend/resume restore, inverted polarity, frequency defaulting, and max/min count conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-loongson.c -->
