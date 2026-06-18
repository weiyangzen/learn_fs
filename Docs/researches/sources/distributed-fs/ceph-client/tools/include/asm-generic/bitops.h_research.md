# sources/distributed-fs/ceph-client/tools/include/asm-generic/bitops.h

## Purpose

This umbrella header collects generic bit-operation helpers for the tools include environment.

## APIs, State, and Dependencies

It includes generic `__ffs`, `ffz`, `fls`, `__fls`, `fls64`, `hweight`, atomic bitops, and non-atomic bitops. It deliberately errors if included directly without `<linux/bitops.h>`, preserving the intended include layering. It has no state or runtime behavior.

## Risks and Test Signals

The risk is include-order drift: direct inclusion breaks by design, and consumers must get types, masks, and compiler attributes from `<linux/bitops.h>`. Tests are compile-only coverage of tools using bit iteration, hweight, set/clear/test helpers, and architecture overrides.
