# sources/distributed-fs/ceph-client/include/asm-generic/archrandom.h

Purpose: Provides default no-hardware-random implementations for architecture random and seed APIs.

Important APIs, types, and functions: Defines `arch_get_random_longs()` and `arch_get_random_seed_longs()`, both `__must_check`, returning zero generated words.

Control flow: Always returns 0, signaling no architecture entropy source.

State and persistence: No state; no entropy is produced.

Dependencies and integration points: Used by the kernel random subsystem when an architecture does not override hardware random helpers.

Risks and test signals: Risks are callers ignoring the return value or assuming hardware entropy exists. Test random subsystem behavior on architectures using this fallback, boot entropy accounting, and compiler warnings for ignored `__must_check`.
