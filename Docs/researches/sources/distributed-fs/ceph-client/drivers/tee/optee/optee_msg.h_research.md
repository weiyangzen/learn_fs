# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_msg.h

## Purpose
`optee_msg.h` defines the OP-TEE message protocol carried by both SMC and FF-A transports. It describes parameter encodings, message argument layout, API identity/revision values, normal-world commands, shared-memory registration commands, async notification commands, and protected-memory commands.

## Important APIs, Types, And Functions
Parameter attribute constants distinguish none, value, registered memory, FF-A memory, and temporary memory inputs/outputs/inouts. Flags include `OPTEE_MSG_ATTR_META`, `OPTEE_MSG_ATTR_NONCONTIG`, and cache attribute fields. `struct optee_msg_param_tmem`, `_rmem`, `_fmem`, and `_value` define the union arms inside `struct optee_msg_param`. `struct optee_msg_arg` is the command envelope with command id, function id, session, cancel id, return code/origin, parameter count, and a flexible parameter array. `OPTEE_MSG_GET_ARG_SIZE()` computes the allocation size.

Command constants include session open/invoke/close/cancel, SHM register/unregister, bottom-half execution, async notification stop, protected memory lend/reclaim/config/assign, and `OPTEE_MSG_FUNCID_CALL_WITH_ARG`. The header also defines UID/revision constants for API probing and protected-memory use-case values.

## Control Flow And State
There is no state in the header, but its structures are the persistent ABI stored in shared memory during every OP-TEE call. Common call code fills `optee_msg_arg`, backends translate Linux params into transport-specific memory parameter forms, secure world updates the same shared memory, and common code copies results back.

## Dependencies And Integration Points
The file is included by `optee_private.h`, SMC/FF-A backend code, and common call/RPC code. It is dual-licensed because it is an ABI contract shared with OP-TEE secure-world sources.

## Risks
Any layout change breaks the shared-memory ABI. Noncontiguous temporary memory uses 4 KiB page-list assumptions even on larger Linux pages, so helper code must preserve the documented chaining format. FF-A and SMC use different memory union arms for conceptually similar memrefs; using the wrong attr family will make secure world reject or misinterpret buffers.

## Test Signals
Compile-time layout/size checks, open-session meta-parameter tests, registered and temporary SHM registration tests, NULL memref tests, noncontiguous user buffer registration, and protected-memory command round trips are the key signals.
