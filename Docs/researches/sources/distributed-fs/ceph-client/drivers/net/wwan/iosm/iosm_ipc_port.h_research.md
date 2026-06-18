# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_port.h

Purpose: declares the IOSM WWAN control-port wrapper and lifecycle APIs.

Important types/APIs: `struct iosm_cdev` holds the Linux `wwan_port`, imem, device, PCIe object, WWAN port type, active IPC channel, and configured channel ID. APIs are `ipc_port_init` and `ipc_port_deinit`.

Control flow role: imem runtime setup creates one `iosm_cdev` per supported configured control channel. The implementation registers WWAN port operations that call imem ops for open, close, and TX. State persists only while the modem is fully functional and is cleaned when imem clears `FULLY_FUNCTIONAL`.

Dependencies: includes Linux WWAN APIs and imem ops, which provide channel and protocol access. Risks: header-level circular include pressure through imem_ops, channel lifetime tied to WWAN callbacks, and port arrays limited by `IPC_MEM_MAX_CHANNELS`. Test signals: build coverage with all configured WWAN port types, init/deinit balance, stop after failed start, and channel pointer validity during modem crash/cleanup.
