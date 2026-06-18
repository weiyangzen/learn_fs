# sources/distributed-fs/ceph-client/net/psample/Makefile

## Purpose
The Makefile maps `CONFIG_PSAMPLE` to the `psample.o` object.

## Important APIs, types, and functions
`obj-$(CONFIG_PSAMPLE) += psample.o` is the only build rule. It creates either built-in or module psample support according to the Kconfig symbol.

## Control flow and state
There is no runtime control flow. Build inclusion controls availability of the generic netlink packet sampling channel and exported APIs.

## Dependencies and integration points
The rule is consumed by Kbuild and must stay aligned with the Kconfig symbol and `psample.c` module metadata.

## Risks and edge cases
Risks are limited to build integration: wrong object name or symbol would break module builds or users of exported psample APIs.

## Test signals
Compile with `CONFIG_PSAMPLE=m` and confirm `psample.ko`; compile built-in and disabled variants for link coverage.
