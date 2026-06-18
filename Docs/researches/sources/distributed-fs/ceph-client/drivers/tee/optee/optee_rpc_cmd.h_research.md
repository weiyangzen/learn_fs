# sources/distributed-fs/ceph-client/drivers/tee/optee/optee_rpc_cmd.h

## Purpose
`optee_rpc_cmd.h` defines RPC command ids and parameter contracts for services secure-world OP-TEE asks normal world to perform in kernel or through tee-supplicant.

## Important APIs, Types, And Functions
The header defines kernel-handled RPCs for time (`OPTEE_RPC_CMD_GET_TIME`), notification wait/send, suspend/sleep, shared-memory allocate/free, I2C transfer, RPMB probing, and RPMB frame routing. It also defines shared-memory types (`OPTEE_RPC_SHM_TYPE_APPL`, `OPTEE_RPC_SHM_TYPE_KERNEL`), I2C operation and flag values, and RPMB type values for eMMC, UFS, and NVMe.

## Control Flow And State
There is no state in the header. `rpc.c` and backend-specific RPC handlers inspect these command ids in `optee_msg_arg.cmd`, validate the documented parameter layouts, and either satisfy the request in kernel or forward it to tee-supplicant.

## Dependencies And Integration Points
The definitions are consumed by `rpc.c`, `smc_abi.c`, and `ffa_abi.c`. The documented parameter contracts must match OP-TEE secure-world RPC generation and tee-supplicant behavior.

## Risks
The command contracts include raw I2C and RPMB access from secure world through normal world; parameter validation and routing policy are security-sensitive. RPMB routing model must match `optee->in_kernel_rpmb_routing` to avoid user/kernel split-brain. SHM allocation/free semantics differ between application and kernel memory.

## Test Signals
Test each command id with correct and malformed parameter counts/types. Exercise I2C with unsupported 10-bit adapters and invalid transfer modes. Run RPMB probe/reset/next/frame flows with each supported RPMB type and with no device present. Verify SHM allocation/free for both APPL and KERNEL types.
