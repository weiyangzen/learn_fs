# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_ffa.h

## Purpose
`optee_ffa.h` defines the OP-TEE FF-A ABI constants shared between normal-world Linux and secure-world OP-TEE for FF-A direct messaging, capability exchange, shared-memory operations, async notifications, protected memory, and yielding calls.

## Important APIs, Types, And Functions
The file declares OP-TEE FF-A API version 1.0 and separates blocking and yielding service ids with `OPTEE_FFA_BLOCKING_CALL()` and `OPTEE_FFA_YIELDING_CALL()`. Blocking calls include API version, OS version, capability exchange, unregister shared memory, enable async notification, and release protected memory. Capability bits describe argument offsets, async notification, RPMB probing, and protected memory support.

Yielding call constants define `OPTEE_FFA_YIELDING_CALL_WITH_ARG`, `OPTEE_FFA_YIELDING_CALL_RESUME`, and return reasons: done, RPC command, and interrupt. Register comments document how `w3-w7` carry service ids, shared-memory handles, offsets, resume info, and return status.

## Control Flow And State
This header has no runtime state. It constrains how `ffa_abi.c` fills `struct ffa_send_direct_data` and interprets secure-world responses.

## Dependencies And Integration Points
It depends on `linux/arm_ffa.h` for FF-A definitions and is included by `ffa_abi.c`. The comments state it is exported by OP-TEE and kept in sync with secure-world code, so mismatches are ABI breakage rather than local implementation bugs.

## Risks
The ABI assumes FF-A 1.0 and AArch32 SMC register conventions for direct messages. If secure world advertises capabilities inconsistently, Linux may pass nonzero argument offsets or notification ids incorrectly. Protected-memory release and shared-memory unregister use global handles split into low/high 32-bit registers, so truncation or endian mistakes would be severe.

## Test Signals
Compatibility tests should validate major/minor negotiation, capability-bit handling, yielding call return reason handling, and shared/protected memory handle split/recombine behavior across 32-bit register fields.
