# sources/distributed-fs/ceph-client/include/asm-generic/bitops.h

Purpose: Aggregates generic bit operation implementations for architectures that use the C-language fallback bitops stack.

Important APIs, types, and functions: Includes generic implementations for `__ffs`, `ffz`, `fls`, `__fls`, `fls64`, scheduler bitops, `ffs`, hweight, lock bitops, atomic bitops, non-atomic bitops, little-endian bitops, and ext2 atomic helpers. Enforces inclusion through `<linux/bitops.h>`.

Control flow: Include-time composition only; direct include triggers `#error` unless `_LINUX_BITOPS_H` is set.

State and persistence: No state; operations act on caller bitmaps/words.

Dependencies and integration points: Depends on irq flags, compiler helpers, barriers, and the Linux bitops wrapper. Used by bitmaps, filesystems, schedulers, locks, and drivers.

Risks and test signals: Risks include direct include misuse, mismatched atomic/non-atomic semantics, endian confusion, and architecture overrides conflicting with generic helpers. Test bitmap/bitops selftests, ext2 bitmap updates, lock bitops, and include hygiene.
