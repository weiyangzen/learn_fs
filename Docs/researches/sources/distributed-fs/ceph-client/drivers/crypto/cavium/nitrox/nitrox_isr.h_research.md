# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_isr.h

Purpose: declares NITROX interrupt registration helpers and the optional SR-IOV configure callback.

Important APIs: `nitrox_register_interrupts()`, `nitrox_unregister_interrupts()`, `nitrox_sriov_register_interupts()`, and `nitrox_sriov_unregister_interrupts()` manage normal and SR-IOV PF interrupt modes. With `CONFIG_PCI_IOV`, `nitrox_sriov_configure()` is external; otherwise an inline stub returns success.

State and dependencies: owns no state, depends on `nitrox_dev.h` and PCI types. It hides `CONFIG_PCI_IOV` from callers.

Integration points: main PCI driver can wire `sriov_configure` and interrupt setup without conditional code.

Risks and test signals: risks include misspelled `interupts` being part of the API, and the no-op SR-IOV stub making enable requests appear successful when IOV support is compiled out if callers do not gate them. Test signals include builds with PCI_IOV on/off and correct function resolution for normal and SR-IOV interrupt modes.
