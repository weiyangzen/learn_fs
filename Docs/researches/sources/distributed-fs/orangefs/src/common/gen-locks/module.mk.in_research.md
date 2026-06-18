# sources/distributed-fs/orangefs/src/common/gen-locks/module.mk.in

Purpose: Build-fragment registration for generic lock support.

Important build variables: Sets `DIR := src/common/gen-locks` and appends `gen-locks.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`.

Control flow/state: Make fragment only.

Dependencies/integration: Ensures POSIX generic locks are available in common, server, and BMI library builds. Windows-specific `gen-win-locks.c` is not listed here, implying it is registered by another platform-specific path or build mechanism.

Risks: If no other fragment adds `gen-win-locks.c`, Windows builds using `__GEN_WIN_LOCKING__` will have unresolved symbols.

Test signals: Inspect configured Windows build source lists and POSIX/BMI link outputs for expected lock implementation objects.
