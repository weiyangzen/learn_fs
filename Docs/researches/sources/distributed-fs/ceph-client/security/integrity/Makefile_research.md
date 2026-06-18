# sources/distributed-fs/ceph-client/security/integrity/Makefile

Purpose: composes integrity subsystem objects based on Kconfig and establishes the relative build order of IMA and EVM.

Important APIs, types, and functions: builds `integrity.o` from `iint.o` plus conditional objects: `integrity_audit.o`, `digsig.o`, `digsig_asymmetric.o`, platform/machine keyring loaders, EFI/S390/PPC platform certificate handlers, and `efi_secureboot.o`. It descends into `ima/` and `evm/`.

Control flow: Kbuild appends objects according to `CONFIG_*` symbols. The comment notes IMA/EVM LSM relative order depends on the listed order.

State and persistence: no runtime state directly.

Dependencies and integration: tied to Kconfig symbols from integrity, platform certs, IMA, EVM, and EFI.

Risks and test signals: build order can affect LSM ordering and therefore integrity behavior. Test signals are successful builds across config matrices and expected object inclusion/exclusion.
