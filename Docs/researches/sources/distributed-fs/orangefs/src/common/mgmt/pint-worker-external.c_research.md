<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-external.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-external.c

Purpose: implements a worker backend that delegates posting and completion progress to an external subsystem through callouts supplied in `PINT_worker_external_attr_t`.

Important functions: `external_init()` copies attributes, initializes a mutex, sets `posted` to zero, and creates an internal wait queue. `external_destroy()` destroys that wait queue. `external_post()` locks the worker, enqueues operations if `max_posts` is positive and the current posted count has reached that limit, otherwise calls the external `post()` callback with the operation id pointer, external context pointer, and operation object, then increments `posted`.

Control flow is intentionally thin: this implementation does not service operations itself and has no `do_work` callback in the vtable. The header defines a `test` callout, but this C file does not use it, so completion progression must be handled elsewhere or is incomplete.

State is process-local: copied attributes, wait queue id, posted count, and mutex. There is no persistence. Dependencies include `pint-queue`, manager/worker contracts, and OrangeFS errors.

Risks: queued overflow operations in `wait_queue` are never drained in this file, and `posted` is incremented but never decremented here. `external_destroy()` calls `PINT_queue_destroy()` without removing producer/consumer refs because none were added, but destruction will still fail if overflow operations remain queued. Tests should cover `max_posts=0`, bounded posting, queueing at limit, external callback errors, destroy with/without queued entries, and whether any higher layer consumes the declared `test` callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-external.c -->
