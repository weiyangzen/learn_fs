# sources/distributed-fs/ceph-client/arch/mips/pci/ops-bonito64.c

## Purpose
Implements Bonito64 PCI config-space operations for MIPS boards.

## Important APIs, Types, And Functions
Exports `bonito64_pci_ops`; core helper `bonito64_pcibios_config_access` maps type 0/type 1 config cycles through Bonito registers, with read/write wrappers for byte, word, and dword sizes.

## Control Flow
Reads/writes validate alignment, compose type-0 IDSEL or type-1 bus/device/function addresses, clear Bonito abort status, program `BONITO_PCIMAP_CFG`, access the CKSEG1 config window, wait for writes, then detect and clear master/target aborts.

## State And Persistence
No software state. Hardware abort bits and mapping registers are mutated per access.

## Dependencies And Integration Points
Depends on Bonito64 board register macros, PCI core `struct pci_ops`, CKSEG1 uncached access, endian conversion helpers, and MIPS board builds.

## Risks And Edge Cases
Device range is limited by IDSEL mapping. Abort returns sometimes use `-1` rather than a PCIBIOS code in wrappers. Byte/word writes require read-modify-write, so abort handling must be correct.

## Test Signals
Bonito64/Malta-style config-space enumeration, byte/word/dword access, absent-device probes, and alignment error tests are relevant.
