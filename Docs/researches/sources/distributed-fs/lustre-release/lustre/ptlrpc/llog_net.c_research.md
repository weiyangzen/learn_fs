# sources/distributed-fs/lustre-release/lustre/ptlrpc/llog_net.c

## Purpose
`llog_net.c` is a small connector for remote OST/MDS recovery logging. It binds an llog context to the client import used for remote llog RPCs, preserving the invariant that a context should not switch between unrelated imports.

## Important APIs, types, and functions
The only exported API is `llog_initiator_connect(struct llog_ctxt *ctxt)`. It reads `ctxt->loc_obd->u.cli.cl_import`, stores a referenced import in `ctxt->loc_imp`, and uses `ctxt->loc_mutex` for synchronization. It uses `class_import_get()` and `class_import_put()` to manage import references.

## Control flow
The function asserts that `ctxt` exists and that an existing `loc_imp`, if present, is already the same import as the current client import. Under the context mutex, it compares `loc_imp` with `new_imp`; if they differ, it drops the old reference, takes a reference to the new import, and assigns it. It returns success after updating or confirming the binding.

## State and persistence behavior
No persistent data is written. The durable effect is the in-memory `llog_ctxt::loc_imp` reference used by `llog_client.c` when issuing remote llog operations. The function deliberately preserves one import per context and asserts on unexpected import changes.

## Dependencies and integration points
It depends on Lustre OBD client state (`loc_obd->u.cli.cl_import`), llog context locking, and import reference helpers. `llog_client_entry()` later consumes the import set here, while recovery and target connection setup code call this function when establishing logging connectivity.

## Risks and edge cases
The strict assertion on changed imports can expose unexpected reconnect or failover behavior if callers try to reuse a context with a different import. The function assumes `loc_obd` and its client import are valid. Since it only updates in-memory state, missed calls leave `llog_client_entry()` returning `-EINVAL` and warning that recovery will retry.

## Test signals
Validation should cover first-time connection, repeated connection with the same import, reference count balance when replacing a null import, warning/retry behavior in `llog_client.c` when no import was set, and failover scenarios that prove contexts are rebuilt or updated without violating the same-import assertion.
