# sources/distributed-fs/ceph-client/samples/kprobes/kretprobe_example.c

Purpose: kretprobe sample that measures return value and duration of a configurable function, defaulting to `kernel_clone`.

Important APIs/functions: `struct kretprobe`, `struct kretprobe_instance`, `register_kretprobe`, `unregister_kretprobe`, `regs_return_value`, `ktime_get`, `ktime_sub`, and per-instance `data_size`.

Control flow: init assigns target symbol and registers a kretprobe with entry and return handlers. Entry skips kernel threads, timestamps user-process calls, and return handler logs return value and elapsed nanoseconds. Exit unregisters and reports missed instances.

State and persistence: global kretprobe and per-active-instance timestamp data.

Dependencies and integration: kretprobe support and function return instrumentation.

Risks: `maxactive=20` may be too low for high-concurrency symbols; missed probes are reported on exit. Probing hot functions adds overhead.

Test signals: load with `func=kernel_clone`, fork processes, inspect duration logs and `nmissed` on unload.
