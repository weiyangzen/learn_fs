# sources/distributed-fs/lustre-release/lustre/ptlrpc/nrs.c

## Purpose

`nrs.c` is the Network Request Scheduler core for PTLRPC services. It registers policy descriptors, instantiates compatible policies on each service partition's regular and high-priority NRS heads, obtains per-request policy resources, enqueues and dispatches requests, supports runtime policy control, and cleans all policy state during service and module teardown.

## Important APIs, Types, and Functions

Central state is `struct nrs_core nrs_core`, `struct ptlrpc_nrs`, `struct ptlrpc_nrs_policy`, `struct ptlrpc_nrs_pol_desc`, `struct ptlrpc_nrs_pol_conf`, `struct ptlrpc_nrs_resource`, and `struct ptlrpc_nrs_request`. Important internal functions include `nrs_policy_start_locked`, `nrs_policy_stop_locked`, `nrs_policy_register`, `nrs_policy_unregister`, `nrs_resource_get_safe`, `nrs_resource_put_safe`, `nrs_request_enqueue`, `nrs_request_get`, and `nrs_request_removed`.

Exported or externally used APIs include `ptlrpc_service_nrs_setup`, `ptlrpc_service_nrs_cleanup`, `ptlrpc_nrs_req_initialize`, `ptlrpc_nrs_req_finalize`, `ptlrpc_nrs_req_add`, `__ptlrpc_nrs_req_get_nolock`, `ptlrpc_nrs_req_del_nolock`, `ptlrpc_nrs_req_pending_nolock`, `ptlrpc_nrs_req_throttling_nolock`, `ptlrpc_nrs_req_hp_move`, `ptlrpc_nrs_policy_control`, `ptlrpc_nrs_init`, and `ptlrpc_nrs_fini`.

## Control Flow

Module initialization creates the core policy list and registers built-in policies. FIFO and delay are registered unconditionally; CRR-N, ORR, TRR, and TBF are registered under server builds. Service setup walks service partitions under `nrs_core.nrs_mutex`, initializes a regular NRS head and optionally an HP head, and registers all compatible descriptors. Policies marked `PTLRPC_NRS_FL_REG_START` start immediately, which makes FIFO the default fallback.

Policy start is serialized per NRS head. Starting a fallback policy is allowed only during setup or as the already active fallback. Starting a primary requires a fallback, optionally restarts if arguments change, grabs a module reference, calls the policy start op outside the spinlock, sets the started reference, and replaces any previous primary. Stopping hides the policy from the NRS head, drops the started reference, waits up to 30 seconds for queued and started requests to drain, and calls the policy stop op when references reach zero.

Request initialization obtains resources for fallback and, if present, primary policies. Resource acquisition walks each policy's resource hierarchy by repeatedly calling `op_res_get`; if a primary rejects a request, only fallback resources remain. Enqueue tries primary resources first, then fallback, increments queued counters, and takes an extra started reference while the request is pending. Dispatch walks policies with queued requests, calls each policy's `op_req_get`, marks returned requests started, updates queued and started counters, and round-robins among policies with queued work. Dequeue and finish paths call policy dequeue/stop hooks and release resource and started references.

High-priority movement obtains HP resources in atomic context, locks the service partition request lock, verifies the request can move, removes it from the regular policy, swaps resource arrays, enqueues it on the HP head, then releases whichever resource set is no longer owned by the request.

## State and Persistence Behavior

NRS state is in-memory only. There is no disk persistence in this file; runtime controls are exposed through policy lprocfs/debugfs implementations and apply to live policy instances. Policy descriptors persist for the lifetime of the PTLRPC module. Policy instances persist for each service partition NRS head until service cleanup or external policy unregistration.

Per-policy state is protected by the NRS head spinlock for lifecycle and counters, plus policy-specific locks or atomic/refcount fields. `pol_start_ref` protects active, queued, and started request ownership. `pol_ref` protects callers that found a policy by name. Module references are held while a policy descriptor has active started instances.

## Dependencies and Integration Points

The core depends on PTLRPC service and service partition structures, `ptlrpc_all_services`, service CPT allocation helpers, built-in policy configuration symbols (`nrs_conf_fifo`, `nrs_conf_delay`, and server-only policies), lprocfs/debugfs policy hooks, Linux modules/refcounting, wait queues, and service request locks. It integrates with PTLRPC request receive/finish paths, high-priority request handling, ldlm lock reorder movement, service registration/unregistration, and lctl-facing policy control paths.

## Risks and Edge Cases

Fallback policy availability is a hard invariant; enqueue ends in `LBUG()` if no policy accepts a request. Runtime start/stop is constrained by transient `STARTING` and `STOPPING` states and can return `-EAGAIN` or `-EBUSY`. The 30-second stop wait means policy stop can fail while requests are still draining. External policies cannot be fallback or auto-start because cleanup cannot safely drain them during partial registration failure. Policy operations run partly outside locks, so policy implementations must obey the core's resource and request ownership contracts exactly.

HP movement is sensitive because it obtains resources before taking the request lock and may allocate with `GFP_ATOMIC`. Request initialized/finalized bits are intentionally accessed without locking at early/late lifecycle points. Debug/control callers can receive `-ENODEV` for stopped policies and `-ENOENT` for missing policy names.

## Test Signals

Core tests should cover service setup with and without HP queues, built-in policy registration order, fallback auto-start, starting and replacing primary policies, resetting to fallback, policy argument restart semantics, stop while queued/started requests drain, and service cleanup. Request tests should cover primary accept/reject fallback behavior, enqueue/dequeue counter updates, queued-policy round robin, peek versus get, finalize releasing both primary and fallback resources, HP move success and no-op cases, and throttling/pending queries. Control tests should exercise regular, HP, and both-queue policy commands, stopped policy `-ENODEV`, missing policy `-ENOENT`, and external policy registration rollback.
