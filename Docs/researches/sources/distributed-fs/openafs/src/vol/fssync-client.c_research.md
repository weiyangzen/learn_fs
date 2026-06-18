# sources/distributed-fs/openafs/src/vol/fssync-client.c

Purpose: client-side implementation of the FSSYNC protocol, compiled when `FSSYNC_BUILD_CLIENT` is set. It lets volume utilities, salvagers, debug tools, and other non-fileserver processes coordinate with the fileserver's volume package through the generic SYNC transport.

Important APIs/types/functions: static `fssync_state` defines the FSSYNC endpoint, protocol version, retry limit, hard timeout, and protocol name. `FSYNC_clientInit`, `FSYNC_clientFinis`, and `FSYNC_clientChildProcReconnect` wrap SYNC connect/close/reconnect. `FSYNC_askfs` serializes requests through `vol_fsync_mutex` under pthread builds and normalizes logging for response classes. `FSYNC_GenericOp` builds a `SYNC_command` from a caller-supplied extension header. `FSYNC_VolOp`, `FSYNC_StatsOp`, `FSYNC_VGCQuery`, `FSYNC_VGCAdd`, `FSYNC_VGCDel`, and `FSYNC_VGCScan` are typed convenience wrappers. `FSYNC_VerifyCheckout` protects demand-attach checkout flows after a lock is obtained.

Control flow: callers initialize the client, fill or request a response buffer, and use a wrapper that sets `programType`, command, reason, total command length, and payload pointer. `FSYNC_askfs` sends the request via `SYNC_ask`, logs exceptional outcomes, and returns the generic SYNC result. Volume group updates funnel through `_FSYNC_VGCUpdate`; scans choose `FSYNC_VG_SCAN` or `FSYNC_VG_SCAN_ALL` depending on whether a partition was supplied. `FSYNC_VerifyCheckout` queries `FSYNC_VOL_QUERY_VOP`, interprets unknown volume or wrong partition as safe, treats missing or mismatched pending operations as a possible fileserver restart, and returns `SYNC_DENIED` when checkout should be retried.

State and persistence: client state is process-global in `fssync_state`. Under pthread builds, a single mutex protects the socket/channel state. No disk state is written by this file; persistence effects are indirect through server-side volume state changes.

Dependencies: generic SYNC APIs, `fssync.h`, volume package globals such as `programType`, logging, partition/volume definitions, and OpenAFS threading primitives. The code assumes protocol payload structs from `fssync.h` match the server ABI.

Integration points: called by volume utilities, salvagers, `fssync-debug.c`, and conversion helpers in `listinodes.c`. It is the narrow client boundary between external utilities and the fileserver's in-memory volume registry.

Risks: a single static socket state makes calls process-global and requires reconnect after fork. `FSYNC_GenericOp` trusts caller-supplied payload length and pointer. The fixed 16-byte partition field truncates through `strlcpy`, so invalid or too-long partition names can be rejected server-side or refer to unintended names. `FSYNC_VerifyCheckout` compares program type, pid, command, and reason, but deliberately avoids thread id due portability concerns.

Test signals: tests should cover init/reconnect/finalize, mutex serialization, response logging for each generic result, null versus caller-owned response buffers, VGC add/delete/scan command selection, checkout verification for matching vop, no pending vop, unknown volume, wrong partition, and mismatched pid/program/command/reason.
