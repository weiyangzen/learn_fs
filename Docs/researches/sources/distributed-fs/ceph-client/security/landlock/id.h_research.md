# sources/distributed-fs/ceph-client/security/landlock/id.h

## Purpose

`id.h` declares audit-only Landlock ID initialization and allocation functions, with no-op stubs when audit is disabled.

## Important APIs, Types, and Functions

With `CONFIG_AUDIT`, it declares `landlock_init_id()` and `landlock_get_id_range()`. Without audit, only an inline empty `landlock_init_id()` exists because IDs are unused.

## Control Flow

Setup calls `landlock_init_id()` unconditionally; compilation selects real or stub behavior. Audit domain creation calls `landlock_get_id_range()`.

## State and Persistence Behavior

The header stores no state. It gates access to `id.c`'s counter.

## Dependencies and Integration Points

It integrates `setup.c` and `domain.c` without forcing audit code into non-audit builds.

## Risks and Test Signals

Header/stub mismatch could break non-audit builds. Test `CONFIG_AUDIT=y` and `CONFIG_AUDIT=n` build combinations.
