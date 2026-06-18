# sources/distributed-fs/ceph-client/drivers/tee/optee/rpc.c

## Purpose
`rpc.c` handles OP-TEE RPC commands requested by secure world. It services time, notification, sleep, I2C, shared-memory allocation/free through supplicant helpers, RPMB probe/frame routing either in kernel or via tee-supplicant, and generic forwarding to the supplicant.

## Important APIs, Types, And Functions
`handle_rpc_func_cmd_get_time()` returns real time in one value output param. `handle_rpc_func_cmd_i2c_transfer()` converts OP-TEE params to Linux TEE params, validates the exact attr layout, acquires an I2C adapter, performs one read or write transfer, and returns transferred length. `handle_rpc_func_cmd_wq()` implements notification wait/send using `optee_notif_wait()` and `optee_notif_send()`. `handle_rpc_func_cmd_wait()` sleeps interruptibly for a requested number of milliseconds.

`handle_rpc_supp_cmd()` converts params, calls `optee_supp_thrd_req()`, then converts output params back. `optee_rpc_cmd_alloc_suppl()` and `optee_rpc_cmd_free_suppl()` request application SHM allocation/free through tee-supplicant, using the returned SHM id to get a kernel reference. RPMB helpers probe/reset devices, iterate matching RPMB devices, copy device ids to output memrefs, and route RPMB frames through `rpmb_route_frames()` when in-kernel routing is enabled.

`optee_rpc_cmd()` dispatches command ids and chooses in-kernel or supplicant RPMB routing based on `optee->in_kernel_rpmb_routing`.

## Control Flow And State
RPC handling happens synchronously while a secure-world call is suspended. Results are written back into the same `optee_msg_arg`. For supplicant commands, a kernel thread queues a request and blocks until userspace receives and sends a response. RPMB probe state is persisted in `optee->rpmb_dev` under `rpmb_dev_mutex` so probe-next can iterate devices across calls.

## Dependencies And Integration Points
The file integrates with Linux timekeeping, I2C, RPMB, TEE parameter conversion backend ops, supplicant request queues in `supp.c`, notification state in `notif.c`, and RPC command definitions in `optee_rpc_cmd.h`.

## Risks
I2C RPC exposes normal-world I2C transfers to secure world; strict attr validation helps but bus/address policy is delegated to secure world and kernel adapter availability. In `handle_rpc_func_rpmb_frames()`, `tee_shm_get_va()` results are not checked with `IS_ERR()` before `rpmb_route_frames()`, unlike other paths. `optee_rpc_cmd_alloc_suppl()` maps supplicant return failures to `-ENOMEM`, losing error specificity. RPMB routing state must be reset on probe-reset to avoid stale device references.

## Test Signals
Malformed RPC parameter counts/types for every command. I2C transfers with missing adapter, unsupported 10-bit mode, invalid operation, and transfer errors. Notification wait timeout and send. Supplicant absent with blocking and nonblocking callers. RPMB probe with multiple device types, no devices, short output buffer, and frame routing errors.
