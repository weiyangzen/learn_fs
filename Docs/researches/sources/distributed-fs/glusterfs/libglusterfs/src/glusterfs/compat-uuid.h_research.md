# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-uuid.h

## Purpose
`compat-uuid.h` wraps libuuid APIs behind `gf_uuid_*` inline functions so the rest of GlusterFS uses a consistent portability layer.

## Important APIs, Types, and Functions
- `gf_uuid_clear()`, `gf_uuid_compare()`, `gf_uuid_copy()`, `gf_uuid_generate()`, `gf_uuid_is_null()`, `gf_uuid_parse()`, `gf_uuid_unparse()`: one-to-one inline wrappers over libuuid.

## Control Flow
Each inline function immediately delegates to the corresponding libuuid function. The TODO comment leaves room for platform-specific implementations such as libc UUID support on NetBSD.

## State and Persistence
No internal state. UUID values are caller-provided buffers.

## Dependencies and Integration Points
Depends on `<uuid/uuid.h>`. Used across inode GFIDs, leases, path/GFID mapping, dictionary values, and common utility functions.

## Risks and Edge Cases
- Callers must provide correctly sized `uuid_t` and output buffers.
- `gf_uuid_unparse()` uses libuuid's default string case/format; code requiring lower/upper variants must be explicit elsewhere.
- Porting to platforms without libuuid requires filling in the compatibility TODO.

## Test Signals
Test parse/unparse round trips, null detection after clear, compare/copy semantics, generated UUID non-null behavior, and platform builds where libuuid differs or is absent.
