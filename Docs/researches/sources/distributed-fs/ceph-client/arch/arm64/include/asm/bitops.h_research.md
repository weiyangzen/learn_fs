## sources/distributed-fs/ceph-client/arch/arm64/include/asm/bitops.h

Purpose: arm64 bit operation facade. It enforces inclusion through `<linux/bitops.h>` and composes generic bit scanning, atomic, locking, endian, scheduler, and ext2 helpers.

Important APIs/types/functions: no local functions. It includes generic implementations for `ffs`, `fls`, `ffz`, hweight, atomic bitops, lock bitops, non-atomic bitops, little-endian bitops, and ext2 atomic set-bit helpers.

Control flow: compile-time include aggregation only.

State and persistence: no state; state changes happen in the generic atomic bitops that this header exposes.

Dependencies and integration: depends on `linux/compiler.h` and the generic bitops headers. It is the architecture hook for every kernel user of bitmaps, flags, and bit locks on arm64.

Risks: include-order violations or replacing a generic header can alter atomicity or endian behavior globally. Test signals include full arm64 builds, lib/bitmap tests, filesystem tests using ext2 bitops, lockdep, and atomic bitops stress.
