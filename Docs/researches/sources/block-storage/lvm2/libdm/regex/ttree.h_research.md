# File Research: sources/block-storage/lvm2/libdm/regex/ttree.h

Purpose: declares the internal fixed-length ternary-tree API used by libdm regex DFA state caching.

Read coverage: complete file read, 28 lines.

Key contents:
- Forward-declares opaque `struct ttree`.
- Declares create, lookup, and insert operations.
- Uses `unsigned int *` key vectors and untyped `void *` payloads.

Dependencies:
- Includes `libdm/misc/dmlib.h` for `struct dm_pool`.

Risk and edge cases:
- The API does not encode key length in calls after creation, so callers must provide keys matching the tree's configured `klen`.
- Payload lifetime is caller-owned; the tree only stores pointers.
