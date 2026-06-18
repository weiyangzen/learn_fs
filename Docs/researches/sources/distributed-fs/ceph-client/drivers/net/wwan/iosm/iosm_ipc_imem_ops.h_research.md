# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_imem_ops.h

Purpose: declares the public operation boundary between imem and upper consumers: WWAN network interfaces, WWAN control ports, and devlink SIO flashing/coredump access.

Important APIs/constants: `IPC_READ_TIMEOUT`, `PSI_START_DEFAULT_TIMEOUT`, `BOOT_CHECK_DEFAULT_TIMEOUT`, mux session range constants, and prototypes for system port open/close/write, WWAN open/close/transmit/channel init, and devlink open/close/read/write/notify_rx.

Control flow role: callers do not manipulate pipes directly; they use these APIs so imem can enforce phase checks, channel reservation/opening, DMA mapping, task-queue scheduling, blocking read/write completions, and mux session routing. State is owned by `iosm_imem`, `iosm_cdev`, and `iosm_devlink`; this header does not persist data itself.

Dependencies: includes mux codec, which pulls in mux/imem/protocol types, so include ordering is important and circularity is managed through the local driver headers. Risks are API misuse from wrong phase or wrong channel ID, especially because some calls are blocking and may be used from contexts that must sleep. Test signals: build coverage for all upper layers, phase/unit tests around open calls, timeout behavior for read and boot, and mux session bounds 0..7.
