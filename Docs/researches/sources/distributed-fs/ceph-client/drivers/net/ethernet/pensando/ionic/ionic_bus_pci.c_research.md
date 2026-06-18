# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_bus_pci.c

Purpose: Implements the Ionic PCI bus driver: device matching, BAR mapping, probe/remove, SR-IOV VF bookkeeping, PCI error/reset recovery, MSI-X vector helpers, and doorbell page mapping.

Important APIs and flow: `ionic_probe()` allocates devlink-private `struct ionic`, sets DMA masks, calls `ionic_setup_one()` for PCI enable/regions/BAR0 mapping/device identify/init/port init/CMB discovery, sizes and allocates the LIF, initializes existing VFs, registers devlink and netdev LIF, registers the RDMA auxiliary device, and starts watchdog/doorbell work. `ionic_remove()` shuts down timers/work, unregisters auxiliary/devlink/LIF, frees queues/IRQs, resets port/device, clears PCI mappings, and frees devlink storage. `ionic_sriov_configure()` enables/disables VFs and manages DMA-backed VF stats through `ionic_vf_alloc()` and `ionic_vf_dealloc()`. FLR/AER paths use `ionic_reset_prepare()` and `ionic_reset_done()` to tear down and rebuild PCI/LIF state.

State and persistence: Persists BAR metadata, mapped BAR0, VF arrays and VF stats DMA addresses, devlink private state, LIF state, IRQ vectors, CMB discovery data, and watchdog/doorbell scheduling over the probe lifetime.

Dependencies and integration: Integrates PCI core, MSI-X, devlink, debugfs, Ionic device commands, LIF lifecycle, auxiliary bus, SR-IOV, and PCI error handlers.

Risks and test signals: Probe unwind spans many subsystems and must match remove ordering. Reset paths assume `ionic->lif` is valid, so error recovery before LIF allocation is a sensitive case. VF stats DMA setup ignores older firmware command failures but must still unmap memory. Test probe failure injection at each stage, FLR while netdev is up, AER frozen channel, SR-IOV enable/disable during firmware reset, doorbell BAR mapping, and module unload after partial probe.
