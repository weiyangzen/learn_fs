# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-timer.c

Purpose: provides a last-resort timing-jitter `RAND_METHOD` for non-Windows platforms.

Important APIs/types/functions: signal handler `sigALRM`, optional forked `pacemaker` when `setitimer` is unavailable, and callbacks `timer_seed`, `timer_bytes`, `timer_cleanup`, `timer_add`, `timer_pseudorand`, `timer_status`, plus `RAND_timer_method`.

Control flow: `timer_bytes` points global volatile state at the caller buffer, installs a SIGALRM handler, starts a 10 ms interval timer or child pacemaker, and repeatedly increments a counter while the signal handler XORs low counter bits into output bytes. It rotates each output byte and repeats four passes, then restores timer and signal state.

State and persistence: uses file-static volatile `counter`, `gdata`, `igdata`, and `gsize` during generation. No long-term state is retained and seed/add are no-ops.

Dependencies and integration points: depends on signals, timers/select/fork/wait depending on platform, `rand.h`, `roken`, and `randi.h`. Fortuna calls it only as a weak fallback entropy source.

Risks and test signals: signal handler global state is process-wide and not thread-safe, entropy quality is weak and environment-dependent, Windows reports unsupported, and the non-`setitimer` path contains old code paths that are hard to exercise. Tests should limit this to availability, nonzero output variation, signal restoration, and Fortuna fallback behavior.
