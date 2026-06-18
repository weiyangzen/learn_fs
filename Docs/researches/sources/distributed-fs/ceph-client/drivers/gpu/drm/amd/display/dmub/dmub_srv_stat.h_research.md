# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/dmub_srv_stat.h

Purpose: this header declares the lock-light DMUB status/notification interface. It exists because some notification polling paths are called without DAL and DC locks and therefore must touch only state dedicated to that purpose.

Important API: `dmub_srv_stat_get_notification(struct dmub_srv *dmub, struct dmub_notification *notify)` retrieves and normalizes a DMUB outbox notification. The implementation lives in `dmub/src/dmub_srv_stat.c`. `struct dmub_notification` and status codes come from `dmub_srv.h`.

Control flow and state: callers pass an existing `dmub_srv` and an output notification buffer. The comment in `dmub_srv.h` notes that `outbox1_rb` is accessed without locks and is intended only for this stat function. That makes this API a constrained side path into DMUB service state rather than a general service operation.

Dependencies and integration: it includes `dmub_srv.h`. `dc/core/dc_stat.c` calls this API, and ASIC-specific DMUB files provide outbox read/write helpers that are documented as callable only by this notification path.

Risks and tests: because the API is used without broad locks, it must avoid modifying unrelated DMUB state and must tolerate concurrent display-core activity. Races around outbox ring pointers, pending notifications, and hardware-ready interrupt status are the main risk. Tests should cover no-data, AUX reply, HPD, HPD IRQ, set-config reply, DPIA notifications, fused I/O, pending-notification chaining, and concurrent polling with normal DMUB command submission.
