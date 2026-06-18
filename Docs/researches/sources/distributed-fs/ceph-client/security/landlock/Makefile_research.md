# sources/distributed-fs/ceph-client/security/landlock/Makefile

## Purpose

The Landlock Makefile builds the single `landlock.o` LSM object from setup, syscall, object, ruleset, credential, task, filesystem, thread-sync, optional network, and optional audit sources.

## Important APIs, Types, and Functions

`obj-$(CONFIG_SECURITY_LANDLOCK) := landlock.o` declares the aggregate. Core objects include `setup.o`, `syscalls.o`, `object.o`, `ruleset.o`, `cred.o`, `task.o`, `fs.o`, and `tsync.o`. `net.o` is included under `CONFIG_INET`; `id.o`, `audit.o`, and `domain.o` are included under `CONFIG_AUDIT`.

## Control Flow

Kbuild links enabled objects into one LSM unit. Setup then calls per-area hook registration functions at boot.

## State and Persistence Behavior

No runtime state is represented. The build composition determines whether network mediation and audit logging code paths exist.

## Dependencies and Integration Points

The file connects Kconfig symbols to the source files used by `setup.c`. Optional file inclusion must match stub definitions in headers such as `net.h`, `audit.h`, and `id.h`.

## Risks and Test Signals

Missing optional objects can cause unresolved symbols or silently absent features. Test with `CONFIG_INET` on/off and `CONFIG_AUDIT` on/off, plus KUnit/selftest builds.
