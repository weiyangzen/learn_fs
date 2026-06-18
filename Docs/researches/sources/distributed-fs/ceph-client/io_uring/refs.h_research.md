# sources/distributed-fs/ceph-client/io_uring/refs.h

Purpose: provides inline request reference-count helpers for `struct io_kiocb` with overflow checks borrowed from page-ref hardening patterns.

Important APIs/types/functions: `req_ref_zero_or_close_to_overflow()` checks ref values near zero/overflow. Helpers include `req_ref_inc_not_zero()`, `req_ref_put_and_test_atomic()`, `req_ref_put_and_test()`, `req_ref_get()`, `req_ref_put()`, `__io_req_set_refcount()`, and `io_req_set_refcount()`.

Control flow: fast paths avoid atomics when `REQ_F_REFCOUNT` is absent, meaning a request with no extra refs is consumed by `req_ref_put_and_test()`. When refcounted, helpers assert the flag and use atomic inc/dec/test operations.

State and persistence: state is `req->refs` and `REQ_F_REFCOUNT` on an in-flight request. It is transient but controls request lifetime.

Dependencies/integration: used by timeout, waitid, poll, and general completion paths that need to keep requests alive across timers, callbacks, or linked operations.

Risks/test signals: misuse causes UAF or leaked requests; overflow warnings catch ref corruption. Test signals are lockdep/KASAN runs under cancellation, linked timeouts, multishot operations, and task exit.
