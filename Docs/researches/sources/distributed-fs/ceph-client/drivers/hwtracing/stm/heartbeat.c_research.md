
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/heartbeat.c

Purpose: STM source test module that periodically emits a static heartbeat message through linked STM devices.

Important APIs/types/functions: `struct stm_heartbeat` embeds source data, hrtimer, and active flag. Module parameters `nr_devs` and `interval_ms` control number of source devices and period. `stm_heartbeat_hrtimer_handler()` writes the heartbeat and rearms while active.

Control flow: init creates up to 32 named sources `heartbeat.N`, initializes hrtimers, and registers source devices. Linking a source starts its hrtimer. Unlinking clears active and cancels the timer. Exit unregisters all and frees names.

State and persistence: static array plus allocated names; timer activity exists only while linked. No persistent trace data.

Dependencies and integration: depends on STM source APIs and high-resolution timers.

Risks: very low intervals can generate substantial trace traffic. Timer handler writes from hrtimer context, so STM source write path must remain context-appropriate. Error cleanup interleaves unregister/free labels and should be regression-tested.

Test signals: register multiple heartbeat sources, link/unlink, observe periodic trace messages, vary interval, validate invalid `nr_devs`, and unload while timers are active.
