# sources/distributed-fs/ceph-client/kernel/exec_domain.c

Purpose: provides the remaining generic execution-domain/personality support. The historical dynamic exec-domain registry is gone; this file exposes a procfs compatibility view and the `personality(2)` syscall for per-task ABI personality flags.

Important APIs/types/functions: `execdomains_proc_show()` prints the static Linux domain line, `proc_execdomains_init()` creates `/proc/execdomains`, and `SYSCALL_DEFINE1(personality)` returns the old personality while optionally setting a new one through `set_personality()`.

Control flow: proc init creates a single generated proc entry. Reads always return the same Linux domain. The syscall snapshots `current->personality`, treats `0xffffffff` as query-only, otherwise updates the task personality, then returns the old value.

State and persistence: mutable state is `current->personality` in each task. Proc output is generated on demand and has no backing store. Personality changes persist in task state under normal inheritance rules handled elsewhere.

Dependencies and integration points: integrates syscall dispatch, task state, procfs, seq_file, and `linux/personality.h`. Compatibility runtimes and loaders depend on exact `personality(2)` ABI behavior.

Risks: the `0xffffffff` query sentinel must not be installed as a real personality. Any return-value or inheritance change is ABI-visible. `/proc/execdomains` is intentionally minimal and may surprise tools expecting legacy dynamic domains.

Test signals: syscall tests should verify query-only behavior, old-value returns, flag setting, inheritance behavior through fork/exec as covered elsewhere, and proc content when procfs is enabled.
