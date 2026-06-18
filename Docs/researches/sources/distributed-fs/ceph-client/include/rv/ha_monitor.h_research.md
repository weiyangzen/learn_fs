# sources/distributed-fs/ceph-client/include/rv/ha_monitor.h

Purpose: Extends deterministic RV monitors with hybrid automata environment variables, clock constraints, invariant timers, and environment-aware reactions.

Important APIs/types/functions: Includes DA monitor after installing HA hooks. Important helpers include `ha_monitor_init_env()`, `ha_monitor_reset_env()`, `ha_monitor_handle_constraint()`, `ha_get_env_string()`, clock helpers for ns and jiffies, invariant conversion helpers, timer setup/start/cancel for timer wheel and hrtimer modes, and trace/reaction helpers.

Control flow and state: HA state overlays `struct ha_monitor` on `struct da_monitor`; a static assertion requires `da_mon` at offset zero. Initialization resets stored environment values and sets up timers. Each DA transition invokes `ha_verify_constraint()` with cached time; failure emits reaction and trace data and rejects the transition. Timers can fire without an event, report the current environment, and reset the DA monitor. Environment storage uses `ENV_INVALID_VALUE` and changes representation between guard reset timestamps and invariant expiration timestamps.

Dependencies and integration: Depends on generated monitor-provided `ha_get_env()` and `ha_verify_constraint()`, RV reactors, seq buffers, Linux timers/hrtimers, and DA monitor types. Timer behavior varies by `HA_TIMER_TYPE`, `HA_CLK_NS`, and monitor scope.

Risks and test signals: Risks include invalid env index use, mixing guard and invariant representations, timer callback racing with transition handling, per-CPU timer affinity mistakes, and missing generated HA callbacks. Tests should cover constraint pass/fail, timer expiry, ns/jiffy clocks, invariant conversion, monitor reset cancellation, and reactor/trace output.
