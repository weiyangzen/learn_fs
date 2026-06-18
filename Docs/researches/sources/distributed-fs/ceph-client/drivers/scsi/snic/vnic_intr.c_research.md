# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_intr.c

Purpose: this file implements minimal vNIC interrupt control allocation, initialization, cleanup, and free helpers.

Important APIs, types, and functions: `svnic_intr_alloc()` binds a `vnic_intr` to an interrupt control MMIO resource by index. `svnic_intr_init()` programs coalescing timer, coalescing type, mask-on-assertion, and clears credits. `svnic_intr_clean()` clears interrupt credits. `svnic_intr_free()` drops the control pointer.

Control flow: SNIC resource allocation calls `svnic_intr_alloc()` for each interrupt vector and later `svnic_intr_init()` after CQ/WQ setup. ISR paths return credits through inline helpers from `vnic_intr.h` rather than this file. Cleanup calls `svnic_intr_clean()` and `svnic_intr_free()`.

State and persistence: runtime state is `vnic_intr.index`, `vdev`, and MMIO `ctrl` pointer plus hardware credit/coalescing registers. No persistent state exists.

Dependencies and integration: depends on vNIC resource lookup, vNIC interrupt structures, PCI/MMIO accessors, and SNIC MSI-X setup.

Risks: allocation fails if resource discovery did not expose enough interrupt controls. Initialization assumes the resource is valid and hardware accepts timer/type values already clamped in SNIC config. Cleaning credits while interrupts are still enabled would lose interrupt accounting.

Test signals: resource count fault injection, interrupt coalescing configuration, cleanup after active interrupts, and remove/unbind with vectors masked.
