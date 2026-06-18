<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/ast.c -->
# sources/distributed-fs/ceph-client/fs/dlm/ast.c

Purpose: manages DLM asynchronous callbacks for kernel lock clients: completion ASTs (CAST) and blocking ASTs (BAST). It suppresses redundant callbacks, captures callback state, queues callbacks during recovery/suspension, and dispatches them either directly, through an ordered workqueue, or to the userspace DLM path.

Important APIs/types/functions: exports `dlm_may_skip_callback`, `dlm_get_cb`, `dlm_add_cb`, `dlm_callback_start`, `dlm_callback_stop`, `dlm_callback_suspend`, and `dlm_callback_resume`. Internal helpers are `dlm_run_callback`, `dlm_do_callback`, `dlm_callback_work`, and `dlm_get_queue_cb`. Key state lives in `struct dlm_lkb` fields such as last callback mode/flags/timestamps, `lkb_lksb`, AST/BAST function pointers, and in `struct dlm_ls` callback lock, delay list, flags, and callback workqueue.

Control flow: `dlm_add_cb` first routes userspace locks to `dlm_user_add_ast`. Kernel locks are checked through `dlm_may_skip_callback`, which suppresses compatible or redundant BASTs and records CAST/BAST history; for user locks it can request LVB copy based on mode transition table. With `ls_cb_lock` held, callbacks are either appended to `ls_cb_delay` when callback delay is active, invoked immediately in softirq mode, or wrapped in a `dlm_callback` and queued to `ls_callback_wq`. Workqueue execution calls the captured AST/BAST function and frees the callback object. Suspend sets the delay flag and flushes in-flight work. Resume drains delayed callbacks in batches of 25, dispatching them according to softirq/workqueue mode, clears the delay flag once empty, and yields between batches.

State and persistence: callback objects are transient allocations from DLM memory helpers. Delayed callback lists persist across recovery suspension until resume. Last callback mode/time fields persist on each lock block and affect future suppression. CAST dispatch writes status and flags into the caller's `dlm_lksb` before invoking `astfn`.

Dependencies and integration: depends on DLM lock/resource/lockspace structures, LVB operation tables, userspace AST support, DLM memory allocation, tracepoints (`trace_dlm_ast`, `trace_dlm_bast`), workqueues, spinlocks with bottom-half disabling, and DLM mode compatibility logic from lock code.

Risks: skipping logic must not suppress a callback required by a client to make progress. Callback ordering matters, hence ordered workqueue and suspension delay. AST functions are external callbacks, so calling context (`LSFL_SOFTIRQ` versus workqueue) is a contract. Incorrect active delay handling can lose callbacks during recovery or invoke them while lockspace state is inconsistent.

Test signals: lock conversion and blocking scenarios should verify CAST/BAST delivery order, duplicate BAST suppression, LVB copy decisions, userspace AST routing, recovery suspend/resume queue draining, workqueue allocation failure handling, tracepoint emission, and softirq-mode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/dlm/ast.c -->
