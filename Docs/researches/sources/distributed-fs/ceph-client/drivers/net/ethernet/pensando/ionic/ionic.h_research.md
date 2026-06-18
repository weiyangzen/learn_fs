# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic.h

Purpose: Provides top-level Ionic driver definitions, PCI IDs, timing constants, main device state, VF state, and cross-object function declarations.

Important APIs/types/functions: `struct ionic` holds PCI/device/devlink objects, `ionic_dev`, command mutex, debugfs root, BAR descriptions, identity data, workqueue, primary LIF, queue/interrupt sizing, interrupt bitmap, CPU affinity masks, doorbell watchdog work, notifier, VF operation lock, VF array, and watchdog timer. `struct ionic_vf` stores VF policy and DMA-backed stats. Declarations expose admin queue posting/waiting, device command waits, setup/identify/init/reset, port identify/init/reset, and `ionic_doorbell_wa()`.

State and persistence: This is the root in-memory state allocated through devlink private storage in `ionic_devlink_alloc()` and attached to the PCI device. It persists for the PCI probe lifetime and is shared by bus, devlink, LIF, ethtool, firmware, auxiliary, and debugfs code.

Dependencies and integration: Includes firmware ABI (`ionic_if.h`), device primitives (`ionic_dev.h`), and devlink declarations. PCI IDs cover Pensando Ionic Ethernet PF and VF devices.

Risks and test signals: Locking contracts are spread across users: `dev_cmd_lock` serializes device commands and `vf_op_lock` protects VF arrays. Tests should cover PF/VF probe, SR-IOV changes, firmware reset, doorbell workaround devices, devlink lifecycle, and module unload after workqueue/timer activity.
