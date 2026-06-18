# sources/distributed-fs/ceph-client/drivers/pwm/pwm-raspberrypi-poe.c

## Purpose

`pwm-raspberrypi-poe.c` exposes the Raspberry Pi firmware-controlled PoE HAT fan PWM as a Linux PWM chip. It talks to Raspberry Pi firmware mailbox properties rather than memory-mapped timer registers. The hardware surface is fixed: 12.5 kHz period, 8-bit duty, normal polarity only, and no real disable bit.

## APIs, control flow, and state

`struct raspberrypi_pwm` stores the firmware handle and cached firmware-scale duty. `raspberrypi_pwm_set_property()` and `raspberrypi_pwm_get_property()` wrap `rpi_firmware_property()` calls and translate firmware status to Linux errors. `raspberrypi_pwm_apply()` validates normal polarity and minimum period, maps disabled state to duty 0, quantizes duty to 0..255, writes firmware only on changes, and updates the cache on success. `get_state()` reports the fixed period and cached duty, so external firmware changes can make it stale.

Probe walks to the parent firmware node, gets a firmware handle, allocates `RASPBERRYPI_FIRMWARE_PWM_NUM` channels, reads the current duty register, and registers with `devm_pwmchip_add()`. Persistent state lives in firmware-controlled hardware plus the driver's duty cache.

## Dependencies and integration points

The driver depends on the PWM core, OF compatible `raspberrypi,firmware-poe-pwm`, `soc/bcm2835/raspberrypi-firmware.h`, and the firmware PoE PWM DT binding.

## Risks and test signals

Small nonzero duty requests can round down to disabled. Period requests above 80 us are accepted but the actual period remains fixed. There is no lock around the cached duty beyond PWM core serialization. Test probe deferral, initial duty readback, disabled/min/half/full duty, inverted-polarity rejection, and firmware error handling.
