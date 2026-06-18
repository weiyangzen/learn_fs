# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/Makefile

Purpose: links the NITROX CNN55XX PF driver composite object.

Important APIs and control flow: `obj-$(CONFIG_CRYPTO_DEV_NITROX_CNN55XX) += n5pf.o` builds the driver. Core members include main PCI code, ISR, lib, HAL, request manager, algorithm registration, mailbox, skcipher, and AEAD. `nitrox_sriov.o` is conditional on `CONFIG_PCI_IOV`; `nitrox_debugfs.o` is conditional on `CONFIG_DEBUG_FS`.

State and dependencies: no runtime state; object membership controls which exported helpers exist for SR-IOV and debugfs paths.

Integration points: links the module named `n5pf`, matching Kconfig help.

Risks and test signals: risks include optional SR-IOV/debugfs symbols needing stub headers and object omission causing unresolved references. Test signals include links with PCI_IOV on/off, DEBUG_FS on/off, and module exposing both skcipher and AEAD registrations.
