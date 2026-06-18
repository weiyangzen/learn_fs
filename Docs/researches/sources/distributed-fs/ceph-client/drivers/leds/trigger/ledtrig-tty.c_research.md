<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-tty.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-tty.c

Purpose: The TTY trigger monitors a named TTY for RX/TX counter changes and modem-control line states, then blinks or enables/disables a LED.

Important APIs and state: `struct ledtrig_tty_data` stores LED pointer, delayed work, a completion used to serialize some sysfs operations with the polling worker, configured tty name, held `tty_struct`, last rx/tx counters, and mode booleans for rx, tx, cts, dsr, dcd, and rng. Sysfs exposes `ttyname` and all mode booleans. Default mode enables rx and tx.

Control flow: Activation allocates state, initializes delayed work and completion, stores trigger data, and schedules the worker immediately. The worker resolves `ttyname` to a device number when needed, opens a shared TTY reference, reads modem-control bits, checks rx/tx counters after line-state evaluation so activity has priority, then either blinks oneshot, sets brightness to blink brightness, or turns off. It completes sysfs waiters and reschedules itself every 100 ms. `ttyname_store()` trims newline, waits for the worker completion, drops any old TTY reference, and replaces the name. Deactivation cancels work, frees the name, drops the TTY reference, and frees state.

State and persistence: Per-LED trigger state persists until deactivation. The TTY reference is held once resolved and released when the name changes or trigger deactivates. There is no persisted configuration across trigger changes.

Dependencies and integration: It depends on TTY core helpers, serial icounter APIs, LED blink helpers, delayed work, sysfs attributes, and completions.

Risks and test signals: Sysfs synchronization uses completion timeouts tied to the polling interval; a wedged worker can cause `-ETIMEDOUT`. Mode stores are not completion-serialized. Test nonexistent TTY retry, TTY hotplug/removal, rx/tx blinking priority over line-state enable, modem-control modes, name replacement, and deactivation with a held TTY.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-tty.c -->
