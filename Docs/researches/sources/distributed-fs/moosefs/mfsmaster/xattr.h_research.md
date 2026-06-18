# sources/distributed-fs/moosefs/mfsmaster/xattr.h

Purpose: declares the MooseFS master xattr subsystem interface used by filesystem and metadata code.

Important APIs/types/functions: the header exports validation (`xattr_namecheck()`), inode cleanup (`xattr_removeinode()`), CRUD/list calls (`xattr_setattr()`, `xattr_getattr()`, `xattr_listattr_leng()`, `xattr_listattr_data()`), packed transfer helpers (`xattr_getall()`, `xattr_check()`, `xattr_setall()`), duplication (`xattr_copy()`), lifecycle (`xattr_cleanup()`, `xattr_init()`), and persistence (`xattr_store()`, `xattr_load()`).

Control flow: callers initialize the subsystem with `xattr_init()`, mutate per-inode xattrs through the setter/copy/remove APIs, serialize or reload metadata through `xattr_store()`/`xattr_load()`, and release all memory through `xattr_cleanup()`. Listing is a two-step API: first ask for size and opaque node pointer, then copy list data with that pointer.

State/persistence: the header itself has no state, but it exposes APIs that operate on the xattr hash table and metadata stream. The `bio` include makes persistence part of the public contract.

Dependencies/integration: includes `<inttypes.h>` and MooseFS `bio.h`; all returned status values are MooseFS protocol statuses defined outside the header. It integrates with filesystem inode lifecycle, metadata save/load, and client-facing xattr protocol handling.

Risks/test signals: consumers must preserve the `void *xanode` cursor only across a stable list operation and must pass packed buffers that match `xattr_getall()` layout. Tests should verify header prototypes stay synchronized with implementation and that callers handle `uint8_t` status/error returns rather than POSIX `errno` values.
