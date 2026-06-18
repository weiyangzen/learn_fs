## sources/distributed-fs/eos/mgm/ofs/fsctl/Drop.cc

Purpose: trusted fsctl handler for dropping a committed or failed replica from file metadata and filesystem views, including delete-on-close `dropall` behavior and optional I/O deletion reports.

Important APIs and types: `XrdMgmOfs::Drop`, `REQUIRE_SSS_OR_LOCAL_AUTH`, `Prefetcher`, `IFileMD`, `IContainerMD`, `IQuotaNode`, `IFsView`, `SymKey::ZDeBase64`, `Iostat`, FuseX refresh, and access-mode/stall/redirect macros.

Control flow: requires SSS/local authentication, marks write access, applies stall/redirect, logs the full environment, requires `mgm.fid` and `mgm.fsid`, converts fid from hex and fsid from decimal, prefetches filesystem file list and file-with-parents metadata, and takes the namespace write lock. If file metadata is already gone, it releases the lock and erases the fsview entry. If metadata exists, it loads `sys.fs.tracking`, parent container, and quota node, builds a list containing either the requested fsid or all locations when `mgm.dropall` is present, and processes each id.

Drop behavior: for each selected fsid, it unlinks linked locations and appends `-fsid` to tracking, removes unlinked locations and appends `/fsid`, optionally sends `DeleteExternal()` for `dropall`, persists tracking/file metadata and reloads the file, or erases stale fsview entries when metadata did not contain the fsid. If no linked or unlinked locations remain and this was a real update/dropall, it removes quota accounting, removes file metadata, updates parent mtime, persists parent, notifies directory service, releases the lock, and broadcasts parent FuseX refresh.

Report behavior: if `mgm.report` is supplied, it base64/zlib-decodes the report and writes it through `mIoStats`; decode failures are logged but do not fail the drop.

State and persistence behavior: mutates file location and unlinked-location lists, `sys.fs.tracking`, file store, fsview entries, quota accounting, file metadata deletion, parent mtime, directory notifications, FuseX cache state, and optional IoStat records.

Dependencies and integration points: called by FST/FUSE close/delete flows to reconcile failed writes or deleted replicas. Relies on trusted auth, filesystem view consistency, metadata services, quota manager, external deletion helper, and I/O report encoding.

Risks: many metadata operations are inside broad `catch (...)` blocks, which can hide partial failures. The handler logs full opaque environment, potentially including large reports. `dropall` iterates over current locations and then mutates/reloads the file; correctness depends on stable metadata semantics. Removal of file metadata occurs only when there was an update or dropall to avoid unlinking namespace files after secondary replica failures.

Test signals: missing fid/fsid error, missing metadata erases fsview entry, single-fsid linked drop, unlinked removal, stale fsview cleanup, `dropall` all-location removal and external deletes, final metadata removal with quota update, parent mtime/FuseX refresh, report decode/write, report decode failure, and auth gate.
