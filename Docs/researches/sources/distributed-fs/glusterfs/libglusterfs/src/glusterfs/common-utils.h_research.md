# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/common-utils.h

## Purpose
`common-utils.h` is a broad foundational header for libglusterfs. It defines constants, validation/logging/assertion macros, bit helpers, iovec utilities, time formatting/diff helpers, path/network/string parsing prototypes, thread helpers, hashing, fd closing helpers, and many cross-subsystem utility declarations.

## Important APIs, Types, and Functions
- Constants: size units, process modes, port ranges, time units, hidden paths, thread name limits, lease buffer sizes, shard GFIDs, special client PIDs, IPC targets.
- Macros: `alloca0`, `min`, `max`, `gf_roof`, `gf_floor`, `VALIDATE_OR_GOTO`, `GF_VALIDATE_OR_GOTO`, xattr guards, `GF_ASSERT`, `GF_STATIC_ASSERT`, `GF_ABORT`, `GF_UUID_ASSERT`.
- Inline helpers: bit-array set/clear/value, iovec duplicate/free/length/subset/skip/copy/load/unload, zero-filled checks, time formatting, thread-name wrapper, `gf_time`, `gf_tvdiff`, `gf_tsdiff`.
- Types: `dht_changelog_rename_info_t`, DNS cache structs, `list_node`, `iov_iter_t`, `token_iter_t`, socket union.
- Prototypes: string-to-number/bytesize/bool/time parsers, IP/hostname validation, UUID/lkowner/lease formatting, path utilities, reserved port parsing, local address checks, xxhash/GFID generation, thread creation/name helpers, service-running checks, recursive rmdir/unlink, robust read/write, SHA256, xattr namespace validation, FOP string/int mapping, pipe/nanosleep helpers.

## Control Flow
Inline iovec helpers implement small iterator-style control flow over scatter/gather buffers. `iov_iter_init()` positions at an offset; `iov_iter_next()` advances through current and subsequent iovecs; `iov_range_copy()` copies between two iterator ranges; `iov_subset()` materializes a subrange into caller-provided or newly allocated iovecs. Time formatters lazily initialize static format arrays, choose local or UTC time from logging settings, and append timezone and microseconds where present.

## State and Persistence
Most items are macros/prototypes with no state. Inline time formatting uses static local pointers initialized once without explicit locking but only to constant arrays. Functions declared here may mutate filesystem paths, process resource limits, DNS caches, or files depending on implementation, but this header itself persists nothing.

## Dependencies and Integration Points
This header is included across libglusterfs and translators. It depends on pthreads, sockets, iovec, uuid, URCU compiler macros, mempool, compat uuid, iatt, logging messages, and many forward-declared Gluster types. It is a high-risk integration surface because API or macro changes affect many translation units.

## Risks and Edge Cases
- Macros can evaluate arguments more than once (`min`, `max`, path removal), so callers must avoid side-effect expressions.
- Validation macros rely on a visible `this` symbol in some contexts.
- `mem_0filled()` returns nonzero when data is not all zero, which is easy to misread from its name.
- Several inline helpers perform pointer arithmetic on `void *`, relying on compiler extensions.
- Header-wide changes can cause large rebuild and behavior changes.

## Test Signals
Tests should cover iovec iterator boundary conditions, zero-filled detection, time formatting in local/UTC modes, validation macro errno behavior through representative users, string/bytesize parsers in implementation, IP validation, GFID generation, robust read/write partial I/O, fd closing exceptions, and FOP string/int mappings.
