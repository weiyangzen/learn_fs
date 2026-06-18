# sources/distributed-fs/moosefs/mfschunkserver/hddspacemgr.c

## Purpose
`hddspacemgr.c` is the MooseFS chunkserver storage manager. It owns the in-memory catalog of local chunk files, per-disk folder state, disk space accounting, chunk read/write/open/close primitives, chunk lifecycle mutations, disk scanning, health/error reporting, duplicate cleanup, background chunk testing, and disk-to-disk rebalancing.

The module is the boundary between chunkserver protocol/job code and the filesystem layout used for chunk storage. Chunk files live below configured HDD roots in `00` through `FF` subdirectories and are named `chunk_%016PRIX64_%08PRIX32.mfs`. Each file contains a MooseFS chunk header, a 4096-byte CRC table, and up to one chunk of data blocks.

## Important APIs, Types, And Functions
The public API is declared in `hddspacemgr.h`.

Main exported status/reporting APIs include `hdd_stats()`, `hdd_op_stats()`, `hdd_get_chart_data()`, `hdd_errorcounter()`, `hdd_clear_errors()`, `hdd_sendingchunks()`, `hdd_spacechanged()`, `hdd_get_space()`, `hdd_is_rebalance_on()`, `hdd_diskinfo_size()`, `hdd_diskinfo_data()`, `hdd_diskinfo_monotonic_size()`, and `hdd_diskinfo_monotonic_data()`.

Master registration/report queues are exposed through `hdd_get_damaged_chunk_count()/data()`, `hdd_get_lost_chunk_count()/data()`, `hdd_get_new_chunk_count()/data()`, `hdd_get_changed_chunk_count()/data()`, `hdd_get_nonexistent_chunk_count()/data()`, `hdd_get_chunks_begin()/next_list_count()/next_list_data()/end()`, and `hdd_regfirst()`. Several of these APIs intentionally act as lock/unlock pairs: callers first ask for a count while the module holds `dclock` or `hashlock`, then call the data function to fill a packet and release the lock.

The core I/O API is `hdd_open()`, `hdd_close()`, `hdd_read()`, `hdd_write()`, `hdd_precache_data()`, `hdd_emergency_read()`, and `hdd_get_chunk_info()`. Internally `hdd_io_begin()` opens a chunk file and loads or initializes the CRC table, and `hdd_io_end()` writes dirty CRCs, updates reference counts, and schedules delayed descriptor/CRC/block cleanup.

Chunk mutation is funneled through `hdd_chunkop()`. Its encoded operation matrix dispatches to `hdd_int_create()`, `hdd_int_delete()`, `hdd_int_test()`, `hdd_int_version()`, `hdd_int_duplicate()`, `hdd_int_truncate()`, `hdd_int_duptrunc()`, and `hdd_int_split()` for erasure-coded part generation. `hdd_rep_setversion()` finalizes a replicated chunk that was created with version zero.

The main internal types are:

- `chunk`: one local chunk record, including `chunkid`, `version`, owner folder, subdirectory `pathid`, block count, header size, disk usage, open fd, loaded CRC table, optional preserved block buffer, damage flag, test-chain links, and a `CH_AVAIL`/`CH_LOCKED`/`CH_DELETED` state.
- `folder`: one configured storage path, including scan/removal/rebalance states, usable/total space, mark-for-removal mode, limit mode, statistics, recent errors, chunk vector, test queues, known disk usage samples, duplicate removal queue, and lock fd metadata.
- `cfgline`: preserves configured HDD lines and points to the matching `folder`.
- `waitforremoval`: tracks duplicate chunk files that should be kept temporarily before unlinking.
- `calc_space_data`: cached global space and disk-count summary sent to master/charts.
- Block-list queue structs such as `damagedchunk`, `lostchunk`, `newchunk`, `chgchunk`, and `nonechunk`: accumulate reports for the master.

Important global locks are `folderlock` for `folderhead` and folder fields, `hashlock` for `hashtab` and chunk lock state, `testlock` for test queues, `dclock` for master report queues and global space flags, `statslock` for counters, `doplock`/`ndoplock` for delayed-open cleanup queues, and `termlock` for background-thread termination.

## Control Flow
Initialization starts in `hdd_init()`. It clears hash tables, creates thread-local buffers when block preservation is disabled, computes the empty-block CRC table, reads options via `hdd_options_common(1)`, parses configured disks with `hdd_folders_reinit()`, computes the open-file limit, and registers reload, exit, timer, destructor, and info hooks with `main_*`. `hdd_late_init()` then starts six worker threads: known disk usage, tester, folder checker, standard rebalance, high-speed rebalance, and delayed cleanup.

