# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/renameat.c

Purpose: Formats the `flags` argument for `renameat2(2)`.

Important APIs/types/functions: `syscall_arg__scnprintf_renameat2_flags` delegates to `renameat2__scnprintf_flags`, which includes `rename_flags_array.c` and defines a `RENAME_` string array.

Control flow: The syscall wrapper reads `arg->val` and invokes `strarray__scnprintf_flags`.

State and persistence: Stateless display code.

Dependencies and integration points: Depends on generated output from `rename_flags.sh` and perf beauty helpers. Bound into perf trace for renameat2 flags.

Risks: Unknown flags fall back numerically. The generated array must follow the bit-position convention used by the shared formatter.

Test signals: Trace `renameat2` with individual and combined flags, checking prefix behavior and numeric fallback.
