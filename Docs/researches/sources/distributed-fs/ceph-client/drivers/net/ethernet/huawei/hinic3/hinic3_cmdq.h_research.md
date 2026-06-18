# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_cmdq.h

## Purpose
Declares hinic3 command-queue wire formats, queue state, command-buffer wrappers, and public command-queue APIs. It is the shared interface between hinic3 firmware-command callers and the command-queue implementation.

## Important APIs And Types
Hardware WQE structs include `cmdq_header`, `cmdq_wqe_scmd`, `cmdq_wqe_lcmd`, `cmdq_completion`, and top-level `cmdq_wqe`, asserted to be exactly 64 bytes. `struct hinic3_cmd_buf` wraps a DMA pool buffer, DMA address, little-endian size, and refcount. `struct hinic3_cmdq_cmd_info` stores per-WQE in-flight command metadata: command type, completion, errcode, completion code, direct response pointer, message ID, and input/output buffers. `struct hinic3_cmdq` owns a WQ, type, wrap bit, lock, command-info array, and hwdev pointer. `struct hinic3_cmdqs` owns all command queues, the DMA pool, doorbell base, optional WQ block, enable/disable state, and command-queue count.

## Control Flow And State
The header defines the state machine implemented in `hinic3_cmdq.c`: commands transition through direct/detail response types, timeout/fake-timeout/force-stop types, and finally idle/none. The `wrapped` bit and WQ indices determine hardware ownership. `cmd_buf` refcounts protect DMA buffers across submission and asynchronous completion/flush cleanup.

## Dependencies And Integration Points
It includes `linux/dmapool.h`, `hinic3_hw_intf.h`, and `hinic3_wq.h`. Callers throughout hinic3 use `hinic3_cmdq_direct_resp()` and `hinic3_cmdq_detail_resp()` to talk to firmware; EQ code calls `hinic3_cmdq_ceq_handler()`.

## Risks And Test Signals
Risks include ABI-size changes to `cmdq_wqe`, incorrect enum use in completion handling, and lifetime bugs if command buffers are freed without refcount discipline. Signals include static assertion coverage, command-queue initialization/free, successful direct and SGE responses, timeout/flush tests, and reset reinitialization while commands are outstanding.