Configuration reload flows through `hdd_reload() -> hdd_options_common(0) -> hdd_folders_reinit()`. Reinit temporarily disables folder actions, marks existing folders for removal, clears `cfgline` entries, reparses the HDD config file, binds or creates `folder` objects through `hdd_parseline()`, then re-enables folder actions. `hdd_parseline()` handles path prefixes (`*`, `~`, `>`, `<`), size/percent limits, `.metaid` validation, `.lock` creation and `lockf()`, duplicate physical-device warnings, read-only mark-for-removal behavior, and rescan/resend decisions for existing folders.

Disk scanning is scheduled by `hdd_check_folders()`. A folder in `SCST_SCANNEEDED` starts `hdd_folder_scan()`, and a folder in `SCST_ATTRNEEDED` starts `hdd_folder_update_attr()`. Scanning first attempts `hdd_folder_fastscan()` using `.chunkdb`; if that is invalid or absent, it creates/accesses `00`..`FF`, migrates older one-hex-directory layouts, walks chunk filenames, and calls `hdd_add_chunk()`. The scanner reports progress via `hddspacerecalc`, shuffles test queues, and transitions to `SCST_BGJOBFINISHED`; `hdd_check_folders()` joins the worker and returns the folder to `SCST_WORKING`.

Normal chunk I/O first locks a `chunk` with `hdd_chunk_get()` or `hdd_chunk_tryfind()`. Lock contention waits on reusable condition objects with a timeout, returning `MFS_ERROR_NOTDONE` for many operations. `hdd_open()` and `hdd_close()` bracket higher-level sessions. `hdd_read()` verifies versions, ranges, and CRCs; reads missing logical blocks as zeroes; supports partial-block reads by reading the full block and combining CRCs; and reports CRC/read errors as damaged chunks. `hdd_write()` verifies caller CRCs, optionally sparsifies new zero regions, extends block counts, updates per-block CRCs, truncates partial new blocks when needed, and marks CRC/disk usage dirty.

Chunk lifecycle operations update both filesystem files and in-memory indexes. Create chooses a writable folder with `hdd_getfolder()`, allocates a `chunk`, creates the file exclusively, writes a new-format header plus empty CRC table, and enqueues it for delayed cleanup. Version and truncate operations rename files and update header version fields before data/CRC changes. Duplicate and duplicate-truncate operations create a target chunk, copy and sparsify source data, copy or rebuild CRCs, and clean up partial targets on error. Delete removes queued duplicates first, unlinks the active file, and removes the chunk from folder, test, and hash structures. Split creates EC4 or EC8 data/parity chunks, reads source block groups, writes missing parts plus XOR parity, sets final versions, and unwinds created chunks on failure.

Folder health and reporting are driven by `hdd_check_folders()`. It handles removal state transitions, sends lost chunks while removing a disk, refreshes space with `statvfs()`, marks disks damaged after repeated EIO/EROFS/ENOENT errors within configured tolerances, drains duplicate-removal queues after the configured hold time, recalculates global `calc_space_data`, and raises `hddspacechanged` for the master.

Rebalancing runs in two modes. Standard `hdd_rebalance_thread()` chooses a source and destination via `hdd_rebalance_find_servers()`, calls `hdd_int_move()` synchronously, and throttles according to `HDD_REBALANCE_UTILIZATION`. High-speed `hdd_highspeed_rebalance_thread()` schedules `job_chunk_move()` jobs up to `HDD_HIGH_SPEED_REBALANCE_LIMIT`. Selection honors forced source/destination flags, usage imbalance thresholds, read/write distribution correction, duplicate queues on destinations, recent rebalance grace period, and folder health.

Termination uses `hdd_wantexit()` to stop folder actions and `hdd_term()` to set `term`, join workers, terminate or join active scans, wait briefly for rebalance jobs, dump `.chunkdb` records for valid folders, flush open CRCs and descriptors, close lock fds, and free all queues and structures.

## State, Persistence, And Dependencies
Persistent chunk data is stored as regular `.mfs` files. Header format validation happens in `chunk_readcrc()`, which accepts MooseFS chunk signatures `C 1.0` and `C 1.1`, verifies embedded chunk id/version, reads the CRC table, and validates empty-block CRCs for newer files. Header sizes may be old 1024-byte or new 4096-byte headers. The data region starts at `hdrsize + CHUNKCRCSIZE`.

Per-disk persistent side files include `.lock` for process exclusion and umount prevention, `.metaid` for MooseFS instance validation, `.chunkdb` as a fast-scan cache, and `.tmp_chunkdb` during atomic cache writes. `.chunkdb` version 4 stores records of chunk id, version, block count, header size, path id, tested flag, and disk usage, ending with an all-zero record. The cache is intentionally not written for damaged, read-only, or duplicate-pending disks.

