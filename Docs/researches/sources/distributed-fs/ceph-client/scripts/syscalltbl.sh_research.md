# sources/distributed-fs/ceph-client/scripts/syscalltbl.sh

Purpose: `syscalltbl.sh` generates a C-style syscall dispatch macro table from architecture syscall table input.

Important APIs, types, and functions: it accepts `--abis`, reads rows as `nr abi name native compat noreturn`, fills gaps with `__SYSCALL(n, sys_ni_syscall)`, emits `__SYSCALL_WITH_COMPAT`, `__SYSCALL_NORETURN`, `__SYSCALL_COMPAT_NORETURN`, normal `__SYSCALL`, or default `sys_ni_syscall` based on columns.

Control flow: `nxt` tracks the expected next number. If a row number is lower than `nxt`, the script reports unsorted/duplicate input and exits. For each gap it emits dummy rows, normalizes `compat=-` to unset, validates the optional `noreturn` token, emits the appropriate macro, and advances `nxt`.

State and persistence: writes the generated output file.

Dependencies and integration points: part of syscall wrapper/header generation for architectures. Depends on trusted table formatting and downstream macro definitions.

Risks: only decimal rows are selected by grep, unlike the number-header scripts. Error output for invalid `noreturn` is missing explicit stderr redirection in one branch. ABI regex is direct from caller input.

Test signals: tables with gaps, duplicate/unsorted numbers, compat entries, `-` compat placeholders, noreturn entries, and missing native symbols.
