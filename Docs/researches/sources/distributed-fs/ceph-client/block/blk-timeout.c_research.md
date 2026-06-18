# sources/distributed-fs/ceph-client/block/blk-timeout.c

Purpose: provides generic request timeout support for the block layer plus optional timeout fault injection. It sets request deadlines, rounds queue timer expirations, bounds maximum timeout distance, and exposes abort/fail knobs.

Important APIs and functions: under `CONFIG_FAIL_IO_TIMEOUT`, `__blk_should_fake_timeout()`, boot parameter parsing for `fail_io_timeout=`, debugfs setup, `part_timeout_show()`, and `part_timeout_store()` control `QUEUE_FLAG_FAIL_IO`. Core functions are `blk_abort_request()`, `blk_rq_timeout()`, and `blk_add_timer()`. `blk_timeout_init()` initializes a mask used by timeout rounding.

Control flow: when a request starts, `blk_add_timer()` fills `req->timeout` from the queue default if needed, clears `RQF_TIMED_OUT`, writes `req->deadline`, rounds the queue timer expiry, and updates `q->timeout` only when no timer is pending or the new deadline is meaningfully earlier. `blk_abort_request()` forces a request deadline to current jiffies and schedules queue timeout work. Fault-injection users can cause completion paths such as BSG to skip normal completion and exercise timeout recovery.

State and persistence: state is in request fields, queue timer state, queue flags, and the global `blk_timeout_mask`. Debugfs and sysfs knobs affect runtime behavior only.

Dependencies and integration points: integrates with `blk-mq` timeout work, request queue timers, `blk_should_fake_timeout()`, block partition/device sysfs attributes declared in `blk.h`, and kernel fault-injection infrastructure.

Risks and test signals: deadline writes are intentionally lightweight, so correctness depends on timeout scanning observing `req->deadline`. Timer slack avoids excessive `mod_timer()` churn but can delay recovery if calculated incorrectly. Test request timeout recovery, `blk_abort_request()` from drivers, fault injection through debugfs and `fail_io_timeout=`, sysfs fail toggles, and very large timeouts clamped by `BLK_MAX_TIMEOUT`.
