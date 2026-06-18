# sources/distributed-fs/ceph-client/drivers/base/syscore.c

Purpose: this file manages `syscore` operations, a list of very low-level system core callbacks used during suspend, resume, and shutdown when normal driver/device ordering is no longer sufficient.

Important APIs, types, and functions: exported functions are `register_syscore`, `unregister_syscore`, `syscore_suspend`, and `syscore_resume`; `syscore_shutdown` is a core shutdown entry point. State is a global `syscore_list` protected by `syscore_lock`. Each element is a `struct syscore` whose `ops` can contain `suspend`, `resume`, and `shutdown` callbacks plus opaque `data`.

Control flow: registration appends to the list under mutex, while unregister removes under mutex. Suspend, when enabled by `CONFIG_PM_SLEEP`, emits power tracepoints, checks pending wakeup events, warns if interrupts are enabled, then walks the list in reverse registration order calling suspend callbacks. On failure, it reports the failing callback and resumes the remaining callbacks in forward continuation order. Resume walks forward and calls resume callbacks. Shutdown locks the list and walks reverse order, optionally logging when `initcall_debug` is set.

State and persistence: registered syscore entries persist globally until explicitly unregistered. Suspend/resume does not change the list; it only invokes callbacks. The callback order encodes dependency behavior: last registered suspends first and resumes later in the unwind sequence.

Dependencies and integration points: it integrates with PM sleep, wakeup-source checks, power tracepoints, the global `initcall_debug`, and subsystems that cannot rely on normal device PM late in suspend. Callers must ensure callback data remains valid while registered.

Risks: callbacks run with one CPU online and interrupts disabled in suspend/resume, so sleeping or enabling interrupts is a serious bug. The suspend path does not hold `syscore_lock`, assuming registration is not racing with suspend. Failure unwind correctness depends on list ordering and callbacks being idempotent enough for partial suspend rollback.

Test signals: suspend/resume trace events, warnings about interrupt state, injected failing syscore suspend callbacks, and shutdown ordering tests are useful. Runtime coverage should check reverse suspend/shutdown order and forward resume order.
