# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_dev.h

Purpose: this header exposes vNIC device abstractions, descriptor ring metadata, interrupt mode enum, BAR descriptor, MMIO 64-bit access fallbacks, and vNIC device APIs.

Important APIs, types, and functions: `enum vnic_dev_intr_mode` names unknown, INTx, MSI, and MSI-X modes. `struct vnic_dev_bar` describes mapped PCI BARs. `struct vnic_dev_ring` tracks coherent descriptor memory, aligned base, descriptor size/count, and availability. Function declarations cover private data lookup, resource count/address lookup, ring allocation/free/clear, devcmd execution, firmware info, config reads, stats, notify, link status, lifecycle commands, resource discovery, interrupt mode get/set, unregister, and devcmd initialization.

Control flow: SNIC probe creates a `vnic_dev`, reads resources/config, allocates rings, sets MSI-X mode, and uses lifecycle commands. Resource-specific code uses `svnic_dev_get_res()` to bind WQ/CQ/INTR control structures.

State and persistence: header-defined structures are runtime-only and back DMA/MMIO state. No persistent state exists.

Dependencies and integration: includes `vnic_resource.h` and `vnic_devcmd.h`. It provides `readq`/`writeq` fallbacks for architectures without native helpers.

Risks: `vnic_dev` is opaque to most callers, so lifecycle ordering is enforced by convention. Descriptor ring fields must be initialized through `svnic_dev_desc_ring_size()` before allocation. `writeq` fallback writes low then high halves, which must match device expectations.

Test signals: compile on architectures with and without native `readq/writeq`, ring alignment checks, resource lookup bounds, and lifecycle call ordering in probe/remove fault injection.
