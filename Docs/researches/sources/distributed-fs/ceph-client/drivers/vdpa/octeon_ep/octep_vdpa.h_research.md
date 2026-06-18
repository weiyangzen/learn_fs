# sources/distributed-fs/ceph-client/drivers/vdpa/octeon_ep/octep_vdpa.h

Purpose: shared Marvell Octeon endpoint vDPA definitions for PCI IDs, BAR layout, mailbox/capability registers, hardware state, queue state, and hardware-helper prototypes.

Important APIs/types/functions: defines Octeon PF/VF device IDs, mailbox/caps BAR indices, readiness signatures, mailbox register macros, device lifecycle enum, `struct octep_vring_info`, vendor capability data layout, and `struct octep_hw`. Declares status/reset, queue select/notify/address/size/ready/state, config read, capability read, feature get/set, and feature verification helpers.

Control flow: no implementation here; it establishes the contract between Octeon main and hardware files.

State and persistence: `struct octep_hw` stores PCI device, BAR mappings, common/device/isr/notify regions, per-vq info, config callback, features, queue count, config size, IRQ list, and virtio device id. Runtime persistence is in memory for the PCI device lifetime.

Dependencies and integration: includes PCI, vDPA, modern virtio-pci, virtio net/block/crypto/config, and uapi vDPA headers. Intended for `octep_vdpa_main.c` and `octep_vdpa_hw.c` named by the Makefile.

Risks: readiness depends on firmware/emulation signatures and BAR initialization. Register macros encode PF/VF mailbox addressing; incorrect function type or ring index can target wrong offsets. The header supports several virtio device classes, so config sizing and feature verification in implementation must be device-id aware.

Test signals: compile main/hw users, probe against supported PF/VF IDs, firmware-ready polling, capability parsing, queue notify/state operations, feature verification, and IRQ callback delivery through `octep_vring_info`.
