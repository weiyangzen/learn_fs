# sources/distributed-fs/ceph-client/include/linux/leds-expresswire.h

Purpose: declares shared helpers for Kinetic ExpressWire LED controllers that are programmed by timed pulses on a control GPIO.

Important APIs and types: `struct expresswire_timing` defines poweroff, detect, data-start, end-of-data, and short/long bit pulse timings. `struct expresswire_common_props` carries the control GPIO and timing table. Public helpers power off, enable, and write an 8-bit value over the pulse protocol.

Control flow: chip drivers initialize timing and GPIO, call `expresswire_enable()` for protocol detection/wake, write bytes with `expresswire_write_u8()`, and call `expresswire_power_off()` when disabling the LED.

State and persistence: protocol state is transient GPIO level/timing state. Hardware may latch the last byte, but the helper header stores no state.

Dependencies and integration points: depends on GPIO descriptors and timing delays in the implementation; shared by KTD2692/KTD2801-style LED drivers.

Risks and test signals: risks are timing regressions, sleeping/atomic context misuse, and GPIO polarity assumptions. Test with logic-analyzer pulse timings, power-off sequencing, byte writes across all bit patterns, and suspend/resume.
