<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-external.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-external.h

Purpose: declares attributes and state for the external worker backend, which lets another subsystem own actual asynchronous execution.

Important callbacks: `PINT_worker_external_post_callout` receives an output op id, an external context pointer, and a `PINT_operation_t`; it should return posted/completed or a negative error. `PINT_worker_external_test_callout` is declared to return completions for external work, but the paired implementation does not currently call it.

Important types: `PINT_worker_external_attr_t` contains `post`, `test`, `external_ptr`, and `max_posts`. `struct PINT_worker_external_s` stores copied attributes, an internal wait queue for overflow, posted count, and mutex. The header exports `PINT_worker_external_impl`.

State behavior: the external subsystem is responsible for real operation progress. This worker only tracks how many posts have been handed out and queues excess operations if configured.

Dependencies are `pint-op.h`, `pint-queue.h`, and the aggregate worker vtable. Integration is through `PINT_WORKER_TYPE_EXTERNAL` in manager worker creation.

Risks: the unused `test` callback and no visible decrement path for `posted` indicate an incomplete or narrowly used implementation. Callers must define ownership rules for `PINT_operation_t` and ensure completion reaches `PINT_manager_complete_op()`. Test signals should include API conformance for external post/test providers, backpressure behavior, and leak checks for overflow queue entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-worker-external.h -->
