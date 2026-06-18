# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/ionic_lif_cfg.h

Purpose: LIF configuration data contract for Ionic RDMA. It defines version/page-size constants, expanded-doorbell capability bits, `struct ionic_lif_cfg`, and the small set of LIF helper prototypes used by the RDMA device setup path.

Important APIs/types: `IONIC_VERSION()` composes major/minor values for identity checks. `IONIC_PAGE_SIZE_SUPPORTED` is the fallback 4K/2M/1G page-size mask. `IONIC_EXPDB_*` bits describe supported expanded-doorbell WQE sizes. `struct ionic_lif_cfg` stores hardware device pointers, LIF indices, kernel doorbell ID/page, interrupt control MMIO, physical doorbell base, page/resource limits, queue bases/counts/types, UDMA grouping, RDMA/admin opcode counts, maximum stride, and expanded-doorbell flags.

Control flow: `ionic_fill_lif_cfg()` populates the structure from an Ethernet LIF before RDMA resources are created. Other Ionic RDMA files then use this immutable-ish configuration for DMA mapping device selection, doorbell ringing, queue ID allocation, stats/admin opcode checks, and user-visible capability decisions.

State and persistence: all fields are runtime configuration cached from firmware/LIF identity. The header itself has no code-managed storage. `dbpage`, `intr_ctrl`, and `db_phys` point into PCI/device resources owned by the Ethernet Ionic device.

Dependencies and integration: declares opaque `struct ionic_lif` use and returns `struct net_device`. The implementation includes Ethernet driver headers; RDMA callers include only this contract.

Risks: the include guard lacks a `#define _IONIC_LIF_CFG_H_`, so repeated inclusion in one translation unit would not be prevented by this file alone. The current source appears to rely on include graph behavior and should be fixed if touched. Hardware capability fields must stay synchronized with firmware identity definitions.

Test signals: clean build with repeated includes, RDMA probe using all queue/resource fields, stats opcode gating, and feature reporting for CMB/expanded-doorbell paths.
