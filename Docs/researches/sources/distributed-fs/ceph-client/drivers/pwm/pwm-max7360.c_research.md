<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-max7360.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-max7360.c

Purpose: exposes the MAX7360 keypad/GPIO expander PWM outputs through the PWM waveform API. The chip provides eight fixed-period, 8-bit duty PWM channels.

Important APIs/types/functions: `struct max7360_pwm_waveform` stores an 8-bit duty value and enable flag. `max7360_pwm_request()` switches a pin to PWM mode through pinctrl. `max7360_pwm_round_waveform_tohw/fromhw()`, `max7360_pwm_write_waveform()`, and `max7360_pwm_read_waveform()` implement fixed 2 ms period conversion and parent regmap accesses. Probe registers eight PWMs.

Control flow: request looks up and selects a per-channel PWM pinctrl state. Waveform conversion clamps duty to 0..255 over the fixed period and represents zero duty as disabled. Write updates the channel duty register or disables by writing zero; read imports current register value. Probe retrieves parent MAX7360 data and registers the chip.

State and persistence: hardware registers store duty values; pinctrl state controls pin function. The driver keeps no software cache and relies on parent regmap state.

Dependencies and integration: depends on the MAX7360 MFD/regmap, pinctrl states, PWM waveform callbacks, and platform device creation by the parent.

Risks and test signals: missing per-channel pinctrl states prevent channel request. Fixed-period semantics should be tested with consumers that ask for different periods. Test all eight channels, 0/1/255 duty, read/write round trips, pinctrl errors, and parent regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-max7360.c -->
