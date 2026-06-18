# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/mr.c

## Purpose
`mr.c` implements exported mlx5 core memory-registration command wrappers for memory keys, protection signature vectors, and the special terminate-scatter-list memory key.

## Important APIs, types, and functions
Exports include `mlx5_core_create_mkey()`, `mlx5_core_destroy_mkey()`, `mlx5_core_query_mkey()`, `mlx5_core_create_psv()`, `mlx5_core_destroy_psv()`, and `mlx5_core_get_terminate_scatter_list_mkey()`. Internal helper `mlx5_get_psv()` extracts PSV indexes from command output slots.

## Control flow
Mkey creation sets the create opcode in the caller-provided input, executes the command, reads the returned mkey index, combines it with the low key byte from the input entry, and returns the complete mkey. Destroy and query convert the full mkey to firmware index and execute the relevant command. PSV creation validates `npsvs <= MLX5_MAX_PSVS`, creates the requested count for a PD, and copies returned PSV indexes. The terminate scatter-list helper returns the legacy constant unless firmware advertises a special mkey and the query succeeds.

## State and persistence behavior
The file stores no state. Successful commands create or destroy firmware objects tied to the HCA. Query fills caller-provided output. The special terminate mkey is read from firmware and returned as big-endian for consumers.

## Dependencies and integration points
It depends on mlx5 command execution, generated command layouts, mkey index conversion helpers, QP constants, and exported symbols for RDMA/Ethernet upper layers. It is used by memory registration, signature offload, and transport paths.

## Risks and edge cases
Caller-provided create input must be correctly sized and initialized beyond the opcode. Mkey low bits are taken from the input entry, so incorrect input produces wrong keys. PSV index extraction supports up to four returned indexes and rejects larger requests. Command failures are returned without partial software cleanup because object ownership remains in firmware/caller contracts.

## Test signals
Test mkey create/query/destroy, invalid PSV count, PSV create/destroy for 1-4 vectors, terminate-scatter-list capability present/absent, firmware command failure injection, and upper-layer memory registration teardown on errors.
