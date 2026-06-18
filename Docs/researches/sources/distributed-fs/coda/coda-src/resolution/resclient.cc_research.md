<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resclient.cc -->
# sources/distributed-fs/coda/coda-src/resolution/resclient.cc

Purpose: implements server-side RPC handlers and helpers used by the client/participant side of resolution phases, especially installing final version vectors and preparing phase-2 inconsistency objects.

Important APIs/control flow: `RS_InstallVV` translates the volume, locks the object, updates version vectors when COP2 is pending, possibly schedules log truncation, and ships directory contents/ACL back to the coordinator. `MarkObjInc` breaks callbacks and sets the inconsistency flag. `CreateObjToMarkInc` ensures an object named in an inconsistency list exists, creating or linking files/directories/symlinks as needed and spooling resolve log records. `GetPhase2Objects` builds and locks a `vlist` for a parent and all relevant child/parent fids from an inconsistency list. `CreateResPhase2Objects` iterates the list and creates missing objects. `GetNameInParent` finds a vnode's name in its parent directory.

State/persistence: mutates volume/vnode version vectors, directory entries, inode numbers, disk usage, callbacks, COP2 flags, and resolution logs under Coda locking/transaction conventions.

Dependencies/integration: integrates with RPC2 side effects, VRDB host indexes, vnode allocation, file operation semantics, `resutil` inconsistency lists, `ops.cc`, and timing probes.

Risks/test signals: complex object creation paths have many partial side effects before returning errors. Yield points exist for large lists. Test missing parent, name collision with different fid, existing deleted file relink, creating each vnode type, incomplete VSG, and successful `RS_InstallVV` truncation decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/resclient.cc -->
