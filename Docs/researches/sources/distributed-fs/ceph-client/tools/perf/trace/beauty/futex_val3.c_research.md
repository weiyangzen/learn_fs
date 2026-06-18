# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/futex_val3.c

## Purpose
This formatter decodes the futex `val3` bitset argument, primarily recognizing the all-bits match-any sentinel.

## Important APIs, Types, And Functions
It defines fallback `FUTEX_BITSET_MATCH_ANY` as `0xffffffff` and implements `syscall_arg__scnprintf_futex_val3()`, exposed as `SCA_FUTEX_VAL3`.

## Control Flow
The formatter reads `arg->val` as an unsigned int. If it equals `FUTEX_BITSET_MATCH_ANY`, it prints `MATCH_ANY` with optional `FUTEX_BITSET_` prefix. Otherwise it prints the bitset numerically.

## State, Dependencies, And Integration
No persistent state and no argument masks are modified. It is used for futex operations whose `val3` argument carries a bitset, with masking controlled by `futex_op.c`.

## Risks And Test Signals
The fallback numeric format string is `%#xd`, which prints hexadecimal followed by a literal `d`; this may be intentional legacy output or a typo worth review. Tests should check both match-any and arbitrary bitset formatting.
