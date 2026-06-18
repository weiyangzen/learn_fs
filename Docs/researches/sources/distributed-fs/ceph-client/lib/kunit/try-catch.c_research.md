# sources/distributed-fs/ceph-client/lib/kunit/try-catch.c

Purpose: executes a potentially aborting KUnit callback in a separate kthread and invokes a catch callback on throw, fault, timeout, or thread creation failure.

Important APIs/types/functions: `kunit_try_catch_throw()`, `kunit_generic_run_threadfn_adapter()`, and `kunit_try_catch_run()`.

Control flow: run stores context, creates a kthread, keeps a task reference, waits on the thread completion up to the configured timeout, and stops timed-out tasks. The adapter initializes `try_result` to `-EINTR`, invokes the try function, and changes untouched `-EINTR` to success. Throw sets `-EFAULT` and exits the kthread. After completion, nonzero results are logged and catch is called; `-EFAULT` is translated back to zero before catch so KUnit aborts are not treated as infrastructure errors.

State/persistence: mutates `try_catch->context` and `try_result`; temporarily owns a kthread/task reference.

Dependencies/integration: used by `test.c` to isolate test bodies and cleanup. Depends on kthread, completions via `vfork_done`, task refcounting, and KUnit logging.

Risks: timeout handling calls `kthread_stop()` after wait timeout; callback code must be stoppable enough for cleanup. Fault reporting uses `test->last_seen` when available.

Test signals: `kunit-test.c` validates normal try, thrown try, and optional null dereference fault catching.
