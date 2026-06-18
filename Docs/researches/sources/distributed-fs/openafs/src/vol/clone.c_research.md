## sources/distributed-fs/openafs/src/vol/clone.c

Purpose: volume clone implementation for copying vnode index metadata from an original read/write volume into a clone or reclone target while managing inode reference counts and directory clone flags.

Important APIs/types/functions: exported `CloneVolume()` clones both large and small vnode indexes and copies the volume header. `DoCloneIndex()` performs the per-vnode-class clone/reclone work. `struct clone_head` and `struct clone_items` batch old clone inodes that should be decremented after the new index is safely written and synced. `ci_InitHead()`, `ci_AddItem()`, `ci_Apply()`, and `ci_Destroy()` manage that batch list. `IDecProc()` applies `IH_DEC()` to queued inodes. `vol_PollProc`/`DOPOLL` integration allows long clone operations to yield/progress.

Control flow: `CloneVolume()` decides whether this is a reclone (`new == old`), clones `vLarge` then `vSmall`, logs filecount/diskused changes, and copies the disk volume header. `DoCloneIndex()` opens original and clone vnode index streams, optionally opens the existing clone for reading, walks original vnode records, increments referenced inodes when needed, marks original directory vnodes as cloned, writes the clone vnode record with `cloned = 0`, queues obsolete clone inodes for later decrement, truncates the clone index during reclone, syncs the target index, then decrements queued old inodes.

State and persistence: mutates vnode index files, inode link counts, original directory `cloned` flags, clone index length, and original volume counters (`V_filecount`, `V_diskused`) when `ReadWriteOriginal` is true. It uses inode handles from volume structures and fsync/truncate operations to make the clone index durable before old references are dropped.

Dependencies: volume/vnode/partition/inode handle APIs (`IH_OPEN`, `IH_INC`, `IH_DEC`, `FDH_*`, `STREAM_*`, `VNDISK_*`), `VnodeClassInfo`, `CopyVolumeHeader`, logging/panic helpers from `common.c`, and OpenAFS poll macros.

Integration points: called by volume server/salvage workflows that create or refresh clone/backup/readonly volumes. It is built into `vlib.a` and linked into volume tools via `Makefile.in`.

Risks: inode reference count ordering is safety-critical: failures after `IH_INC()` must decrement immediately or queue later decrements only after durable replacement. Recloning reads and writes the same clone index through separate streams and assumes it never reads data being simultaneously written. Directory `cloned` rollback is best-effort if a later write fails. `ReadWriteOriginal` is hard-coded true with a comment about readonly fileserver behavior. Memory allocation failure in `ci_AddItem()` panics the process.

Test signals: clone and reclone volumes with large/small vnode classes; directory and file vnodes; unchanged clinode matching rwinode; stale clone inodes that must be decremented; write/seek/IH_INC/IH_DEC/truncate/sync failure injection; filecount/diskused recomputation; old clone tail truncation; and verification that original directory clone bits are set or rolled back correctly.
