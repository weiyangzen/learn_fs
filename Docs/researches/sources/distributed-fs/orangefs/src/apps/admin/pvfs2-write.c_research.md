<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-write.c -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-write.c

**Purpose:** `pvfs2-write` writes a zero-filled in-memory buffer to a Unix or OrangeFS destination for throughput and file-creation testing, similar to `dd if=/dev/zero`.

**Important APIs, types, and functions:** `struct options` stores stripe size, datafile count, buffer size, file size, destination, and timing flag. `parse_bytes()` supports K/M/G suffixes. `generic_open()` handles Unix open or PVFS create, including parent lookup and optional `simple_stripe` distribution setup. `generic_write()` wraps Unix `write` or `PVFS_sys_write` with a contiguous request. `make_attribs()` builds settable attributes from credentials and datafile count.

**Control flow:** The parser requires `dest_file file_size`, defaults to 10 MiB buffer, imports PVFS hints, initializes PVFS, resolves the destination, creates credentials, opens/creates the destination, allocates and zeros the buffer, writes chunks until requested size is reached, prints timings if requested, then cleans up.

**State and persistence:** It creates or truncates Unix files and creates PVFS files. PVFS destination overwrite is refused; Unix destination uses `O_TRUNC`. It writes zero bytes of the requested length and may leave partial files on failure.

**Dependencies and integration points:** It depends on sysint create/write, PINT path helpers, PVFS hints, distribution lookup, and local POSIX file I/O.

**Risks and edge cases:** The option string omits `f` even though there is a dead `case 'f'`; file size comes from positional arg. `sscanf("%lu", &uint64_t)` in `parse_bytes` is type-sensitive across platforms. `PVFS_Request_free` is not called on write error. `memset(&dest, 0, sizeof(src))` relies on same type. Tests should cover suffix parsing, Unix and PVFS destinations, existing PVFS target refusal, Unix truncation, stripe/datafile creation, partial write failures, and large file sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-write.c -->
