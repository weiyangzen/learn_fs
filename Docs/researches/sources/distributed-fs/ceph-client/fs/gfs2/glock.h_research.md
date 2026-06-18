## sources/distributed-fs/ceph-client/fs/gfs2/glock.h

### Purpose
`glock.h` declares GFS2's lock-manager-facing constants, glock public API, holder lifecycle helpers, assertion/debug macros, and DLM lockops interface. It is the contract used by file, inode, glops, quota, rgrp, super, and recovery code to acquire cluster locks.

### Important APIs, Types, and Functions
The header defines lock name types (`LM_TYPE_INODE`, `LM_TYPE_RGRP`, `LM_TYPE_IOPEN`, etc.), lock states (`LM_ST_UNLOCKED`, `LM_ST_EXCLUSIVE`, `LM_ST_DEFERRED`, `LM_ST_SHARED`), request flags (`LM_FLAG_TRY`, `LM_FLAG_RECOVER`, `LM_FLAG_ANY`, `GL_ASYNC`, `GL_EXACT`, `GL_SKIP`, `GL_NOCACHE`, `GL_NOBLOCK`), DLM output flags, adaptive hold-time constants, `struct lm_lockops`, and `struct gfs2_glock_aspace`. Inline helpers include `gfs2_glock_is_locked_by_me`, `gfs2_glock2aspace`, `gfs2_glock_nq_init`, holder initialization checks, and `glock_needs_demote`.

### Control Flow
The most important inline flow is `gfs2_glock_nq_init`: initialize a holder with the calling instruction pointer, enqueue it with `gfs2_glock_nq`, and uninitialize on failure. Callers use this to enforce acquire/release symmetry. `gfs2_glock_is_locked_by_me` scans current holders under the glock spinlock and is used to avoid self-deadlock in permission, lookup, and getattr paths.

### State and Persistence Behavior
The header does not persist state itself but defines the symbolic state machine consumed by `glock.c` and operation hooks. Flags such as `GL_NOCACHE`, `GL_SKIP`, `LM_FLAG_RECOVER`, and `LM_FLAG_NODE_SCOPE` affect whether state is cached, whether instantiate hooks read disk, whether recovery can bypass blocked locks, and whether exclusive DLM ownership can be shared locally.

### Dependencies and Integration Points
It includes `incore.h` for core structures and exposes `gfs2_dlm_ops` for clustered lock integration. It is included by all major GFS2 subsystems that need glock acquisition, debug dumps, delete verification, or debugfs integration.

### Risks and Edge Cases
Because this header defines flag values and lock-state compatibility semantics, any change can affect the whole filesystem. Inline holder checks must remain consistent with `glock.c` holder list invariants. Misusing `GL_SKIP`, `GL_NOCACHE`, or `GL_NOBLOCK` can bypass instantiate, force unnecessary demotes, or produce surprising nonblocking errors.

### Test Signals
Coverage is indirect: all glock acquisition tests, recovery tests, DLM integration tests, inode lookup/delete tests, and local-vs-clustered locking configurations exercise this contract.
