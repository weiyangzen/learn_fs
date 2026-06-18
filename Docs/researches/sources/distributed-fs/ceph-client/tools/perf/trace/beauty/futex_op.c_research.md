# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/futex_op.c

## Purpose
This formatter decodes futex operation values and hides syscall arguments that are unused for a given futex command.

## Important APIs, Types, And Functions
It uses `FUTEX_CMD_MASK`, `FUTEX_PRIVATE_FLAG`, `FUTEX_CLOCK_REALTIME`, common futex operations, and fallback definitions for newer ops. The formatter is `syscall_arg__scnprintf_futex_op()`, exposed as `SCA_FUTEX_OP`.

## Control Flow
The function splits `op` into command and option bits, formats the command name or hex fallback, and sets `arg->mask` bits for unused timeout/uaddr2/val3 arguments depending on the command. It then appends `PRIVATE_FLAG` and `CLOCK_REALTIME` suffixes if set.

## State, Dependencies, And Integration
Runtime state mutation is the syscall argument mask, which affects later futex argument display in `perf trace`. The file depends on `linux/futex.h` and `beauty.h` conventions.

## Risks And Test Signals
Futex has command-specific argument meanings, so incorrect masks can make traces misleading. The formatter also needs updates for new futex commands. Tests should cover each command family, private/realtime modifiers, and unknown command fallback.
