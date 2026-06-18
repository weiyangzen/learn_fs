
# sources/distributed-fs/ceph-client/lib/test_fortify/test_fortify.sh

## Purpose

This shell script is the per-test verifier for fortify compile-time failures. It compiles a given source and decides whether the expected fortify diagnostic was observed.

## Important APIs And Control Flow

The script derives `FILE`, `FUNC`, and expected symbol `WANT="__${FILE%%-*}"` from the source filename. It compiles with `-Werror`, capturing stderr to a temporary log. If compilation fails, it greps for an error mentioning the expected symbol. If compilation succeeds, it checks `nm` output for an unresolved reference to the expected symbol, which covers cases where the diagnostic is deferred.

## State, Dependencies, And Integration Points

It writes a temporary file beside the final log and removes it with a trap. It forces `LANG=C` so compiler messages use predictable punctuation. It depends on POSIX shell, the compiler, `nm`, `grep`, and the kbuild-provided argument list.

## Risks And Test Signals

The script is tightly coupled to filename conventions and compiler warning wording. It handles GCC and Clang's warning-attribute phrasing with a regex. Output beginning with `ok:` is success; output beginning with `warning:` is a test failure and includes compiler output for diagnosis.
