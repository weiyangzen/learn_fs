# sources/distributed-fs/ceph-client/drivers/vdpa/ifcvf/ifcvf_base.h

Purpose: shared IFCVF constants, data structures, and hardware-helper prototypes.

Important APIs/types/functions: defines N3000 IDs, BAR constants, min queue size, MSI-X allocation modes, `struct vring_info`, `struct ifcvf_lm_cfg`, `struct ifcvf_hw`, `struct ifcvf_adapter`, and `struct ifcvf_vdpa_mgmt_dev`. Declares all hardware operations used by `ifcvf_main.c`.

Control flow: no executable flow; it establishes the contract between hardware access and vDPA glue layers.

State and persistence: describes persistent in-memory state for mapped registers, callbacks, IRQs, features, and vDPA management/adapter ownership.

Dependencies and integration: includes PCI, vDPA, modern virtio-pci, virtio net/block/config, and uapi vDPA headers.

Risks: structure fields encode hardware assumptions such as LM BAR index and MSI-X sharing modes. Consumers must initialize sentinel IRQ values and allocated `vring` arrays consistently.

Test signals: compile coverage across net and block IDs, structure use by both source files, and static analysis for uninitialized fields after allocation.
