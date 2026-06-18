# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/post_act.h

Purpose: Declares the post-action steering subsystem interface and opaque handle types.

Important APIs: Init/destroy, add/del, offload/unoffload, table getter, and handle-to-register modify-header setup.

Control flow and state: Callers create a post-action context for a namespace/chains pair, allocate handles for deferred attrs, offload matching rules, and add register-setting actions to previous rules.

Dependencies and integration: Includes mlx5e core types and fs chains; used by TC action parsing/offload code that needs multi-table continuation.

Risks and tests: Handle lifecycle must be paired carefully with rule offload. Tests should include add failure, offload failure cleanup, and using `get_ft()` for sample/default table paths.
