# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-sh7786.c



Source read size: 168 lines, 4623 bytes.



Purpose: PCIe configuration-space operations for SH7786 root-complex ports.

Important APIs/types/functions: `sh7786_pci_ops`, `sh7786_pcie_config_access()`, `sh7786_pcie_read()`, `sh7786_pcie_write()`, root-bus self-enumeration handling, and SH4A PCIEPAR/PCTLR/PDR/ERRFR registers.

Control flow: validates bus/dev/function/offset, handles root bus devfn 0 through direct controller config registers, otherwise clears errors, programs PIO address/type, enables config access, checks completer/master/target aborts, transfers data, and disables access. Public read/write wrappers serialize with `pci_config_lock` and handle byte/word extraction or merging.

State and persistence: writes mutate PCIe controller and endpoint config space; error flags are cleared per access.

Dependencies and integration points: used by `pcie-sh7786.c`, generic PCI core, SH7786 register definitions, and PCI config locking.

Risks and test signals: root-complex self-access is special-cased because normal config transactions abort; write path performs read-modify-write and must preserve other bytes. Test root port enumeration, endpoint config cycles, absent-device errors, and unaligned access rejection.
