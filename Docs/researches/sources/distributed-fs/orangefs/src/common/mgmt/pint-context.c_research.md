<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-context.c -->
# sources/distributed-fs/orangefs/src/common/mgmt/pint-context.c

Purpose: implements completion contexts for the management subsystem. A context groups completed operations either in a queue for later polling or behind a callback that is invoked immediately on completion.

Important internals: a global quickhash table `pint_contexts` maps `PINT_context_id` to `struct PINT_context`. Queue contexts own a `PINT_queue_id`; callback contexts store `PINT_completion_callback`. `struct PINT_context_queue_entry` wraps completed op id, user pointer, result, and intrusive queue entry. Public operations are `PINT_open_context()`, `PINT_close_context()`, reference/dereference helpers, `PINT_context_complete()`, `PINT_context_complete_list()`, `PINT_context_test_all()`, `PINT_context_test()`, and `PINT_context_is_callback()`.

Control flow: opening initializes the global table on first use, creates either a queue or callback context, registers an id with `id_gen_fast_register()`, and inserts into quickhash. Completing an op either invokes the callback with arrays of one element or allocates a completion entry and pushes it onto the context queue. Test functions remove queued completions via `PINT_queue_timedwait()` or `PINT_queue_wait_for_entry()`, fill caller arrays, and unregister/free `PINT_op_entry` objects when found.

State is process-local and protected partly by `pint_context_mutex`, while queue-level state is protected by `PINT_queue`. There is no persistence. Dependencies include `quickhash`, `quicklist`, `gen-locks`, `id_gen`, `pint-queue`, and debug/gossip infrastructure.

Risks: `pint_context_count` is never incremented in the visible open path but is decremented/used for finalization, making lifecycle logic suspicious. Some error paths unlock a mutex they may not hold. `PINT_context_complete_list()` asserts queue context and can leak previously allocated entries if a later allocation fails. Tests should cover open/close lifecycle, queued and callback completions, empty close rejection, timeout behavior, op-entry cleanup, and concurrent complete/test interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/pint-context.c -->
