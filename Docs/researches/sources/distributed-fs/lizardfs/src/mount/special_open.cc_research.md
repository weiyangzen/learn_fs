## sources/distributed-fs/lizardfs/src/mount/special_open.cc

Purpose: implements open behavior for special inode files.

Important APIs: `MASTERINFO`, `OPLOG`, and `OPHISTORY` require read-only access. Stats open allocates `InodeStats::sinfo`, initializes a mutex, snapshots all stats via `stats_show_all`, and stores it in `fi->fh`. Oplog/history opens allocate oplog handles with or without history. Tweaks open allocates a `MagicFile`. `special_open` dispatches by special inode index.

State and dependencies: stores per-open state in `LizardClient::FileInfo::fh`. Sets FUSE hints: masterinfo is cacheable, stats/oplog/history/tweaks use direct IO and no keep-cache.

Risks: if later operations fail, allocated `sinfo`, oplog handles, or `MagicFile` require release cleanup. No range check before table indexing. Stats snapshot allocation errors are mapped to out-of-memory.

Test signals: verify access modes, per-file `direct_io`/`keep_cache`, handle allocation, stats mutex lifecycle, and invalid inodes.
