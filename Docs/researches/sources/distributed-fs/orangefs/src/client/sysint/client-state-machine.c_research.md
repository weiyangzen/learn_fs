# sources/distributed-fs/orangefs/src/client/sysint/client-state-machine.c
## sources/distributed-fs/orangefs/src/client/sysint/client-state-machine.c

**Purpose:** Core client-side state-machine runtime for sysint and mgmt operations. It opens/closes the job context, posts state machines, progresses jobs, records completions, maps operation IDs, cancels I/O, and releases control blocks.

**APIs and control flow:** `PINT_client_state_machine_initialize/finalize()` wrap job context open/close. `PINT_client_state_machine_post()` starts an SM, records event hints, handles immediate completion, or registers an op ID for deferred completion. `PINT_client_state_machine_test`, `testany`, and `testsome` call `job_testcontext`, continue completed jobs, and drain a bounded completion list. `client_state_machine_terminate()` adds completed non-immediate operations to the completion list after freeing hints and ending events. `PINT_client_io_cancel()` marks an I/O SM cancelled and posts cancellations for in-flight BMI/flow/write-ack jobs. Release helpers unregister IDs, clean credentials, free hints, and free SMCBs.

**State and dependencies:** Global state includes `pint_client_sm_context`, a completion array of 256 SMCBs, completion/test mutexes, op tables, and event integration. Dependencies include `job`, `state-machine`, id generator, ncache/acache, hints, events, and generated SM symbols.

**Risks and tests:** Range validation in `client_op_state_get_machine()` can index gaps between sys and mgmt enums. Several `assert(ret > -1)` checks assume job progress cannot return timeout/error. `PINT_client_state_machine_release()` frees hints twice in current form. Completion list capacity is asserted rather than handled. Test signals should include immediate/deferred operations, completion-list overflow behavior, `testany/testsome` ordering, cancellation with pushed frames, invalid op values, and error returns from job context.
