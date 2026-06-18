# sources/distributed-fs/coda/coda-src/vol/fssync.h

Purpose: public command and API definitions for file-server/volume-utility synchronization.

Important definitions: commands are `FSYNC_ON`, `FSYNC_OFF`, `FSYNC_NEEDVOLUME`, and `FSYNC_MOVEVOLUME`. Reasons include salvage, move, and operator action. Replies are byte-sized `FSYNC_DENIED` or `FSYNC_OK`. Exported APIs initialize the file-server side, register utility clients, finalize clients, issue synchronization requests, and check temporary relocation information.

Control flow/state: the header constrains the protocol surface used by volume utilities and the volume package. `FSYNC_NEEDVOLUME` is intentionally mode-sensitive: callers pass volume attachment mode in the `reason` position. `FSYNC_CheckRelocationSite` is marked with `WARN_SINGLE_HOMING`, signaling that single-server assumptions may be relevant.

Dependencies/integration: depends on Coda transaction annotations and deprecation helpers; uses `VolumeId` from included volume/common headers. Risks are protocol ambiguity from integer commands/reasons and compatibility dependence on exact numeric constants. Test signals are compile-time coverage in utilities and runtime tests for every command/reason pair.
