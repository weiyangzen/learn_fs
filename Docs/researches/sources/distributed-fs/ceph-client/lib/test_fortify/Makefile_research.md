
# sources/distributed-fs/ceph-client/lib/test_fortify/Makefile

## Purpose

This kbuild fragment builds every `*-*.c` fortify test source as a compile-time negative test and aggregates the logs into `test_fortify.log`.

## Important APIs, Types, And Functions

`cmd_test_fortify` invokes `test_fortify.sh` with the input source, output log, `nm`, compiler, normal C flags, and extra warning settings. Pattern rule `$(obj)/%.log` creates one log per test source. `cmd_gen_fortify_log` concatenates all per-test logs into a single summary log.

## Control Flow And State

The build disables the normal `fortify-source` warning suppression for this directory, builds test objects with `-Werror`, writes logs beside build outputs, and always builds the aggregate log. No runtime state exists.

## Dependencies And Integration Points

It depends on kbuild command tracking, `$(CONFIG_SHELL)`, `$(NM)`, `$(CC)`, the shared shell script, and the common header. It also sets `KASAN_SANITIZE := y` because some architecture configurations interact with `__NO_FORTIFY` and sanitizer flags.

## Risks And Test Signals

The rules rely on filenames encoding expected fortify warning symbols. Useful signals are per-test `.log` files beginning with `ok:` and an aggregate `test_fortify.log`; failures report missing expected compiler diagnostics or unresolved fortify symbols.
