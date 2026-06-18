# sources/distributed-fs/ceph-client/drivers/firmware/broadcom/tee_bnxt_fw.c

## Purpose
This file is a TEE client driver for Broadcom BNXT firmware management. It opens an OP-TEE trusted application session, invokes a secure fastboot command for firmware loading, and provides a coredump-copy helper that transfers secure coredump data through shared memory.

## Important APIs, Types, And Functions
`struct tee_bnxt_fw_private` stores the global device, TEE context, session ID, and 4 MiB shared-memory pool. Public exported functions are `tee_bnxt_fw_load()` and `tee_bnxt_copy_coredump()`. `prepare_args()` initializes `tee_ioctl_invoke_arg` and `tee_param` arrays for `TA_CMD_BNXT_FASTBOOT` and `TA_CMD_BNXT_COPY_COREDUMP`. `tee_bnxt_fw_probe()` opens the OP-TEE context, opens a session using the UUID from the tee bus device ID, allocates shared memory, and stores global state. Remove and shutdown release the shared memory, session, and context.

## Control Flow, State, And Persistence
Probe establishes the only persistent runtime state in `pvt_data`. `tee_bnxt_fw_load()` checks the context and invokes command 0 with no parameters. `tee_bnxt_copy_coredump()` loops over the requested size in chunks no larger than the shared-memory pool, passes offset/size to the TA, maps the returned shared memory with `tee_shm_get_va()`, copies to the caller buffer, and advances offset.

## Dependencies And Integration Points
The file depends on the TEE client framework, OP-TEE implementation ID matching, UUID device matching, and `linux/firmware/broadcom/tee_bnxt_fw.h` consumers. It registers a `tee_client_driver` with UUID `6272636D-2019-0716-4243-4D5F53434849`.

## Risks And Test Signals
The global singleton means multiple matching devices would overwrite state; exported calls fail with `-ENODEV` before probe or after remove. Both TA invocation failures and nonzero TA return codes collapse to `-EINVAL`, which hides exact TA error semantics. Coredump copying relies on `void *` arithmetic and repeated shared-memory VA lookup. Tests should cover probe error unwinding, no-context exported calls, fastboot success/failure, chunked coredump copies larger than 4 MiB, remove/shutdown idempotence expectations, and OP-TEE-only context matching.
