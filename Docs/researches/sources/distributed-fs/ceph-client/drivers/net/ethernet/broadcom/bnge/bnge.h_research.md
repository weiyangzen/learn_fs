# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge.h

Purpose: Main private header for the Broadcom ThorUltra `bng_en` NIC driver. It defines driver identity, board enum, firmware capability flags, enable flags, RSS/resource constants, `struct bnge_dev`, and doorbell helpers used across core, devlink, ethtool, auxiliary RDMA, netdev, TX/RX, resource, and HWRM files.

Important APIs/types: `struct bnge_dev` is the persistent PCI function context: device/P PCI/netdev pointers, DSN/VPD strings, BARs, doorbell geometry, HWRM command state, firmware version/capability data, PF info, driver state bits, context memory, resource limits, RSS config, ring counts, auxiliary RDMA resources, MTU/stat sizes, traffic-class mapping, IRQ table, aux device pointers, link info, and PHY flags. Helpers include `bnge_is_roce_en()`, `bnge_is_agg_reqd()`, `bnge_writeq()`, `bnge_db_write()`, `bnge_aux_registered()`, and `bnge_aux_get_msix()`.

Control flow support: Probe fills `bnge_dev`, HWRM updates capabilities/resources, netdev alloc attaches `bd->netdev`, aux and ethtool read the same state, and TX/RX code uses doorbell helpers to notify hardware.

State/persistence: This header defines most persistent driver state. Firmware capabilities (`fw_cap`), enabled features (`flags`), RSS tables, IRQ accounting, aux device state, VPD strings, link info, and HWRM sequence/lock state remain for device lifetime. On 32-bit systems, `db_lock` protects atomic 64-bit doorbell writes.

Dependencies/integration: Includes Linux ethernet helpers, firmware HSI header, and local resource/aux headers. It references `struct bnge_net` and many macros from sibling headers not in this work item, showing that this file is a cross-module contract.

Risks/test signals: Field layout and flag semantics are shared widely. Doorbell writes are especially sensitive to 32-bit atomicity and ring index/epoch masking. Test compile with 32-bit and 64-bit, HWRM probe paths, RSS sizing, RoCE enable/disable, jumbo/TPA aggregation conditions, and TX/RX doorbell behavior.
