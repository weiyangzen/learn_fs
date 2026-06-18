# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_auxr.h

Purpose: Defines the public contract between the `bnge` L2 NIC driver and its RDMA/RoCE auxiliary device.

Important APIs/types: `struct bnge_msix_info` describes vector, ring index, and doorbell offset handed to the aux driver. `struct bnge_fw_msg` wraps firmware command/response buffers and timeout for `bnge_send_msg()`. `struct bnge_auxr_info` stores client handle and allocated MSI-X count. `struct bnge_auxr_dev` is the shared aux-device payload containing netdev, PCI device, BAR0, MSI-X array, RoCE capability flags, doorbell sizes/offset, chip/stat/PF metadata, enable state, resource counts, and a mutex. Exported functions cover aux lifecycle, client register/unregister, and firmware send.

Control flow support: Core probe initializes and adds the auxiliary device; the RDMA client later calls register/unregister and send-message hooks. The header also defines minimum RoCE ring/stat context requirements and max MSI-X vectors.

State/persistence: Aux state persists while the auxiliary device exists. Capability flags record RoCE v1/v2 support and MSI-X allocation. `en_state` mirrors `bnge_dev` driver state for client visibility.

Dependencies/integration: Depends on Linux auxiliary bus and shared `struct bnge_dev`; consumers also rely on firmware HSI structures and PCI/netdev context supplied in the C implementation.

Risks/test signals: Any ABI-like change affects the auxiliary RDMA client. Validate struct field expectations with the RDMA module, vector count limits, RoCE v1/v2 flag propagation, locking around aux operations, and removal ordering.
