# sources/distributed-fs/eos/mgm/proc/user/Fileinfo.cc

## Purpose

`Fileinfo.cc` implements file and directory metadata reporting for legacy `ProcCommand::Fileinfo()`. It supports text, monitoring key/value, environment, and JSON output; path, fid/fxid, pid/pxid, and inode addressing; file health classification; filesystem-location tables; and recursive JSON children for directories.

## Important APIs, Types, and Functions

`FileMDToStatus()` classifies file state as `hardlink`, `symlink`, `healthy`, `pending_deletion`, `locations::uncommitted`, `locations::incomplete`, `locations::overreplicated`, or FUSE-related states. `Fileinfo()` resolves the input and dispatches to `FileInfo()`, `DirInfo()`, `FileJSON()`, or `DirJSON()`. `FileInfo()` and `DirInfo()` produce text or monitoring output. `FileJSON()` and `DirJSON()` build JSONCPP objects and can write to `stdJson` or an output parameter.

## Control Flow

`Fileinfo()` maps paths unless an id-style argument is used, stats normal paths to determine file versus directory, converts FUSE inode values when requested, and dispatches by `mJsonFormat`. `FileInfo()` prefetches file metadata by id or path, locks the namespace view, retrieves and clones metadata, releases the lock, and formats requested fields. Non-monitoring output supports filters such as `-path`, `-fxid`, `-fid`, `-size`, `-checksum`, `-fullpath`, and `-proxy`; `-m` produces key/value monitoring output; `-env` dumps the file environment. `DirInfo()` mirrors this for containers. JSON functions prefetch metadata with parents, optionally lock, clone/read metadata, attach xattrs, etags, locations, children, and error objects.

## State and Persistence

This command is read-only for namespace metadata. It reads file/container attributes, locations, unlinked locations, timestamps, layout ids, checksums, etags, tree counters, and filesystem snapshots. It may invoke scheduler access calculations for proxy display, but does not persist scheduling decisions.

## Dependencies and Integration Points

It depends on `gOFS` namespace services, `eos::Prefetcher`, `Resolver`, `FileId`, `LayoutId`, checksum and etag utilities, `FsView`, `Scheduler::FileAccess`, table formatter helpers, JSONCPP, and container iterators. `ArchiveAddEntries()` depends on the monitoring `fileinfo -m` shape, especially `keylength.file`, `file`, xattr pairs, size, timestamps, layout, and checksum fields.

## Risks and Test Signals

Output format stability is critical because other commands parse it. The monitoring parser must preserve paths with spaces via `keylength.file`. JSON directory recursion can be expensive on large trees. Locking is intentionally minimized by cloning metadata before formatting, so tests should watch for stale but safe snapshots. The status classifier depends on location counts, tape fsid, unlinked locations, and `sys.fusex.state` suffix parsing. Test signals include path/id/inode resolution, detached metadata, symlink targets inside and outside EOS, hardlinks, all filter options, monitoring output with xattrs and alt checksums, JSON errors, filesystem location tables, proxy display, unlinked locations, directory tree counters, and recursive JSON children.
