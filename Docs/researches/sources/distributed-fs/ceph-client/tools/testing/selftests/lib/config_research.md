# sources/distributed-fs/ceph-client/tools/testing/selftests/lib/config

## Purpose

`lib/config` declares kernel configuration dependencies for the selftests under `tools/testing/selftests/lib`.

## Important APIs, Types, and Functions

It lists `CONFIG_TEST_BITMAP=m`, `CONFIG_PRIME_NUMBERS=m`, and `CONFIG_TEST_BITOPS=m`. These are Kconfig symbols rather than executable code.

## Control Flow and State

There is no control flow. The file is consumed by kselftest tooling to determine required kernel features or modules.

## Dependencies and Integration Points

It integrates with config-check tooling and with `bitmap.sh`, whose module depends on these symbols.

## Risks and Test Signals

Risks are missing or wrong symbols causing false skips or build/load failures. Signals are config check output and successful loading of the bitmap-related test module.
