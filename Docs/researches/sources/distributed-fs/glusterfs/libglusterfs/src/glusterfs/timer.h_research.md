# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/timer.h

Purpose: `timer.h` declares a per-context timer registry for delayed callbacks.

Important APIs and types: `gf_timer_t` has list/next/prev linkage, scheduled `timespec`, callback, callback data, owning translator, and fired flag. `gf_timer_registry_t` has an active list, mutex, condition variable, thread, and finish flag. APIs schedule callbacks after a delta, cancel events, and destroy the registry.

Control flow and state: timers are inserted into a context registry, a registry thread waits until the next deadline, fires callbacks, and cancellation removes pending events. State is attached to `glusterfs_ctx_t`.

Dependencies and integration: includes `xlator.h` and pthread/time headers. Logging suppression flush, syncop sleeps/timeouts, and other delayed tasks can use this registry.

Risks: callback lifetime depends on caller-owned `data` and `xl` staying valid until fire/cancel. Races between cancellation and fired callbacks are central. Registry destruction must stop the thread after draining or invalidating callbacks.

Test signals: schedule/cancel races, immediate and delayed timers, destroy with pending timers, callback ordering, fired flag behavior, and translator cleanup interactions should be covered.
