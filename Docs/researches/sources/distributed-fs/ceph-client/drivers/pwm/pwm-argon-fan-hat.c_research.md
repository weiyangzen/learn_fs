# sources/distributed-fs/ceph-client/drivers/pwm/pwm-argon-fan-hat.c

Purpose: exposes the Argon40 Fan HAT I2C fan controller as a one-channel PWM provider with a fixed about-30 kHz period.

Important APIs/types/functions: this driver uses the PWM waveform API rather than legacy `.apply`. `argon_fan_hat_round_waveform_tohw()` maps requested duty length to an 8-bit percentage value, `argon_fan_hat_round_waveform_fromhw()` maps percentage back to a fixed-period waveform, and `argon_fan_hat_write_waveform()` writes the duty percent to I2C register `0x80`.

Control flow: I2C probe allocates one PWM chip and stores the `i2c_client` as driver data. Users set waveforms through the PWM core; the driver rounds any period to the fixed HAT period and writes only the duty percentage. There is intentionally no read callback because reading from the controller stops the fan.

State and persistence: no software cache is kept. The controller stores the last written duty internally; the PWM core's requested state is the only readable host-side state.

Dependencies and integration: depends on I2C SMBus byte writes, OF compatible `argon40,fan-hat`, and the PWM core waveform callbacks. It can also participate in the framework's character-device waveform path.

Risks and test signals: absence of hardware readback limits diagnostics and resume validation. Rounding is coarse to integer percent and ignores requested offset or period. Test signals include I2C write failures, 0/100 percent duty, fixed-period roundtrip through `PWM_IOCTL_ROUNDWF`, and verifying that no read path is attempted on hardware.
