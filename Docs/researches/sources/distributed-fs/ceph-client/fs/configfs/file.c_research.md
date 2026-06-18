# sources/distributed-fs/ceph-client/fs/configfs/file.c

Purpose: implements configfs regular and binary attribute file operations and helpers to attach attribute dirents to config items.

Important APIs/types/functions: `struct configfs_buffer` stores per-open buffer state, item/attribute pointers, module owner, read/write mode flags, binary buffer, and mutex. `configfs_read_iter()` and `configfs_write_iter()` serve text attributes through `show()` and `store()`, with a fixed 4096-byte simple-attribute limit. `configfs_bin_read_iter()` and `configfs_bin_write_iter()` handle variable-size binary attributes with optional `cb_max_size`; binary writes are committed on `release`. `__configfs_open_file()` validates fragment liveness, permissions, callbacks, and module references. `configfs_create_file()` and `configfs_create_bin_file()` create attribute dirents.

Control flow: open takes the fragment read semaphore, rejects dead fragments, resolves parent item and attribute, pins the attribute owner module, checks requested read/write support, and stores a buffer in `file->private_data`. Text reads fill once then copy to userspace; text writes copy a whole buffer and call `store()`. Binary reads first query size with `read(item, NULL, 0)`, allocate, then read data. Binary writes grow an in-memory buffer and call `write()` at close.

State and persistence: per-open buffers are transient. Attribute values are owned by client subsystems. `frag_dead` makes callbacks return `-ENOENT` during teardown.

Dependencies/integration: depends on configfs dirents/fragments, public `configfs_attribute` and `configfs_bin_attribute`, module refcounting, VFS iov_iter APIs, and `dir.c` population.

Risks: text partial writes are intentionally unsupported; callers must write complete values. Binary read/write modes cannot be mixed on one open. Large binary buffers can consume memory up to `cb_max_size`. Fragment locking protects object lifetime but client callbacks must still validate their own state.

Test signals: text show/store limits, write without store, read without show, open during unregister, binary size query/fill, binary write commit on release, `cb_max_size` enforcement, module unload while file open, and concurrent readers/writers on separate opens.
