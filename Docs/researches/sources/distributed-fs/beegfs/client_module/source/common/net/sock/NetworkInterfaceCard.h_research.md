# sources/distributed-fs/beegfs/client_module/source/common/net/sock/NetworkInterfaceCard.h

Purpose: Declares BeeGFS NIC discovery and capability helpers used by connection-pool setup.

Important APIs/types/functions: `NIC_findAll`, `NIC_nicTypeToString`, `NIC_nicAddrToString`, `NIC_supportsRDMA`, and `NIC_supportedCapabilities` are the public surface around `NicAddressList` and `NicListCapabilities`.

Control flow: Consumers call `NIC_findAll` with filter/RDMA/domain parameters, then inspect the resulting list or derived capabilities. The header itself keeps implementation details in the `.c` file.

State and persistence behavior: No state is stored in the header; callers own discovered list contents.

Dependencies and integration points: Depends on `NicAddress`, `NicAddressList`, iterators, filters, and string/common helpers.

Risks: Callers must free allocated list elements with the matching BeeGFS list cleanup utilities and must understand that capability reporting reflects current discovery, not a persistent hardware registry.

Test signals: Compile/link coverage plus integration tests for standard-only, RDMA-capable, and RDMA-filtered discovery.
