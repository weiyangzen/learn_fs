## sources/distributed-fs/eos/mgm/ofs/cmds/Stat.inc

Purpose: implements stat/lstat and checksum retrieval for files and containers, translating EOS namespace metadata into POSIX `struct stat` plus XRootD-specific tape/offline flags.

Important APIs and types: public `XrdMgmOfs::stat` overloads, `_stat`, `_stat_set_flags`, `_getchecksum`, `lstat`, `eos::Resolver::retrieveFileIdentifier`, `Prefetcher`, `IFileMD`, `IContainerMD`, `LayoutId`, `Quota::MapSizeCB`, `calculateEtag`, and `appendChecksumOnStringAsHex`.

Control flow: public `stat()` namespace-maps and authorizes `AOP_Stat`, maps identity in stat mode, applies read access/stall and redirect except for the master proc path, calls `_stat()`, sets tape/offline flags on success, and may attempt ENOENT redirect/stall handling on missing paths. `_stat()` handles the master proc path only on a master MGM, enforces public access policy, prefetches the item, takes a read lock, and first attempts file lookup. It supports `/.fxid:` inode addressing, rejects a file stat with trailing slash as `EISDIR`, optionally returns URI and checksum, then fills POSIX fields from file metadata. If no file is found, it attempts container lookup and fills directory stat fields.

File metadata behavior: file stat sets device, inode derived from fid, mode from metadata, nlink from layout redundancy and disk/tape locations, size, uid/gid, block size, quota-mapped block count, ctime/mtime/atime including nanoseconds, optional etag, and optional checksum. Tape mode sets `XRDSFS_HASBKUP`, and files with no disk copies but nonzero size set `XRDSFS_OFFLINE`.

Directory metadata behavior: directory stat sets inode from container id, mode, uid/gid, tree size, `st_blksize` as child count, ctime/mtime, and atime as tree-modification time when sync-time accounting is enabled. Etag is calculated from container metadata and checksum is returned empty for directories.

State and persistence behavior: read-only except stats counters and prefetch/cache effects. It does not perform normal ACL checks for stat for performance, but does enforce public-access restrictions.

Dependencies and integration points: used by XRootD stat/lstat, share-path validation, versioning, and checksum queries. Integrates with namespace resolver, metadata services, quota size mapping, layout encoding, tape constants, and redirect/stall macros.

Risks: stat intentionally bypasses ACL checks, making public-access policy the main read guard here. `/.fxid:` lookup bypasses path traversal and must remain restricted by public-access and caller context. File trailing slash detection uses `std::string(path).back()` and assumes non-empty path. `lstat()` behaves like `stat()` and follows the same implementation.

Test signals: regular file stat, symlink/follow behavior, directory stat, missing path, `/.fxid:` lookup, file path with trailing slash, master proc path on non-master, tape-only/offline flags, etag for hardlink attribute, checksum output, public-access denial, and platform-specific nanosecond fields.
