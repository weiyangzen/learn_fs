# sources/cloud-native/cri-o/server/server_freebsd.go

Purpose: FreeBSD implementation of Go runtime thread-limit configuration for CRI-O.

Important APIs and functions: `configureMaxThreads` reads `kern.threads.max_threads_per_proc`, sets Go's max thread limit to 90 percent of that value, and logs the configured value.

Control flow: sysctl read errors are ignored with nil return. Successful reads compute `(value / 100) * 90`, then call `debug.SetMaxThreads`.

State and persistence: mutates the Go runtime's process-wide max thread setting.

Dependencies and integration: called during `New` server initialization on FreeBSD; uses `golang.org/x/sys/unix` sysctl and `runtime/debug`.

Risks: integer math truncates before multiplying by 90, so small values lose precision. Ignoring sysctl errors favors startup resilience over explicit warnings.

Test signals: no direct tests in this subset.
