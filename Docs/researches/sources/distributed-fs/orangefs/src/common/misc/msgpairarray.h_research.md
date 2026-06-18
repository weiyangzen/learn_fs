# sources/distributed-fs/orangefs/src/common/misc/msgpairarray.h

Purpose: Declares the state-machine interface and state records used to send and receive one or more PVFS server request/response message pairs. It groups per-message request encoding, BMI addressing, job ids/status, retry state, and completion callbacks for generated `msgpairarray.c`.

Important APIs and types: `pvfs2_msgpairarray_sm` is the exported state machine. `PINT_sm_msgpair_state` holds filesystem id, target handle, retry flags/count, completion callback, server BMI address, session tag, server request, encoded request, encoding type, response buffer, send/recv job ids/status, operation status, and completion marker. `PINT_sm_msgpair_params` carries timeout, retry delay/limit, job context, quiet flag, and remaining completion count. `PINT_sm_msgarray_op` embeds either a single `msgpair` or an allocated `msgarray`. Macros initialize single-message operations and iterate arrays.

Control flow and integration: Callers fill `fs_id`, `handle`, `retry_flag`, and `comp_fn`, initialize a single or array operation, resolve addresses with `PINT_serv_msgpairarray_resolve_addrs()`, and enter the generated state machine. Completion callbacks inspect decoded server responses. Helper functions initialize/destroy arrays, compute aggregate status, decode responses, and release encoded/decoded resources.

State and persistence behavior: State is transient per state-machine operation. Persistent state is not modified by the header, but server requests carried in `req` can mutate filesystem state when processed remotely. The `retry_count`, `complete`, and job status fields govern idempotence and retry behavior.

Dependencies and risks: Depends on PVFS request protocol, encoding, BMI/job interfaces, and state machine generation. The `PINT_msgpair_init` and `PINT_init_msgpair` macros free existing dynamic arrays when switching back to a single embedded message; callers must not retain stale pointers. Tests should cover single vs multi-message initialization, address resolution, retry/no-retry paths, failed send/recv status, decode failures, and resource cleanup after partial completions.
