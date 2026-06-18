<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.h

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.h_research.md`.

Purpose: declares endpoint posting, replay, key, and fake-error APIs plus a small work item used for asynchronous error injection.

Important APIs/types/functions: `struct kfilnd_ep_err_fail_loc_work`, inline `kfilnd_ep_replays_pending()`, operation posters/cancelers, immediate-buffer APIs, lifecycle `kfilnd_ep_alloc/free()`, replay queue APIs, key APIs, and `kfilnd_ep_gen_fake_err()`.

Control flow: transaction code posts sends/RMA/tagged receives through this API; CQ code checks/flushes replay queues; device code allocates/frees endpoints and posts immediate buffers.

State and persistence behavior: the inline replay predicate observes endpoint `replay_count`; all other state is owned by `struct kfilnd_ep`.

Dependencies and integration: includes `kfilnd.h` and exposes kfabric error-entry types to endpoint users.

Risks: declarations include `kfilnd_ep_reg_mr()`/`dereg_mr()` but the current source set does not define/use them, so stale prototypes should be watched. Callers must respect endpoint initialization state and transaction ownership.

Test signals: compile all users, run replay/fake-error paths, and use symbol checks to detect stale undeclared or undefined APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/kfilnd_ep.h -->
