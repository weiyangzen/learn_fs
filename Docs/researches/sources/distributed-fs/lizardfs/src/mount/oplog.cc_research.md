## sources/distributed-fs/lizardfs/src/mount/oplog.cc

Purpose: implements an in-memory operation log backing special files for live operation log and operation history. It stores formatted log lines in a fixed-size circular buffer and lets readers hold handles with independent read positions.

Important APIs/types: `fhentry` tracks handle id, read position, refcount, and next link. `oplog_printf` overloads prepend timestamps and optional Lizard client uid/gid/pid context, then append to the ring via `oplog_put`. `oplog_newhandle`, `oplog_releasehandle`, `oplog_getdata`, and `oplog_releasedata` manage reader cursors.

Control flow: log writes lock `opbufflock`, wrap-copy into `opbuff`, advance `writepos`, and broadcast waiters. New history handles start either at zero or near `writepos - MAXHISTORYSIZE` aligned to the next newline; live handles start at current `writepos`. Reads find the handle, increment refcount, block up to one second for new data, return either a contiguous ring slice or `"#\n"` heartbeat, and intentionally leave `opbufflock` held until `oplog_releasedata`.

State and persistence: all log data is volatile process memory. The ring is 16 MiB with history capped at about 15 MiB. Time conversion caches localtime for the current hour under a separate mutex.

Dependencies and integration: special inode open/read/release uses handles for `OPLOG` and `OPHISTORY`; many mount operations call `oplog_printf`. Uses pthread primitives and `LizardClient::Context`.

Risks: callers must always call `oplog_releasedata` after `oplog_getdata` because the mutex remains locked. If a handle is invalid in `oplog_getdata`, the function returns without unlocking, which is a latent deadlock path if reachable. Returned buffers point into the ring and are valid only while the lock is held.

Test signals: no direct unit tests here. Important tests are concurrent writers/readers, history truncation alignment, timeout heartbeat, and invalid-handle behavior.
