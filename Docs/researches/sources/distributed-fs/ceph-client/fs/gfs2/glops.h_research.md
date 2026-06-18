## sources/distributed-fs/ceph-client/fs/gfs2/glops.h

### Purpose
`glops.h` declares the glock operation tables and synchronization helpers implemented in `glops.c`. It lets the generic glock engine and other GFS2 modules refer to type-specific policies without coupling to implementation details.

### Important APIs, Types, and Functions
The header exports `gfs2_freeze_wq`, all `const struct gfs2_glock_operations` instances for meta, inode, rgrp, freeze, iopen, flock, nondisk, quota, and journal glocks, the `gfs2_glops_list` lookup table, `gfs2_inode_metasync`, and `gfs2_ail_flush`.

### Control Flow
There is no executable control flow in the header. The declared operation tables are selected when glocks are created and invoked by `glock.c` around state transitions.

### State and Persistence Behavior
Persistence behavior is delegated to the declared helpers: `gfs2_inode_metasync` writes inode metadata mapping pages, while `gfs2_ail_flush` converts AIL buffers into revokes and flushes the log. The operation tables drive sync/invalidate/instantiate behavior at demotion and acquisition time.

### Dependencies and Integration Points
It includes `incore.h` and is used by glock creation sites in inode, file, rgrp, quota, journal, and mount/recovery code. The declarations must stay aligned with lock types and `gfs2_glops_list` indexing.

### Risks and Edge Cases
The header is small, but mismatched declarations or missing operation table entries would break glock creation or cause type-specific hooks not to run. That can become a durability or cache-coherency bug rather than a compile-only issue if an incorrect table is wired to a lock type.

### Test Signals
Indirect coverage comes from any test that creates and transitions each glock type, especially inode/rgrp demotion, freeze, iopen remote delete, quota locking, and journal recovery.
