# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_cmdq.c

## Purpose
Implements the HINIC synchronous command queue used by the driver to send low-level commands to firmware or on-card modules after the management and CEQ infrastructure is available. It owns command-buffer allocation, WQE construction, command doorbells, completion handling from the command CEQ, and firmware command queue context setup.

## Important APIs, Types, and Functions
Public entry points are `hinic_alloc_cmdq_buf`, `hinic_free_cmdq_buf`, `hinic_cmdq_direct_resp`, `hinic_init_cmdqs`, and `hinic_free_cmdqs`. Important helpers include `cmdq_prepare_wqe_ctrl`, `cmdq_set_lcmd_wqe`, `cmdq_set_direct_wqe`, `cmdq_sync_cmd_direct_resp`, `cmdq_ceq_handler`, `cmdq_init_queue_ctxt`, `init_cmdqs_ctxt`, and `hinic_set_cmdq_depth`.

## Control Flow
Initialization creates a DMA pool for 2 KiB command buffers, allocates command work queues, initializes each `hinic_cmdq`, writes command queue contexts to firmware through `HINIC_COMM_CMD_CMDQ_CTXT_SET`, registers `cmdq_ceq_handler` on CEQ event `HINIC_CEQ_CMDQ`, and sets the firmware command queue depth. A synchronous command allocates a WQE under `cmdq_lock`, stores stack-local completion and error-code pointers by producer index, formats the WQE in big endian, writes the first 8 bytes last, rings the command doorbell, and waits up to `CMDQ_TIMEOUT`. CEQ processing drains completed WQEs, distinguishes arm commands from regular commands through saved header data, completes waiters, clears the hardware busy bit, returns WQEs, and sends a follow-up arm command when needed.

## State and Persistence Behavior
Persistent runtime state is in `struct hinic_cmdqs` and per-queue `struct hinic_cmdq`: DMA pool, saved WQs, command queue page metadata, doorbell bases, completion pointer tables, errcode pointer tables, lock, and wrapped bit. Hardware-visible state includes command WQ pages, command queue context PFNs, CEQ arm/en bits, command depth, and doorbell writes. No disk state is kept.

## Dependencies and Integration Points
Depends on `hinic_hw_wq` for WQE allocation, `hinic_hw_wqe` layouts, `hinic_hw_mgmt` for context commands, `hinic_hw_eqs` for CEQ callbacks, and `hinic_hw_io` for doorbell areas. It is used by IO setup to program SQ/RQ contexts and clean offload context, and by other modules that need direct-response firmware commands.

## Risks
Timeout handling must null stack-local completion and errcode pointers before returning, otherwise late CEQ completions could dereference invalid stack addresses. Doorbell ordering relies on `wmb()` and first-8-byte-last WQE writes. The CEQ handler assumes WQE size inference from header and correct saved arm bit semantics. Error unwinds must unregister CEQ callbacks before freeing command queue tables. Endian conversion mistakes silently corrupt firmware commands.

## Test Signals
Useful signals include command queue init/free across PF and VF paths, direct response success and nonzero firmware error code, command timeout with CEQ dump, CEQ arm command completion, queue full returning `-EBUSY`, command buffer size validation, module unload with outstanding command activity, and fault injection through failed WQ/DMA-pool/context setup.
