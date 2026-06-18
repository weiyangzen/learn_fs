# sources/distributed-fs/ceph-client/security/integrity/Kconfig

Purpose: defines configuration for the Linux integrity subsystem, including IMA, EVM, signature verification, asymmetric keys, trusted/platform/machine keyrings, platform key loading, and integrity audit.

Important APIs, types, and functions: Kconfig symbols include `INTEGRITY`, `INTEGRITY_SIGNATURE`, `INTEGRITY_ASYMMETRIC_KEYS`, `INTEGRITY_TRUSTED_KEYRING`, `INTEGRITY_PLATFORM_KEYRING`, `INTEGRITY_MACHINE_KEYRING`, `INTEGRITY_CA_MACHINE_KEYRING`, `INTEGRITY_CA_MACHINE_KEYRING_MAX`, `LOAD_UEFI_KEYS`, `LOAD_IPL_KEYS`, `LOAD_PPC_KEYS`, and `INTEGRITY_AUDIT`. It sources `ima/Kconfig` and `evm/Kconfig`.

Control flow: config dependencies/selects determine which keyrings, parsers, crypto algorithms, platform loaders, and audit support are compiled. `INTEGRITY` gates the whole subtree.

State and persistence: no runtime state directly; it controls compiled-in runtime state such as keyrings and LSM components.

Dependencies and integration: integrates with `SECURITY`, `KEYS`, `SIGNATURE`, asymmetric key infrastructure, system trusted/blacklist/secondary keyrings, EFI/S390/PPC platform support, and audit.

Risks and test signals: dependency errors can produce missing verification paths or overly broad trust. Test signals are config matrix builds for IMA/EVM/signature/keyring combinations and boot-time keyring availability.
