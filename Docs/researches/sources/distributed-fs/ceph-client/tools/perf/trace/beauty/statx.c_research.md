# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/statx.c

Purpose: Formats the `statx(2)` mask argument.

Important APIs/types/functions: `syscall_arg__scnprintf_statx_mask` delegates to `statx__scnprintf_mask`, which includes `statx_mask_array.c` and formats `STATX_*` bitmasks.

Control flow: The syscall wrapper reads `arg->val` and passes it through `strarray__scnprintf_flags` with prefix control.

State and persistence: Stateless display code.

Dependencies and integration points: Generated output comes from `statx_mask.sh`; the formatter is used by perf trace for statx.

Risks: Composite mask values such as `STATX_BASIC_STATS` are intentionally omitted by the generator, so output decomposes into individual bits. New bits require regeneration.

Test signals: Trace `statx` with basic, all, and individual masks; verify generated names and hex fallback for unknown bits.
