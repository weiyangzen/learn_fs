# sources/distributed-fs/ceph-client/include/trace/events/timer.h

Purpose: Defines the `timer` trace system for low-resolution timers, high-resolution timers, interval timers, and tick-stop decisions.

Important APIs/types/functions: Uses `timer_class`, `hrtimer_class`, `itimer_state`, and related templates to define `timer_start`, `timer_expire_entry`, timer cancel/expire events, `hrtimer_setup`, `hrtimer_start`, `hrtimer_expire_entry`, hrtimer cancel/expire/forward/rearm events, `itimer_*`, and `tick_stop`.

Control flow: Timer core code calls generated helpers when timers are initialized, started, cancelled, expired, or when the periodic tick is stopped. TP assignment records timer addresses, callbacks, expiry times, clock base, modes, and process/signal context for interval timers.

State/persistence: No timer ownership is introduced. The trace stream persists point-in-time timer configuration and expiry observations.

Dependencies/integration: Includes timer/hrtimer, signal, and tracepoint-related kernel types; integrated with ftrace, perf, and timer debugging tools.

Risks: Timer callbacks are often on hot paths or interrupt context. Trace fields must avoid sleeping, must tolerate partially initialized timers, and must preserve event ABI names used by diagnostics.

Test signals: Kernel timer selftests, hrtimer stress, NO_HZ/tick-stop workloads, and tracefs checks for start/expire/cancel event pairing.
