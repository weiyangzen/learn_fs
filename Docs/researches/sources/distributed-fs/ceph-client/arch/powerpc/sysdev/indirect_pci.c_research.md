<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/indirect_pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/indirect_pci.c

Purpose: Provides generic indirect PCI config-space access for PowerPC host bridges with address/data config registers.

Important APIs/types/functions: Implements `__indirect_read_config()`, `indirect_read_config()`, `indirect_write_config()`, `setup_indirect_pci()`, and static `indirect_pci_ops`.

Control flow: Read/write helpers reject unsupported devices based on no-link and platform exclusion flags, compute type-0/type-1 config addressing, handle extended register bits, write the config address using big- or little-endian MMIO, and access the config data window at the offset lane. Write suppresses primary-bus writes and clears broken MRM cache-line-size writes when configured. Setup maps the address/data pages and installs the PCI ops into the controller.

State and persistence: Persistent state lives in `struct pci_controller`: `cfg_addr`, `cfg_data`, `ops`, and `indirect_type` flags. Hardware state changes occur through config cycles.

Dependencies and integration points: Depends on PowerPC PCI host bridge data, `ppc_md.pci_exclude_device`, endian MMIO helpers, and platform host setup code such as Grackle or embedded controllers.

Risks: No locking is done around shared config address/data registers, so callers must rely on PCI core serialization. Mis-set endian/type/extended flags produce silent bad config cycles. `PPC_INDIRECT_TYPE_NO_PCIE_LINK` only permits root device/function zero.

Test signals: PCI enumeration on indirect host bridges, config byte/word/dword reads and writes, type-1 access to subordinate buses, excluded-device handling, extended register offsets, and errata flags.

Source read size: 172 lines, 4486 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/indirect_pci.c -->
