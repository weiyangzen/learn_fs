# sources/distributed-fs/eos/mgm/proc/user/Ls.cc

Purpose: implements legacy `ProcCommand::Ls()` for user namespace listing, including simple listing, long listing, globbing, backend status, checksums, inode printing, and optional directory-list cache.

Important APIs and types: uses `XrdMgmOfsDirectory`, `gOFS->_stat`, `_access`, `_readlink`, `common::Glob`, `Path`, `Timing::ToLsFormat`, `modeToBuffer`, `LayoutId`, UID/GID mapping, and an optional static `LRU::Cache` controlled by `EOS_MGM_LISTING_CACHE`.

Control flow: the handler decodes paths when requested, rejects too-long and too-deep paths, maps namespace aliases, applies token scope, parses options, detects globbing unless disabled, stats the target, resolves the URI, then either opens a directory or prepares a single-file listing from its parent. It iterates entries, applies hidden-file and glob filters, and formats either bare names or long records with mode, link count, owner/group, size, timestamp, symlink target, backend redundancy symbol, checksum, and inode fields.

State and persistence: read-only except `MgmStats` and the process-local LRU cache keyed by inode, mtime, and options. Cache hits are still gated by an access check.

Dependencies and integration: provides familiar `ls` semantics through the proc framework while relying on EOS namespace stat/readlink and identity mapping services.

Risks: output is capped at 1 GiB but built in memory, and formatting uses fixed buffers. Cache correctness depends on mtime/ino/options and does not include caller identity, though access is rechecked. Globbing returns `ENOENT` when no entries match. Tests should cover cache hit and invalidation behavior, glob and no-glob paths, file versus directory listing, symlink formatting, backend status mode, numeric IDs, hidden files, long output truncation, and token/path mapping failures.
