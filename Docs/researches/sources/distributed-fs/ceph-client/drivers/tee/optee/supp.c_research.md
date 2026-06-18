# sources/distributed-fs/ceph-client/drivers/tee/optee/supp.c

## Purpose
`supp.c` implements the kernel side of the OP-TEE supplicant RPC queue. Secure-world calls can request userspace services; kernel requesters enqueue work, tee-supplicant receives it through privileged TEE ioctls, and sends results back.

## Important APIs, Types, And Functions
`struct optee_supp_req` stores one request, including queue/id state, function id, return code, params, and completion. `optee_supp_init()` initializes mutex, completion, IDR, request list, and synchronous request id. `optee_supp_release()` aborts all requests in the IDR and queue, completes their waiters with communication errors, clears `supp->ctx`, and resets synchronous state.

`optee_supp_thrd_req()` enqueues a request, wakes supplicant waiters, and blocks killably until completion; if interrupted while still queued it removes the request and returns communication error. `optee_supp_recv()` validates the user-provided receive parameter slots, waits for a queued request, assigns an IDR id, supports asynchronous mode when a meta parameter is provided, copies request params to userspace, and returns the requested function id. `optee_supp_send()` finds the outstanding request by async meta id or synchronous `req_id`, copies output values and memref sizes back to the original params, stores the supplicant return code, and completes the blocked requester.

## Control Flow And State
The supplicant state is protected by `supp->mutex`. Requests start in `supp->reqs`, move into `supp->idr` after userspace receives them, and complete when userspace sends a response. `supp->req_id` enforces legacy synchronous mode; async mode uses a meta value parameter carrying the IDR id and requires `supp->req_id == -1`.

## Dependencies And Integration Points
The file integrates with privileged OP-TEE supplicant TEE device ops, TEE parameter/memref helpers, Linux completions, IDR, and common RPC dispatch in `rpc.c`. `core.c` manages supplicant context singleton and calls release cleanup.

## Risks
`supp_check_recv_params()` drops references for memrefs present in receive buffers before validating attrs, relying on ioctl-layer reference behavior. Supplicant must not mix synchronous and asynchronous request modes; violations return errors that force restart-like behavior. If no supplicant is present and caller is blocking, requests can wait until interrupted. Output copying only updates value outputs/inouts and memref sizes, not memref object pointers or contents, which is intentional but must match caller expectations.

## Test Signals
Supplicant recv/send in synchronous and asynchronous meta modes, mixed-mode rejection, too few receive params, malformed attrs, interrupted requester waits, supplicant release with queued and in-flight requests, and output propagation for value and memref params.
