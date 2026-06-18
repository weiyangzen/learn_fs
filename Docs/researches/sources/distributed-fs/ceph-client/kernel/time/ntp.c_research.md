# sources/distributed-fs/ceph-client/kernel/time/ntp.c

Purpose: implements kernel NTP state discipline: tick length adjustment, PLL/FLL phase/frequency control, leap-second state, `adjtimex` state import/export, optional PPS discipline, and optional synchronized RTC/CMOS updates.

Important APIs and flow: `ntp_data` stores per-timekeeper discipline fields. `ntp_update_frequency()` folds tick, frequency, and boot adjustment into scaled tick length. `ntp_update_offset()` clamps phase offset, computes PLL/FLL frequency adjustment, and sets residual offset. `second_overflow()` advances leap-second state, maxerror, phase chunking, PPS validity, and `adjtime()` tick adjustments once per second. `ntp_adjtimex()` processes modes such as status, nano/micro, frequency, errors, time constant, TAI, offset, and tick, emits audit changes, and fills return timex fields. PPS paths normalize timestamps, update frequency intervals/stability, reject jitter/wander, and optionally drive clock phase/frequency. CMOS sync uses an hrtimer plus workqueue to write persistent clock or RTC near the desired second edge.

State and persistence: `tk_ntp_data[]` persists per timekeeper. Hardware sync has static offset state plus `sync_hrtimer` and work item. Boot parameter `ntp_tick_adj=` modifies core tick adjustment.

Dependencies and integration: timekeeping internals, audit, hrtimer/workqueue, RTC class or legacy persistent clock, jiffies tick constants, PPS config, timex ABI, and leap-second consumers.

Risks and test signals: risks include scaled math overflow/clamping, leap second boundaries, PPS false rejection, unsynchronized status propagation, RTC phase-window retries, and multi-timekeeper indexing. Test with `adjtimex`, leap insert/delete simulations, PPS hardpps input, `STA_UNSYNC` transitions, RTC sync retry/offset changes, and boot tick adjustment.
