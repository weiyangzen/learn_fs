# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mode_t.c

Purpose: Formats `mode_t` arguments for syscalls such as `open`, `mkdir`, and permission-changing calls.

Important APIs/types/functions: `syscall_arg__scnprintf_mode_t` emits symbolic `S_*` file type and permission bits. Local fallback definitions cover common aggregate macros such as `S_IALLUGO`.

Control flow: The function iterates through aggregate and individual `S_*` macros using `P_MODE`, printing matching components with `|` separators and clearing handled bits. Unknown remaining bits are appended in hex.

State and persistence: No persistent state; only local formatting state.

Dependencies and integration points: It depends on POSIX stat mode macros and perf trace's syscall argument formatter macro `SCA_MODE_T`.

Risks: Aggregate macros are printed before individual bits, so output intentionally favors compact forms such as `S_IALLUGO`; tests must account for that ordering. If platform headers omit macros, fallback coverage is partial.

Test signals: Format file-type modes, permission-only modes, aggregate modes, and unknown high bits. Confirm `show_string_prefix` toggles `S_`.
