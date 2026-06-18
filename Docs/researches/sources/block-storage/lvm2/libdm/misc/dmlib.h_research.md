# File Research: sources/block-storage/lvm2/libdm/misc/dmlib.h

## Summary
Primary internal include for libdm source files. It defines symbol-version export macros, documents their use, includes public libdevmapper and utility headers, connects logging, and pulls in `unistd.h`.

## Main Contents
- `DM_EXPORT_NEW_SYMBOL(rettype, func, ver)`
- `DM_EXPORT_SYMBOL(func, ver)`
- `DM_EXPORT_SYMBOL_BASE(func)`
- GNU symbol-version implementations using either `__attribute__((__symver__))` or `.symver` assembly.
- Non-GNU fallback macros that compile without symbol versioning.
- Includes `libdm/libdevmapper.h`, `libdm/dm-tools/util.h`, and `libdm/misc/dm-logging.h`.

## Important Behavior
New default-version symbols get `@@DM_<ver>`, older compatibility symbols get `@DM_<ver>`, and base symbols can be bound to `@Base`. Compatibility implementations must use suffixed function names such as `_v1_02_104`.

When `GNU_SYMVER` is unavailable, version macros reduce to normal function definitions or empty declarations, preserving source compatibility without versioned exports.

## State and Lifetime
No runtime state. This header is intended to be included first by every library source file so symbol/export and logging definitions are consistently available.

## Risks
Symbol-version declarations require exact function prototypes and names. Incorrect use can create ABI breaks or missing exported versions, especially when adding backward-compatible implementations.
