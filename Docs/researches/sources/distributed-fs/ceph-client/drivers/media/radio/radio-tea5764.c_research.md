# sources/distributed-fs/ceph-client/drivers/media/radio/radio-tea5764.c

Purpose: implements an I2C V4L2 radio driver for the NXP TEA5764 FM tuner, originally used in Motorola EZX phones. It supports FM tuning, mono/stereo selection, mute, signal reporting, and chip power up/down.

Important APIs and functions: I2C lifecycle is `tea5764_i2c_probe` and `tea5764_i2c_remove`. Register helpers are `tea5764_i2c_read` and `tea5764_i2c_write`. Power/tuning helpers include `tea5764_power_up`, `tea5764_power_down`, `tea5764_set_freq`, `tea5764_get_freq`, `tea5764_tune`, `tea5764_set_audout_mode`, and `tea5764_mute`. V4L2 handlers cover tuner/frequency operations and mute control.

Control flow: probe registers a V4L2 device and mute control, reads the full register map, verifies chip and manufacturer IDs, initializes the video device, sets stereo, mutes, powers down, then registers the radio node. Setting a nonzero frequency clamps to 87.5-108 MHz, powers up, converts V4L2 units to Hz-like chip input, programs PLL fields, and writes registers. Setting frequency zero is a legacy non-compliant power-down path that returns `-EINVAL`. Tuner get reads registers, reports stereo state, signal level, AFC, and current audio mode.

State and persistence: `struct tea5764_device` stores V4L2 objects, control handler, I2C client, video device, cached register image, and mutex. The cached register image mirrors hardware after reads/writes but is not persisted across unload. `use_xtal` and `radio_nr` are module parameters.

Dependencies and integration points: depends on I2C transfers, V4L2 device/ioctl/control/event APIs, endian conversion for packed register structures, and the board instantiating an I2C client named `radio-tea5764`.

Risks: register structures use packed layout and cast a register buffer to `u16 *`, so endian/unaligned assumptions need care. The zero-frequency power-down behavior is explicitly non-compliant but preserved for compatibility. I2C write errors in helpers such as mute/tune are often logged or ignored rather than propagated through all call chains. The driver has TODOs for platform IRQs and RDS support.

Test signals: I2C probe ID validation, endian-correct register dumps, frequency set/get across band limits, zero-frequency power-down compatibility, mute and mono/stereo controls, signal/AFC reporting on hardware, remove-time power-down, and `v4l2-compliance`.
