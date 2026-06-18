## sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/shm_ipc_defs.h

### Purpose
`shm_ipc_defs.h` defines the fixed shared-memory layout used by qtnfmac IPC peers.

### Important APIs, Types, And Functions
It sets `QTN_IPC_REG_HDR_SZ` to 32 bytes, `QTN_IPC_REG_SZ` to 4096 bytes, and `QTN_IPC_MAX_DATA_SZ` to the remaining payload capacity. It defines `QTNF_SHM_IPC_NEW_DATA` and `QTNF_SHM_IPC_ACK`, `struct qtnf_shm_ipc_region_header`, `union qtnf_shm_ipc_region_headroom`, and `struct qtnf_shm_ipc_region`.

### Control Flow
The implementation writes `data_len` and payload, then toggles `flags` between `NEW_DATA` and `ACK`. The 32-byte headroom ensures the payload begins at a fixed offset expected by both host and firmware.

### State, Persistence, And Dependencies
This header has no runtime state, but it defines the persistent shared-memory ABI. It depends only on Linux integer types and `BIT()`.

### Integration Points
`shm_ipc.c` validates this layout with `BUILD_BUG_ON()`. Bus code maps this structure over PCI/device shared memory, and firmware must use the same offsets and flag values.

### Risks
Changing sizes, packing, or flag meanings breaks host/firmware communication. `data_len` is 16-bit, which is sufficient for the 4064-byte payload but still requires validation before consuming inbound data.

### Test Signals
Build-time offset/size checks, firmware ABI tests, max payload transfer, invalid length injection, and flag transition tracing validate this header.
