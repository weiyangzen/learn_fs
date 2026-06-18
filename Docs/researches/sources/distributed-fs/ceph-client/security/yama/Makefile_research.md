# sources/distributed-fs/ceph-client/security/yama/Makefile

## Purpose

This Makefile builds the Yama LSM object when `CONFIG_SECURITY_YAMA` is enabled.

## Important APIs, types, and functions

It declares `obj-$(CONFIG_SECURITY_YAMA) := yama.o` and composes `yama-y := yama_lsm.o`.

## Control Flow

The Kbuild conditional includes or omits Yama based on the config symbol. There is no runtime logic.

## State and Persistence

No state is stored. The output is the linked `yama.o` built from `yama_lsm.o`.

## Dependencies and Integration Points

It depends on the Kconfig symbol from `Kconfig` and on `yama_lsm.c`. It integrates with the kernel security directory's recursive build.

## Risks and Test Signals

Risks are limited to build wiring. Tests should compile with `CONFIG_SECURITY_YAMA=y`, `m` if permitted by surrounding build rules, and `n` to verify no stale references.
