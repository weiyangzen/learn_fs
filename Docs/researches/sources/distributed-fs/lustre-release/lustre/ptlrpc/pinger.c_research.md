# sources/distributed-fs/lustre-release/lustre/ptlrpc/pinger.c

Purpose: manages periodic import pinging, reconnect triggering, ping suppression for pingless imports, idle disconnects, and the server-side ping evictor thread that evicts exports whose clients stop sending traffic.

Important APIs/types/functions: exported helpers include `ptlrpc_pinger_suppress_pings()`, `ptlrpc_obd_ping()`, `ptlrpc_pinger_ir_up()`, `ptlrpc_pinger_ir_down()`, `ptlrpc_pinger_add_import()`, `ptlrpc_pinger_del_import()`, `ping_evictor_wake()`, `ping_evictor_start()`, and `ping_evictor_stop()`. Internal flow uses `ptlrpc_prep_ping()`, `ptlrpc_ping()`, `ptlrpc_update_next_ping()`, `ptlrpc_pinger_process_import()`, delayed work `ping_work`, global `pinger_imports`, and ping evictor globals `pet_*`.

Control flow: pinger start creates a CPT-bound workqueue and schedules immediate processing. Each run scans registered imports under `pinger_mutex`, skips imports not due, starts recovery for disconnected active imports, avoids pings when recovery is disabled or the import is inactive, and sends async OBD_PING requests through `ptlrpcd_add_req()` when appropriate. It computes the nearest next wakeup from `imp_next_ping`. The evictor thread waits for OBDs queued by `ping_evictor_wake()`, scans sorted timed exports, logs and optionally dumps debug data, then calls `class_fail_export()` for expired clients.

State/persistence: maintains in-memory import list membership and refcounts, global IR state, optional module parameter `suppress_pings`, a delayed workqueue, and an evictor kthread/list. No durable state is written; import deadlines and next-ping times are runtime state.

Dependencies/integration: depends on PTLRPC request packing, async daemon queues, import state transitions, adaptive timeout data, OBD import/export events, LDLM namespace reference counts for idle detection, LNet NID logging, failure injection, and Lustre environment setup for the evictor.

Risks/test signals: races around import removal, pinger wakeup after stop, pingless suppression, and forced verification can affect recovery latency. Evictor correctness depends on export deadline ordering and reference handling while dropping OBD locks. Tests should cover pinger start/stop idempotence, adding/removing imports, disconnected import reconnect, idle disconnect, pingless IR suppression, force-next-verify behavior, async ping queuing, evictor wake/refcount lifecycle, and timed export eviction.
