# sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/bitsperlong.h

## Purpose
Defines Alpha UAPI long width for tools builds.

## Important APIs, Types, And Functions
- Sets `__BITS_PER_LONG` to `64`.
- Includes `asm-generic/bitsperlong.h` for generic definitions.

## Control Flow
No runtime flow.

## State And Persistence
No state. It affects compile-time ABI constants.

## Dependencies And Integration Points
Used by tools UAPI headers to size masks and syscall-facing types for Alpha.

## Risks
Changing this breaks Alpha ABI assumptions in tools.

## Test Signals
Cross-compile tools for Alpha and verify `sizeof(long)` assumptions and generated masks.
