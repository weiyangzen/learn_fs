# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_lif_cfg.c

Purpose: adapter between the Ionic Ethernet LIF identity and the RDMA driver's compact LIF configuration. It extracts firmware identity limits, queue type identifiers, doorbell resources, stats support, UDMA layout, page-size capabilities, and expanded-doorbell support.

Important APIs/functions: `ionic_fill_lif_cfg()` is the main initializer. `ionic_lif_netdev()` returns a held netdev reference. `ionic_lif_fw_version()` copies the firmware version string. `ionic_lif_asic_rev()` exposes the ASIC revision. `ionic_get_expdb()` is an internal helper that converts physical CMB expanded-doorbell page availability into RDMA flags.

Control flow: `ionic_fill_lif_cfg()` reads `lif->ionic->ident.lif.rdma` and device identity, stores device and LIF pointers, kernel doorbell page, interrupt control base, physical doorbell BAR address, queue bases/counts/types, resource counts, RDMA/admin opcode limits, stats type, UDMA shift/count, maximum stride, and expanded-doorbell capability. For RDMA identity version at least 2.1 it trusts firmware `page_size_cap`; older identities use a hard-coded 4K/2M/1G mask.

State and persistence: the function populates caller-owned `struct ionic_lif_cfg`, which becomes part of `struct ionic_ibdev`. It snapshots firmware and LIF configuration at RDMA device setup time; it does not allocate long-lived resources except the netdev reference in `ionic_lif_netdev()`.

Dependencies and integration: depends on Ionic Ethernet driver internals (`ionic.h`, `ionic_lif.h`), PCI BAR/device identity fields, RDMA identity structures, and local config constants in `ionic_lif_cfg.h`.

Risks: values are trusted from device identity and must be validated by later resource creation. `udma_count` is currently forced to two, so hardware with a different future UDMA count would require updates. Callers of `ionic_lif_netdev()` must balance the `dev_hold()`.

Test signals: probe on older and newer firmware identity versions, page-size capability reporting, expanded-doorbell feature combinations, queue count clamping by admin setup, and netdev reference leak checks.
