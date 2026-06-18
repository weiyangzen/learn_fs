# sources/distributed-fs/ceph-client/tools/include/linux/find.h

## Purpose

This header exposes bitmap bit-search helpers for tools code, with small-constant inline fast paths and external generic implementations for larger bitmaps.

## APIs, State, and Dependencies

It can only be included through `<linux/bitmap.h>`. It declares `_find_next_bit`, `_find_next_and_bit`, `_find_next_zero_bit`, `_find_first_bit`, `_find_first_and_bit`, and `_find_first_zero_bit`. Inline public helpers check `small_const_nbits` and use `GENMASK`, `__ffs`, and `ffz` for one-word cases, otherwise delegate to external functions. There is no state.

## Risks and Test Signals

The header relies on proper bounds handling before calling undefined helpers like `__ffs` or `ffz`. Include layering is enforced with an error. Tests should cover empty, full, sparse, offset-at-size, and one-word versus multiword bitmap searches.
