# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-data.h

Purpose: declares the EC fop/callback data lifecycle interface.

Important APIs: `ec_cbk_data_allocate()` creates per-child callback records; `ec_fop_data_allocate()` creates a managed fop with wind/handler/callback union and caller data; `ec_fop_data_acquire()` and `ec_fop_data_release()` manage fop references; `ec_fop_cleanup()` clears accumulated answers; `ec_pending_fops_completed()` is the completion notification hook used when the pending list drains.

Control flow and integration: fop entry points allocate `ec_fop_data_t`, populate operation-specific fields, and start `ec_manager()`. Child callbacks allocate `ec_cbk_data_t`, combine answers, and call `ec_complete()`. Release interacts with `ec-common.c` for parent resume and pending-fop completion.

State behavior: the header exposes lifecycle ownership but not the full struct layout, which is defined through `ec-types.h`. Risks are ownership mismatches: callers must not release borrowed callback fields, and every acquire/sleep path must eventually release/resume. Test signals include compile checking all fop wrappers against the allocation signature and lifecycle tests that prove answer cleanup does not leak dicts, fds, inodes, iobuf refs, or vectors.
