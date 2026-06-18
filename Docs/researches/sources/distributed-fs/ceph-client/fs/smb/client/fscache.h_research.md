# sources/distributed-fs/ceph-client/fs/smb/client/fscache.h

Purpose: declares the CIFS fscache interface and provides no-op stubs when `CONFIG_CIFS_FSCACHE` is disabled, allowing the rest of the client to call cache hooks unconditionally.

Important APIs and types: defines `struct cifs_fscache_volume_coherency_data` for share/volume coherency, `struct cifs_fscache_inode_coherency_data` for inode timestamp coherency, prototypes for super and inode cookie lifecycle functions, and inline helpers `cifs_fscache_fill_coherency`, `cifs_inode_cookie`, `cifs_invalidate_cache`, and `cifs_fscache_enabled`.

Control flow: when fscache is enabled, coherency filling snapshots inode ctime and mtime into little-endian seconds/nanoseconds fields. `cifs_inode_cookie` returns the netfs cookie embedded in `CIFS_I(inode)->netfs`. `cifs_invalidate_cache` packages current coherency and size and calls `fscache_invalidate` with caller-supplied invalidation flags. `cifs_fscache_enabled` queries the cookie state. When disabled, all lifecycle and invalidation functions become no-ops, the cookie accessor returns NULL, and enabled checks return false.

State and persistence behavior: the header defines the persistent coherency records that accompany cached CIFS data. The enabled path records cache state in the netfs inode context; disabled builds intentionally persist nothing and should not alter runtime behavior except missing cache acceleration.

Dependencies and integration points: includes Linux swap and fscache headers plus CIFS globals. It is included by file I/O, inode, and fscache implementation code. Invalidation flags passed by file paths include direct-write cases and general cache invalidation after remote or local coherency changes.

Risks: duplicate prototypes in the enabled section are harmless but make API drift easier to miss. Enabled and disabled builds have materially different behavior, so both need compile coverage. Timestamp-only inode coherency must remain aligned with the implementation and server metadata update rules. Callers must tolerate `cifs_inode_cookie()` returning NULL in disabled or failed-acquisition paths.

Test signals: build with `CONFIG_CIFS_FSCACHE=y` and `n`; direct-write invalidation via `cifs_invalidate_cache`; open/close use/unuse behavior; inode release clearing cookies; mtime/ctime coherency changes; and callers that use `cifs_fscache_enabled` to decide whether extra read access is needed for write-only opens.
