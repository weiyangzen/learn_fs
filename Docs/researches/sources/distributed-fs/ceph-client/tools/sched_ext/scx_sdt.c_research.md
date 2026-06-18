# sources/distributed-fs/ceph-client/tools/sched_ext/scx_sdt.c

Purpose: userspace loader and monitor for the `scx_sdt` arena-backed sched_ext scheduler. It opens, loads, attaches, and restarts the BPF struct_ops scheduler while printing scheduler and allocator counters once per second.

Important APIs, types, and functions: uses the generated `scx_sdt.bpf.skel.h` skeleton, sched_ext helper macros `SCX_OPS_OPEN`, `SCX_OPS_LOAD`, `SCX_OPS_ATTACH`, and `UEI_REPORT`, plus libbpf logging via `libbpf_set_print()`. `libbpf_print_fn()` gates debug messages behind `-v`; `sigint_handler()` sets `exit_req`; `main()` drives argument parsing, attachment, stat reporting, link destruction, and restart on `UEI_ECODE_RESTART()`.

Control flow: `main()` installs SIGINT/SIGTERM handlers, opens the skeleton at the `restart:` label, parses `-v`/`-h`, loads and attaches `sdt_ops`, then loops until a signal or BPF exit info is reported. The loop reads BSS globals directly through `skel->bss`, prints scheduling counters and allocator counters, flushes stdout, and sleeps one second. On exit it destroys the BPF link, reports the UEI code, destroys the skeleton, and restarts if requested.

State and persistence: userspace state is minimal: `verbose`, `exit_req`, the skeleton pointer, and the link. BPF state is reset on a full skeleton destroy/reopen except when the kernel requests a controlled restart, in which case the program jumps back to load a fresh instance. Printed allocator `arena_pages_used` is read but, in the BPF source viewed here, not visibly updated, so it may stay zero unless maintained by included arena helpers.

Dependencies and integration points: depends on libbpf, generated skeletons, `scx/common.h`, `scx_sdt.h`, and kernel sched_ext support. It must run with privileges sufficient to attach sched_ext struct_ops.

Risks: the program does not validate the returned `link` pointer beyond the macro behavior, so failures are macro-dependent. Its stats are raw monotonic counters without rate calculation. Because it sleeps one second, shutdown has up to one second latency. It also assumes all expected BSS symbols exist and match the BPF object.

Test signals: `-h` should print usage, `-v` should enable libbpf debug logging, and a successful run should print both scheduling and allocation sections repeatedly. Restart behavior can be observed by causing sched_ext to request restart and checking the loader reopens instead of exiting.
