<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.h

Purpose: exposes minimal domain-state helpers and global domain list symbols for OCFS2 DLM internals.

Important APIs and types: declares `dlm_domain_lock` and `dlm_domains`, defines inline `dlm_joined()` and `dlm_shutting_down()` predicates, and declares `dlm_fire_domain_eviction_callbacks()`. `dlm_joined()` tests `DLM_CTXT_JOINED`; `dlm_shutting_down()` tests `DLM_CTXT_IN_SHUTDOWN`; both take `dlm_domain_lock`.

Control flow: only the two inline predicates execute code. They acquire the global domain lock, inspect `dlm->dlm_state`, and release the lock.

State and persistence behavior: no state is owned by the header; it exposes the global domain lock/list defined in `dlmdomain.c` and reads volatile `dlm_ctxt` state.

Dependencies and integration points: used by DLM modules that need to test domain membership or shutdown state without duplicating locking rules. The eviction callback declaration lets recovery/domain code notify filesystem consumers of node eviction.

Risks: these helpers intentionally expose coarse state checks; callers needing `DLM_CTXT_IN_SHUTDOWN` to count as fully usable should use `dlm_domain_fully_joined()` instead. The global symbols should only be manipulated according to the lock ordering documented in `dlmdomain.c`.

Test signals: compile coverage and behavior checks around join/shutdown transitions, especially paths that should reject new operations in shutdown but still accept certain network messages while leaving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.h -->
