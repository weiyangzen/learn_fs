# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/check_cc.sh

## Purpose

`check_cc.sh` is a tiny compiler capability probe used by the x86 selftests Makefile to decide whether a compiler can build a given test program with a given set of flags.

## Important APIs, Types, and Functions

It accepts `CC`, `TESTPROG`, and remaining compiler flags. It invokes `$CC -o /dev/null "$TESTPROG" -O0 "$@"` with stderr suppressed.

## Control Flow

If `CC` is non-empty and the compile/link command succeeds, it prints `1`; otherwise it prints `0`. It always exits zero so Makefile variable assignment can consume the printed capability bit without failing the build.

## State and Persistence Behavior

No files are persisted because the output path is `/dev/null`.

## Dependencies and Integration Points

It depends on a shell and the selected compiler. The Makefile uses it for 32-bit, 64-bit, and `-no-pie` probes.

## Risks and Edge Cases

Compiler paths containing shell metacharacters are not protected because `$CC` is intentionally expanded as a command. Linker/runtime library failures are treated the same as compiler failures.

## Test Signals

The only signal is stdout `1` or `0`.
