# File Research: sources/block-storage/kvdo/vdo/int-map.h

Public interface for the integer-to-pointer map.

Key responsibilities:
- Documents `int_map` as a `uint64_t` to non-NULL pointer map.
- Declares opaque `struct int_map`.
- Declares allocation/free, size, get, put, and remove operations.

Dependencies:
- Includes `compiler.h` and `type-defs.h`.

Notable risks:
- Header documents expected constant-time operations but insertion can resize linearly.
- Values are not owned by the map and must not be NULL.
