# sources/distributed-fs/ceph-client/arch/mips/pci/ops-lantiq.c

## Purpose
Provides Lantiq PCI config-space read/write callbacks used by the Lantiq PCI controller.

## Important APIs, Types, And Functions
Defines `ltq_pci_read_config_dword` and `ltq_pci_write_config_dword`; internal `ltq_pci_config_access` maps config accesses through `ltq_pci_mapped_cfg` under `ebu_lock`.

## Control Flow
Access rejects non-bus-0, invalid slots, slot 0, and the SoC's own AD29 devfn. It builds a config address, performs swapped 32-bit reads/writes, executes a write barrier, clears possible master abort status through a status-command register sequence, and treats all-ones reads as not found.

## State And Persistence
No persistent software state; uses external Lantiq mapped config base and EBU lock. Hardware error status is cleared per access.

## Dependencies And Integration Points
Depends on Lantiq SoC helpers, `pci-lantiq.h`, `ltq_pci_mapped_cfg`, and global `ebu_lock`.

## Risks And Edge Cases
Endianness swabbing and master-abort cleanup are hardware-sensitive. Slot filtering is strict and may hide devices if topology differs. Uses exported-looking function names rather than a local `struct pci_ops` in this file.

## Test Signals
Lantiq PCI enumeration, all byte/word/dword config access sizes, absent-device probing, and concurrent config access stress under interrupt load are useful.
