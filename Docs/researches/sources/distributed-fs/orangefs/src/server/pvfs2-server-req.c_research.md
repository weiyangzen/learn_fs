# sources/distributed-fs/orangefs/src/server/pvfs2-server-req.c

## Purpose
Maps decoded protocol operation numbers to server request parameters and exposes small accessor helpers used by dispatch, scheduling, permission checking, object lookup, credential extraction, and debugging.

## Important APIs, Types, And Functions
`PINT_server_req_table[]` is the central table, indexed directly by `enum PVFS_server_op`. Each entry stores the op type and a `PINT_server_req_params *` from the operation's state-machine module. Exported helpers are `PINT_server_req_readonly`, `PINT_server_req_modify`, `PINT_server_req_get_perm_fun`, `PINT_server_req_get_access_type`, `PINT_server_req_get_sched_policy`, `PINT_server_req_get_object_ref`, `PINT_server_req_get_credential`, and `PINT_map_server_op_to_string`. `CHECK_OP` asserts that the enum value matches the table slot.

## Control Flow
When a request is decoded, server code uses the request's `op` as an array index. Accessor functions assert table alignment, then read function pointers from `params`. If no access-type callback exists, access defaults to readonly. If no object-ref or credential callback exists, output references or credentials are set to zero/NULL and success is returned. `PINT_map_server_op_to_string` returns the static `string_name` stored in the params for logging.

## State And Persistence
The table is process-static runtime metadata, not persistent storage. It binds op numbers to state machines, scheduling policies, permission callbacks, object-reference extractors, credential extractors, and names. Some management operations intentionally have `NULL` params or optional certificate params depending on `ENABLE_SECURITY_CERT`.

## Dependencies And Integration Points
The file depends on `pvfs2-server.h`, `pvfs2-internal.h`, and every generated/manual server state-machine module that exports a `pvfs2_*_params` symbol. `pvfs2-server.c` uses this table via `server_op_state_get_machine`, permission code uses `PINT_server_req_get_perm_fun`, and request scheduling uses the access/schedule metadata.

## Risks And Test Signals
Because the table is indexed by protocol enum value, any mismatch with `pvfs2-req-proto.h` can dispatch a request to the wrong state machine. Helpers dereference `params` without guarding every NULL case, so ops with NULL params must not be passed to helpers that require them. `CHECK_OP` is an `assert`, so release builds may lose protection. Test signals include compile/link checks for every extern params symbol, startup dispatch tests for every implemented op, assertions under debug builds, certificate-enabled and certificate-disabled builds, and negative tests for unsupported/null-param operations such as write completion or disabled certificate management.
