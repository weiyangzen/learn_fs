# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_device.c

## Purpose
`aw88395_device.c` is the register/DSP engine for AW88395. It implements chip identification, DSP mailbox access, firmware/profile updates, volume and fade handling, calibration data updates, PLL/system status checks, start/stop sequencing, and profile query/set helpers exported to the top-level driver.

## Important APIs, Types, And Functions
Exported APIs include `aw88395_init()`, `aw88395_dev_init()`, `aw88395_dev_start()`, `aw88395_dev_stop()`, `aw88395_dev_fw_update()`, volume/profile helpers, `aw88395_dev_mute()`, and generic `aw_dev_dsp_read()`/`aw_dev_dsp_write()`. DSP access supports 16-bit and 32-bit data using `AW88395_DSPMADD_REG` and `AW88395_DSPMDAT_REG`, serialized by `aw_dev->dsp_lock`. Firmware update writes register sections, optionally DSP firmware, always DSP config, copies config for CRC calculation, computes vcalb, reads RA, F0 delay, and initial VMAX. Runtime start checks PLL, amplifier/system state, firmware sample contents, DSP CRC32, watchdog, and interrupts before unmuting.

## Control Flow
Initialization starts with chip-ID read and default `aw_device` setup, including `fw_status = FAILED`, default volume/fade settings, profile defaults, and optional `awinic,audio-channel`. `aw88395_dev_init()` parses the already validated ACF, sets profile 0 current/index, performs a forced full firmware update, then leaves the chip muted, TX feedback disabled, DSP disabled, amplifier powered down, and chip powered down. Playback start powers up, checks PLL in mode1 with mode2 fallback, enables amplifier, checks system status, validates DSP firmware/config when DSP is active, enables I2S TX feedback, unmutes, clears interrupts, and marks `PW_ON`. Stop reverses that path and, if stop-time system interrupts indicate an anomaly, reloads DSP firmware/config before power-down.

## State And Persistence
State lives in `struct aw_device`: `status`, `fw_status`, `prof_cur`, `prof_index`, `dsp_cfg`, `dsp_crc_st`, firmware/config lengths, profile descriptors, volume descriptor, DSP memory descriptor, calibration descriptor, VMAX, and channel. The parsed firmware container remains the backing store for profile section pointers. `crc_dsp_cfg` is a mutable copy of the DSP config used to incorporate runtime calibration changes before CRC32 generation.

## Dependencies And Integration Points
The file depends on regmap, I2C, device tree, CRC32C, Linux delays, mutexes, and definitions from `aw88395_reg.h`, `aw88395_device.h`, and `aw88395_lib.c`. It integrates upward with ALSA controls through exported volume/profile/calibration methods, and downward with hardware through precise register sequences and DSP memory base addresses.

## Risks And Test Signals
The 32-bit DSP access ordering and endian conversions are critical; corruption would surface as firmware check, CRC, or calibration failures. Bounds checks exist for config mutation and profile indices, but firmware section completeness is delegated to the parser. Start/stop has many hardware timing assumptions; missing clocks produce PLL/system-status errors. Test signals include chip ID `0x2049`, successful SRAM test, DSP firmware sample check, CRC32 pass, watchdog nonzero, sane RA/cali values, profile switching while active, and no interrupt bits after stop.
