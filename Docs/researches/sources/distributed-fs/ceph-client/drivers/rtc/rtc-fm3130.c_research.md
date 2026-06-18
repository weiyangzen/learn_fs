# sources/distributed-fs/ceph-client/drivers/rtc/rtc-fm3130.c

Purpose: implements an I2C RTC driver for the Ramtron FM3130, including clock read/write, alarm register access, alarm enable control, and probe-time cleanup of oscillator/read/write/calibration modes.

Important APIs/types/functions: `struct fm3130` caches register buffers, I2C messages, RTC pointer, and validity flags. `fm3130_rtc_mode()` toggles read/write mode bits. `fm3130_get_time()`/`fm3130_set_time()` access clock registers. `fm3130_read_alarm()`/`fm3130_set_alarm()` handle alarm registers with `0x80` wildcard/disable values. `fm3130_alarm_irq_enable()` toggles `AEN`.

Control flow: probe validates I2C functionality, builds reusable I2C messages, reads time and alarm blocks, clears calibration/read/write modes, starts the oscillator, clears low-battery/POR flags, configures alarm write-protect control, sanity-checks cached clock/alarm values, and registers the RTC even if cached values are invalid. Time reads enter read mode, perform a block transfer, exit normal mode, and decode BCD. Time writes enter write mode and write individual bytes. Alarm writes update five alarm registers and control bits.

State and persistence: time, alarm, control, and calibration registers persist in the chip. Runtime `data_valid` and `alarm_valid` determine whether reads return `-EIO` until a successful write establishes sane data.

Dependencies and integration: depends on I2C/SMBus byte writes, RTC core, BCD helpers, and client ID binding.

Risks and test signals: probe labels the clock-register sanity block as alarm validation first, so alarm validity appears based on current clock fields rather than alarm fields. I2C SMBus writes in loops do not check every return. Test invalid battery/POR data, mode cleanup, oscillator enable, alarm wildcard handling, alarm enable/disable, and partial I2C failure behavior.
