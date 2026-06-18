# sources/distributed-fs/ceph-client/tools/perf/util/string2.h

## Purpose

`string2.h` declares perf's miscellaneous string helper API.

## Important APIs, Types, and Functions

It exposes `graph_dotted_line`, `dots`, `perf_atoll()`, glob matching functions, `strisglob()`, `strtailcmp()`, integer-expression formatting helpers, tracepoint PID filter formatting, escaped/quoted scanning and duplication, `hex()`, and `strreplace_chars()`.

## Control Flow and Data Flow

The header's inline helpers route `asprintf_expr_in_ints()` and `asprintf_expr_not_in_ints()` to `asprintf_expr_inout_ints()` with the inclusion flag. `strisglob()` uses `strpbrk()` to detect glob metacharacters.

## State and Persistence Behavior

No state is declared beyond external constant string pointers. Functions returning `char *` generally allocate caller-owned memory.

## Dependencies and Integration Points

It depends on Linux string/types, sys/types for `pid_t`, stddef, and string. It is shared by filters, parsers, tracepoint tooling, and display code.

## Risks and Edge Cases

The header declares `asprintf__tp_filter_pids()` even though it is not implemented in the nearby `string.c`; link coverage must ensure another object supplies it or unused declarations remain harmless. Callers must free allocated return strings and handle NULL.

## Test Signals

Compile/link coverage plus unit tests for each declared helper validate the contract.
