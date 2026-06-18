## sources/distributed-fs/lizardfs/src/mount/special_write.cc

Purpose: implements writes to special files.

Important APIs: masterinfo, oplog, and ophistory reject writes with EACCES. Stats writes mark the per-open stats snapshot to reset counters on release and report all bytes written. Tweaks writes splice bytes into the per-open `MagicFile::value`, mark it written, and apply on release. `special_write` dispatches by inode.

State and dependencies: mutates only per-open `sinfo` or `MagicFile` state until release. Uses oplog for tracing.

Risks: stats reset is content-insensitive. Tweaks accepts sparse/offset writes and grows a string; malformed data is logged on release. The write function trusts `off + size` arithmetic and table index validity.

Test signals: writes to read-only internal files return EACCES; stats write triggers reset only after release; tweak offset writes compose expected string and update registered atomics after release.
