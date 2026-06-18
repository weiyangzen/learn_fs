# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs_send.c

## Purpose
`qat_algs_send.c` provides common firmware-message submission and backlog handling for QAT crypto/compression algorithms. It wraps `adf_send_message()` with retry or Crypto API backlog behavior.

## Important APIs, Types, And Functions
Public functions are `qat_alg_send_message()` and `qat_alg_send_backlog()`. Internal helpers are `qat_alg_send_message_retry()`, `qat_alg_try_enqueue()`, and `qat_alg_send_message_maybacklog()`. It consumes `struct qat_alg_req` and `struct qat_instance_backlog` from `qat_algs_send.h`.

## Control Flow
For requests without `CRYPTO_TFM_REQ_MAY_BACKLOG`, `qat_alg_send_message_retry()` retries a full ring up to `ADF_MAX_RETRIES` and returns `-ENOSPC` on persistent `-EAGAIN`, otherwise `-EINPROGRESS`. With backlog allowed, `qat_alg_send_message_maybacklog()` first tries immediate enqueue if no backlog exists and the ring is not nearly full. If that fails, it locks the backlog, retries under the lock, and queues the request list node with `-EBUSY` if still unable. Completion callbacks call `qat_alg_send_backlog()`, which drains queued requests until the ring refuses one and completes each dequeued base request with `-EINPROGRESS`.

## State And Persistence Behavior
Backlog state is an in-memory list protected by a spinlock. Individual `qat_alg_req` nodes are embedded in per-request contexts and persist until sent or completed. No persistent storage exists.

## Dependencies And Integration Points
It depends on `adf_transport` ring APIs and the Crypto API async request completion mechanism. Symmetric, asymmetric, and compression code all embed `qat_alg_req` and share instance backlogs.

## Risks
Backlogged requests depend on request-context lifetime; callers must not free contexts after receiving `-EBUSY`. The immediate path returns `-EINPROGRESS` even if `adf_send_message()` succeeds after retries, matching Crypto API async semantics. A nearly-full threshold can send requests to backlog before hard full, trading latency for flow control. Completion-driven draining means a dead ring can leave backlog stalled.

## Test Signals
Ring-full tests should observe `-ENOSPC` without backlog and `-EBUSY` with backlog. Completion should later produce `-EINPROGRESS` for dequeued requests. Concurrency tests should cover multiple producers sharing one backlog.
