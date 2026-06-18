# sources/distributed-fs/ceph-client/arch/mips/pci/ops-sni.c

## Purpose
Provides SNI PCIMT and PCIT PCI config-space operations.

## Important APIs, Types, And Functions
Exports `sni_pcimt_ops` and `sni_pcit_ops`. Helpers are `set_config_address`, `pcimt_read/write`, `pcit_set_config_address`, and `pcit_read/write`.

## Control Flow
PCIMT validates devfn/register, rejects bus-0 devfns beyond the decoded range, writes an ASIC config address, and uses port I/O for data. PCIT uses CF8/CFC-style type-1 addresses and, for bus 0 reads, performs a guarded write/probe sequence to avoid data bus errors before doing the requested access.

## State And Persistence
No persistent software state; direct ASIC or port I/O registers are programmed per access.

## Dependencies And Integration Points
Depends on SNI address constants and PCI core ops.

## Risks And Edge Cases
The bus-0 PCIT existence probe is invasive but protects against bus errors. Return values are sometimes raw zero instead of `PCIBIOS_SUCCESSFUL`, which is equivalent here but inconsistent. Device decode assumptions differ between PCIMT and PCIT.

## Test Signals
SNI RM200/RM300 hardware enumeration and absent-device reads are the only realistic signals.
