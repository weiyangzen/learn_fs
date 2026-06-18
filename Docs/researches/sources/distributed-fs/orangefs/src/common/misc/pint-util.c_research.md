# sources/distributed-fs/orangefs/src/common/misc/pint-util.c

Purpose: Implements internal OrangeFS utility primitives used across client/server code: wall/user/system timing, message-tag allocation, deep copy/free of `PVFS_object_attr`, object-type names, time helpers, BMI address/layout request encoding, alias guessing, and Windows `statfs` shims.

Important APIs and functions: `PINT_time_mark`/`PINT_time_diff` capture elapsed wall and CPU time. `PINT_util_get_next_tag` returns nonzero protocol message tags under `current_tag_lock`. `PINT_copy_object_attr` and `PINT_free_object_attr` own deep-copy and teardown for nested object attributes including distributions, datafile arrays, mirror arrays, symlink targets, directory hints, distributed-directory bitmaps/handles, and capabilities. `encode/decode_PVFS_BMI_addr_t` and `encode/decode_PVFS_sys_layout` bridge BMI addresses/layout lists into the request protocol. Time helpers expose seconds, milliseconds, microseconds, timestamp formatting, version packing, and absolute timespec construction.

Control flow: Attribute copy walks the source mask and allocates only masked dynamic fields, freeing destination-owned fields first when the destination already carries compatible mask bits. Encoding converts BMI handles through reverse lookup strings and bounds layout encodings against `PVFS_REQ_LIMIT_LAYOUT`. Windows `PINT_statfs_lookup` canonicalizes a path, extracts the root/UNC share, then fills a POSIX-like `struct statfs` from `GetDiskFreeSpace`.

State and persistence: Process-local state is limited to the static message tag counter/mutex. Attribute routines transfer heap ownership but do not persist. Time and encoding helpers are stateless. Windows filesystem statistics are read live from the OS.

Dependencies and integration points: Includes `pvfs2-internal.h`, generated request-protocol encoders, `gen-locks`, BMI, gossip logging, security capability helpers, distribution utilities, distributed-directory helpers, and byte-swap code. The functions are used by request construction, metadata caches, setattr/getattr paths, and platform abstraction code.

Risks: `PINT_copy_object_attr` can leak partially allocated fields on mid-copy failure unless callers free the destination. Some nested copies assume valid source pointers when length fields are positive. Windows `PINT_time_mark` appears to assign user time from the system `FILETIME` value rather than the user value. `decode_PVFS_sys_layout` asserts allocation success instead of returning an error. `PINT_util_get_timeval_diff` returns microseconds in `int`, so long intervals can overflow.

Test signals: Exercise deep-copy/free round trips for every attr mask combination, including partial allocation failures. Test tag wraparound around `PINT_MSG_TAG_INVALID`, BMI address encode/decode with unknown addresses, layout size-limit failure, Windows `statfs` for drive and UNC paths, and timing helpers for monotonic positive deltas.
