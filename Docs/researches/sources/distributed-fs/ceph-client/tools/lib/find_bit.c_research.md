## sources/distributed-fs/ceph-client/tools/lib/find_bit.c

Purpose: Implements generic bitmap search helpers for tools builds lacking architecture overrides.

Important APIs/functions: `_find_first_bit()`, `_find_first_and_bit()`, `_find_first_zero_bit()`, `_find_next_bit()`, `_find_next_and_bit()`, and `_find_next_zero_bit()`. Macros `FIND_FIRST_BIT` and `FIND_NEXT_BIT` share word-scanning logic.

Control flow: Search scans bitmap words until it finds a non-zero candidate word after optional preprocessing. Next-bit search masks off bits before `start`, increments word index, and returns `size` when not found.

State/persistence: Stateless and read-only over caller-provided bitmaps.

Dependencies/integration: Uses Linux bitops, bitmap masks, `BITS_PER_LONG`, `__ffs`, `min`, and `unlikely`. Functions are conditionally compiled only when macro versions are absent.

Risks: Callers must supply enough memory for the requested bit count. Behavior is word-size dependent. `_and` variants require both bitmaps to be equally valid for the range.

Test signals: Cover zero-sized and boundary-sized bitmaps, starts at/after size, first/last bits, zero-bit searches, cross-word searches, and 32/64-bit word builds.
