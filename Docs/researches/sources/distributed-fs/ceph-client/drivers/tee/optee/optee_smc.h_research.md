# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_smc.h

## Purpose
`optee_smc.h` defines the SMC/HVC ABI constants, register contracts, return codes, capability bits, and helper result structures used by the OP-TEE SMC backend.

## Important APIs, Types, And Functions
Macros build SMCCC fast and standard call ids. API probe calls include call count, UID, API revision, OS UUID, OS revision, optional image loading, call-with-arg variants, shared-memory config, capability exchange, SHM cache enable/disable, thread count, async notification enable/get value, protected-memory config, and return-from-RPC.

Capability bits describe reserved SHM, unregistered SHM, dynamic SHM, virtualization, NULL memref, async notification, RPC arg support, RPMB probe, protected memory, and dynamic protected memory. RPC return values encode allocate, free, foreign interrupt, and command requests. `OPTEE_SMC_RETURN_IS_RPC()` identifies RPC returns by prefix while excluding unknown-function.

## Control Flow And State
There is no local state. The SMC backend fills registers according to this header, loops on RPC returns and thread-limit returns, and interprets fast-call capability data during probe.

## Dependencies And Integration Points
The header depends on ARM SMCCC and bitops and mirrors constants from `optee_msg.h`. It is included by `smc_abi.c`, which uses the structures as overlays on `arm_smccc_res`.

## Risks
Register field ordering is the ABI. A high/low register mixup can corrupt pointers or memory handles. SHM cache disable returns stale `tee_shm` pointers from secure world, so `smc_abi.c` must ignore them when they may not be mapped by the current kernel. Optional firmware image loading is security-sensitive and separately gated by Kconfig.

## Test Signals
SMCCC ABI probing against known OP-TEE versions, capability exchange matrix tests, dynamic versus reserved SHM probe, RPC prefix decoding, async notification value retrieval, and SHM cache enable/disable behavior during boot and shutdown.
