<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-mgmt.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-mgmt.h

Purpose: public management API for operation managers. It exposes the abstraction that callers use to initialize a manager, add worker implementations and queues, post operations, test or wait for completion, cancel operations, map work to workers, and observe events.

Important constants and enums: return codes include `PINT_MGMT_OP_COMPLETED` and `PINT_MGMT_OP_POSTED`; `PINT_MGMT_TIMEOUT_NONE` represents indefinite waits. `PINT_event_type` has start and end operation events. `PINT_manager_t` is opaque.

Important APIs: `PINT_manager_init()`/`destroy()` manage lifecycle. `PINT_manager_worker_add()` and `PINT_manager_worker_remove()` manage worker instances. `PINT_manager_queue_add()`/`remove()` associate queues with queue-capable workers. `PINT_manager_post()` is a macro over `PINT_manager_id_post()` using implicit worker selection. `PINT_manager_ctx_post()` allows explicit completion context. `PINT_manager_cancel()`, `PINT_manager_add_map()`, `PINT_manager_test_context()`, `PINT_manager_test()`, `PINT_manager_test_op()`, `PINT_manager_wait_context()`, `PINT_manager_wait()`, `PINT_manager_wait_op()`, `PINT_manager_service_op()`, and `PINT_manager_complete_op()` form the runtime control surface.

State behavior is mostly opaque but the API contract implies generated operation ids remain valid until completion/test cleanup. Dependencies include worker, op, queue, and context headers.

Risks: callers must choose test versus wait based on context type; queue contexts and callback contexts are not interchangeable. The `PINT_manager_post` macro hides implicit worker selection, which falls back to blocking if no mapping applies. Test signals should cover all public entry points, timeout constants, callback and queue completion modes, and mapping functions returning worker ids, queue ids, implicit ids, and errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-mgmt.h -->