Most long-lived state is in memory: `folderhead`, `cfglinehead`, a 16M-entry `hashtab` keyed by low chunkid bytes, delayed-open hashes, duplicate-removal hashes, report queues, global stats counters, and `global_csd`. Space accounting combines `statvfs()` availability, configured limits, `LeaveFree`, known disk usage sampling, inode limits, mark-for-removal accounting, and EC chunk counters.

The module depends on MooseFS-local utilities and protocols: `MFSCommunication.h` for constants/status codes and packet flags, `datapack.h` for binary packing, `crc.h` for CRC and combination functions, `cfg.h` for configuration, `masterconn.h` for meta id exchange, `main.h` for lifecycle hooks, `bgjobs.h` for async rebalance jobs, `lwthread.h` for thread creation, `ionice.h` for low-priority background work, and logging/assertion helpers. It depends on POSIX filesystem APIs including `open`, `read`, `write`, `pread`/`pwrite` or seek wrappers, `rename`, `unlink`, `stat`, `statvfs`, `fsync`/`F_FULLFSYNC`, `lockf`, `ftruncate`, `opendir`, and pthread mutexes/conds.

## Integration Points
`init.h` registers `hdd_init`, `hdd_late_init`, and `hdd_restore` in chunkserver startup. `masterconn.c` consumes space summaries, full/partial chunk registration lists, damaged/lost/new/changed/nonexistent queues, send-progress flags, per-chunk status, rebalance state, and meta id writes. `mainserv.c` uses the I/O API for client reads and writes, including precache and close handling. `replicator.c` uses create/open/write/setversion/close flows for incoming replication. `bgjobs.c` dispatches asynchronous chunk operations, reads, writes, info requests, open/close, and moves to this module. `csserv.c` exposes HDD list, monotonic disk info, and clear-errors operations to clients/admin tools. `chartsdata.c` samples stats, operation counters, space, EC chunk counts, disk health counts, and usage-diff data.

## Risks
Concurrency is the primary risk. The module mixes several lock domains, lock/unlock-pair APIs, per-chunk condition waits, background scanner/rebalance/test threads, and delayed descriptor cleanup. Any caller that skips the second half of a lock-pair API or calls it with mismatched buffers can leave internal locks held. New code must preserve existing lock order, especially around `folderlock`, `hashlock`, and `testlock`.

Filesystem mutation has multi-step failure windows. Version, truncate, duplicate, duplicate-truncate, split, and move operations combine header writes, CRC writes, renames, truncates, and in-memory state changes. Many paths try rollback or unlink partial files, but crashes between steps can leave duplicate files, stale `.chunkdb`, zero-version replication files, or headers whose filename and embedded version temporarily disagree.

Space accounting is approximate by design. It uses cached disk usage samples, statvfs values, inode limits, configured logical limits, and delayed refresh flags. Sparse writes and delayed `stat()` refreshes can make `avail`, `total`, and `diskusage` temporarily stale. A filesystem reporting changed total blocks or read-only flags can cause the disk to be marked damaged.

The duplicate-removal queue is conservative but operationally important. Duplicate files are kept for `HDD_KEEP_DUPLICATES_HOURS`; while pending, rebalance avoids the disk and `.chunkdb` is not trusted. Incorrect duplicate classification could either delete useful recovery data too early or keep disks out of rebalance too long.

CRC integrity is central. Reads and writes verify per-block CRCs, but partial writes must combine CRCs correctly, and sparse zero handling must preserve caller-visible zero data. Any change to block sizing, header sizing, or EC split mapping needs targeted CRC and recovery tests.

Resource limits matter. Open descriptors are capped at two thirds of `RLIMIT_NOFILE`, but delayed close keeps files open briefly. Large hash tables, chunk vectors, `.chunkdb` reads into memory, optional mmap allocation, and per-thread buffers can consume significant memory on large chunkservers.

## Test Signals
Good regression signals include startup scans from empty disks, populated disks, invalid `.chunkdb`, old one-hex directory layouts, read-only mark-for-removal disks, duplicate chunk versions, and mismatched `.metaid` files.

Chunk I/O tests should cover open/read/write/close, whole-block and partial-block reads/writes, writes beyond current length, zero-only sparse writes, CRC mismatch detection, wrong-version errors, block-number/offset/size bounds, forced fsync close, and emergency read error flags.

Chunk operation tests should cover create/delete, version rename/header update, truncate expansion and shrink with aligned and unaligned lengths, duplicate, duplicate-truncate, replication create plus `hdd_rep_setversion()`, EC4/EC8 split with selected missing masks, and cleanup after injected read/write/rename/truncate failures.

Operational signals include master reports for damaged/lost/new/changed/nonexistent chunks, `hddspacechanged` transitions after scans/removals/refreshes, diskinfo packet sizes and flags, charts counters, error tolerance damage marking, `hdd_clear_errors()`, rebalancing source/destination selection, high-speed rebalance limits, delayed descriptor/CRC cleanup, and shutdown writing reusable `.chunkdb` caches.
