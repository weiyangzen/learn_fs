# sources/distributed-fs/ceph-client/drivers/net/dsa/hirschmann/hellcreek_ptp.c

Purpose: this file implements the Hellcreek PTP hardware clock and LED status outputs. It registers a PHC, reads and sets time, applies frequency and offset adjustments, tracks seconds in software around a hardware nanoseconds counter, schedules overflow maintenance, and registers two LED class devices backed by PTP status output bits.

Important APIs, types, and functions: exported helpers are `hellcreek_ptp_read()`, `hellcreek_ptp_write()`, `hellcreek_ptp_gettime_seconds()`, `hellcreek_ptp_setup()`, and `hellcreek_ptp_free()`. PTP operations include `hellcreek_ptp_gettimex()`, `hellcreek_ptp_settime()`, `hellcreek_ptp_adjfine()`, `hellcreek_ptp_adjtime()`, and `hellcreek_ptp_enable()`. Worker and LED helpers include `hellcreek_ptp_overflow_check()`, `hellcreek_led_setup()`, and brightness set/get callbacks.

Control flow: setup initializes delayed overflow work, fills `ptp_clock_info`, registers the PHC, enables hardware offset and drift correction, registers LEDs from the `leds` child node, and schedules periodic overflow checks. Time reads snapshot hardware, read several sync-data words, wrap system timestamp pre/post hooks around the low-nanoseconds read, update software seconds when nanoseconds roll over, and return full nanoseconds. Large time adjustments are converted to settime; smaller adjustments program slow offset correction registers. Frequency adjustments compute a drift addend from scaled ppm and program the drift register.

State and persistence: `hellcreek->seconds` and `hellcreek->last_ts` persist the high-order time component missing from hardware. `status_out` shadows LED output bits. The PTP clock registration persists until remove. Hardware persistence includes clock write, drift, offset, status, snapshot, and status output registers.

Dependencies and integration points: it integrates with Linux PTP clock core, system timestamp capture, delayed work, LED class devices and OF LED defaults, Hellcreek hwtstamp worker, and the `ptp_lock` shared with timestamping and TAPRIO schedule calculations.

Risks: hardware exposes only nanoseconds plus partial seconds, making periodic overflow checks essential. `hellcreek_ptp_gettime_seconds()` must infer whether a packet timestamp belongs to the current or previous software second. LED setup requires two available LED child nodes; failure unregisters the PHC. Adjfine arithmetic assumes a 125 MHz oscillator and hardware accumulator behavior.

Test signals: PHC registration and `phc2sys` reads, `settime`, small and large `adjtime`, positive and negative `adjfine`, rollover handling across seconds, hwtstamp timestamp reconstruction near rollover, PTP worker invocation, LED default-state parsing and brightness writes, and remove cleanup cancelling overflow work and unregistering LEDs/PHC.
