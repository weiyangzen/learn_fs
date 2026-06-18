# sources/compression/zstd/tests/cli-tests/common/platform.sh

## Purpose

This shared shell helper normalizes platform variables for zstd CLI tests.

## Important APIs, Types, and Functions

It sets `UNAME`, `isWindows`, `INTOVOID`, `DEVDEVICE`, `MD5SUM`, `DIFF`, `hasMT`, and `NON_DETERMINISTIC`. Function `md5hash()` emits a 32-character hash line. It selects `/dev/random` on GNU, `/dev/zero` generally, `NUL` on Windows, platform-specific md5 commands, and `gdiff` on SunOS.

## Control Flow, State, and Persistence

At source time it probes multithreading by running `zstd -v -T2` and probes deterministic build status with `zstd -vv --version`. Results become shell variables for later tests.

## Dependencies and Integration Points

It depends on `uname`, `zstd`, `grep`, `md5sum` or `md5`, `dd`, and `diff`/`gdiff`. Many CLI tests source it directly or through other common helpers.

## Risks and Test Signals

Probe output is coupled to CLI diagnostics. `dd status=none` may not exist on some older systems. Tests should verify sourced variables on Linux, macOS, BSD, SunOS, and Windows shells.
