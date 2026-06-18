# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol.c

Purpose: owns protocol shared-memory allocation, message send/wait orchestration, PM wrappers, and AP context-info publication to CP.

Important functions: `ipc_protocol_init`, `ipc_protocol_deinit`, `ipc_protocol_tq_msg_send`, `ipc_protocol_msg_send`, `ipc_protocol_doorbell_trigger`, `ipc_protocol_pm_dev_sleep_handle`, `ipc_protocol_suspend`, `ipc_protocol_resume`, and `ipc_protocol_s2idle_sleep`.

Control flow: init allocates coherent AP shared memory containing context info, device info, head/tail arrays, and message ring; fills physical addresses into the context info; writes context address to MMIO; and initializes PM. Blocking message send schedules preparation in the IPC task queue, stores a response completion in `rsp_ring`, triggers message HP update, and waits with boot/run timeout. On timeout it removes the response pointer and sends modem-timeout uevent. Suspend/resume perform PM state preparation and send host sleep messages.

State/dependencies: `iosm_protocol` stores coherent shared-memory pointer/physical address, PM state, PCIe/imem/device, response ring, and old message tail. Dependencies include protocol_ops for message/TD details, task queue, imem, MMIO, PM, uevents, and DMA coherent allocation. Risks: response pointer lifetime after timeout, task-queue synchronous semantics, DMA allocation/free balance, and PM/message deadlocks. Test signals: message success/error/timeout, response-ring cleanup, boot vs run timeout selection, coherent memory fields, suspend/resume failures, and deinit while waiters exist.
