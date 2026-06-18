# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_protocol.h

Purpose: declares the IOSM protocol shared-memory layout, doorbell IDs, IRQ vector assignments, message-ring size/timeouts, protocol object, task-queue message arguments, and public protocol APIs.

Important types/APIs: `ipc_protocol_context_info`, `ipc_protocol_device_info`, `ipc_protocol_ap_shm`, `iosm_protocol`, `ipc_call_msg_send_args`, and functions for task-queue message send, blocking message send, PM suspend/resume/s2idle/device-sleep handling, doorbell triggering, sleep notification string, init, and deinit.

Control flow role: imem and protocol_ops use the shared-memory layout for CP-visible descriptors: head/tail arrays for pipes, message ring, device info, and context info physical addresses. Doorbell constants identify HPDA, IPC state, and sleep-control interrupts. Blocking message timeouts define failure detection for boot and runtime.

State/dependencies: protocol state persists for the device lifetime and owns DMA-coherent AP shared memory plus PM state. Dependencies include imem, PM, and protocol_ops headers; this creates tight layering but keeps the shared ABI central. Risks: CP-visible struct layout drift, one-vector IRQ assumptions, response-ring size coupling to message ring entries, and blocking API use from non-sleepable contexts. Test signals: layout offset verification, timeout behavior, doorbell type coverage, init/deinit allocation balance, and include-cycle compile checks.
