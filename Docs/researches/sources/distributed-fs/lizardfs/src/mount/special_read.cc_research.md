## sources/distributed-fs/lizardfs/src/mount/special_read.cc

Purpose: implements read behavior for special files.

Important APIs: `InodeMasterInfo::read` returns the 14-byte master location/session/version buffer after optional proxy rewriting. `InodeStats::read` slices the per-open stats snapshot. `InodeOplog` and `InodeOphistory` read from oplog handles. `InodeTweaks::read` lazily snapshots `gTweaks.getAllValues()` into its `MagicFile` and returns requested slices. `special_read` dispatches by inode.

State and dependencies: uses file-handle state from `special_open`, mastercomm/masterproxy, stats snapshot buffers, oplog, tweaks, and operation logging. Reads return `std::vector<uint8_t>`.

Risks: oplog read constructs a vector from `buff` after `oplog_releasedata`; because release may unlock and allow ring mutation, this depends on the source bytes remaining valid long enough and should copy before release. Offset/size arithmetic casts around signed `off_t` and unsigned sizes need boundary tests. No range check before dispatch.

Test signals: partial reads at zero/middle/end for masterinfo/stats/tweaks, blocking oplog read heartbeat, proxy masterinfo rewrite, and concurrent tweak writes.
