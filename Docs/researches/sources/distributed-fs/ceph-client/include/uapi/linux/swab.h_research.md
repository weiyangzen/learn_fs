# sources/distributed-fs/ceph-client/include/uapi/linux/swab.h

## Purpose
Provides byte-swap and halfword-swap helpers for UAPI and userspace code, with constant-folding, compiler builtins, and architecture-specific overrides.

## Important APIs, Types, and Constants
Constant macros include `___constant_swab16`, `___constant_swab32`, `___constant_swab64`, `___constant_swahw32`, and `___constant_swahb32`. Inline helpers include `__fswab16`, `__fswab32`, `__fswab64`, `__fswahw32`, and `__fswahb32`. Public macros/functions include `__swab16`, `__swab32`, `__swab64`, `__swab`, `__swahw32`, `__swahb32`, pointer forms `__swab16p`, `__swab32p`, `__swab64p`, `__swahw32p`, `__swahb32p`, and in-place forms `__swab16s`, `__swab32s`, `__swab64s`, `__swahw32s`, `__swahb32s`.

## Control Flow, State, and Persistence
The helpers are pure value transforms with no persistent state. Compile-time paths prefer compiler builtins or `__builtin_constant_p`; runtime paths use arch helpers or portable shifts.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<linux/stddef.h>`, `<asm/bitsperlong.h>`, and `<asm/swab.h>`. Used by endian conversion headers and wire-format parsers.

## Risks and Test Signals
Risks include signedness mistakes, unaligned pointer use by callers, wrong `__BITS_PER_LONG` path, and architecture override mismatch. Test constant and runtime values for 16/32/64-bit cases, pointer and in-place forms, 32-bit/64-bit builds, and compiler-builtin and no-builtin configurations.
