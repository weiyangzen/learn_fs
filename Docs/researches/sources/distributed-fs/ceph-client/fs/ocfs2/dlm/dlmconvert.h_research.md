<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.h

Purpose: declares the two conversion entry points used outside `dlmconvert.c`: one for resources mastered locally and one for resources mastered by another node.

Important APIs and types: `dlmconvert_master(struct dlm_ctxt *dlm, struct dlm_lock_resource *res, struct dlm_lock *lock, int flags, int type)` performs conversion against a locally mastered lock resource. `dlmconvert_remote(...)` performs the secondary-node path and sends a network conversion request to the current owner. The declarations rely on DLM core types and `enum dlm_status` from the included DLM common/API headers in callers.

Control flow: this header has no executable control flow. It defines the compile-time contract consumed mainly by `dlmlock.c`, allowing `dlmlock()` to dispatch `LKM_CONVERT` based on `res->owner == dlm->node_num`.

State and persistence behavior: no state is stored in the header. The functions it exposes mutate runtime lock and lock-resource queue state only in memory.

Dependencies and integration points: included by `dlmlock.c` and implemented by `dlmconvert.c`. It is part of the internal OCFS2 DLM interface, not a public exported symbol interface.

Risks: prototypes must stay consistent with the implementation and with `dlmlock()` dispatch assumptions. Since conversion status is returned as `enum dlm_status`, callers must preserve DLM-specific retry semantics such as `DLM_RECOVERING`, `DLM_MIGRATING`, `DLM_FORWARD`, and `DLM_NOTQUEUED`.

Test signals: build coverage with OCFS2 DLM enabled is the primary signal. Conversion tests in `dlmlock()` should cover both declared paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.h -->
