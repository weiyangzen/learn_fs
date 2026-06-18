<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-context.h -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-context.h

Purpose: declares the completion-context API used by the manager and workers to deliver operation results. It separates callback-style completions from queue-style completions.

Important types: `enum PINT_context_type` has `PINT_CONTEXT_TYPE_QUEUE` and `PINT_CONTEXT_TYPE_CALLBACK`. `PINT_context_id` is a generated id. `struct PINT_op_entry` stores the user pointer, queued `PINT_operation_t`, original worker/queue id, context id, final error, and quickhash link. `PINT_completion_callback` receives a context id, count, arrays of op ids/user pointers/errors.

APIs: `PINT_open_context()` and `PINT_close_context()` manage context lifetime. `PINT_context_complete()` and `PINT_context_complete_list()` are called by manager/worker code to record completions. `PINT_context_test_all()`, `PINT_context_test_some()`, and `PINT_context_test()` define polling interfaces, although only all/test are implemented in the paired C file in this subset. `PINT_context_is_callback()`, `PINT_context_reference()`, and `PINT_context_dereference()` support manager lifecycle checks.

State behavior is opaque to callers: callers hold ids, not context pointers. Queue contexts accumulate completed operations until tests drain them; callback contexts do not retain completions. Dependencies include `pint-op.h`, `quicklist.h`, `quickhash.h`, and OrangeFS id/error types.

Risks: the header advertises `PINT_context_test_some()` but `pint-context.c` does not provide an implementation in the read file, so link coverage should verify whether another file implements it or whether it is dead API. `struct PINT_op_entry` is exposed enough that lifecycle coupling with id generation and `pint-mgmt.c` is fragile. Tests should validate callback signatures, queue-drain semantics, and header/source symbol parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-context.h -->
