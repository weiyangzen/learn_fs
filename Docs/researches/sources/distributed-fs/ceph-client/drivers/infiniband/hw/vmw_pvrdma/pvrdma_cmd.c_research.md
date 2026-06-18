<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cmd.c

## Purpose

Implements the synchronous guest-to-device command path for PVRDMA. Commands are written into a DMA-coherent command slot, signaled through a request register, and optionally completed by copying the response slot after an interrupt-driven completion.

## Important APIs, Types, And Functions

`PVRDMA_CMD_TIMEOUT` is 10 seconds. `pvrdma_cmd_post()` serializes command submissions with `cmd_sema`, copies a `union pvrdma_cmd_req` into `dev->cmd_slot`, writes `PVRDMA_REG_REQUEST`, checks `PVRDMA_REG_ERR`, and receives responses through `pvrdma_cmd_recv()`. `pvrdma_cmd_recv()` waits for `dev->cmd_done`, copies `dev->resp_slot`, and validates the response ack code.

## Control Flow

Callers fill a command union, call `pvrdma_cmd_post()`, and pass a response union plus expected response code when a response is needed. The response interrupt handler in `pvrdma_main.c` completes `cmd_done`. Timeout or interruptible wait interruption is reported as `-ETIMEDOUT`; wrong response ack is `-EFAULT`; device error register nonzero is also reported as `-EFAULT`.

## State And Persistence Behavior

Command state lives in per-device coherent command/response slots and the command completion. `cmd_sema` guarantees only one outstanding command per device. `cmd_lock` protects slot copies.

## Dependencies And Integration Points

Depends on `pvrdma_write_reg()`, `pvrdma_read_reg()`, command/response unions from `pvrdma_dev_api.h`, and the response interrupt path.

## Risks And Edge Cases

The path treats interrupted waits like timeouts. If an interrupt is lost or the device writes a mismatched ack, all higher-level verbs operations fail. The `BUILD_BUG_ON` ties command union sizing to `pvrdma_cmd_modify_qp`; ABI changes must preserve slot sizing.

## Test Signals

Exercise every command with expected response codes, no-response destroy commands, timeout injection, wrong ack injection, and concurrent callers verifying semaphore serialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_cmd.c -->
