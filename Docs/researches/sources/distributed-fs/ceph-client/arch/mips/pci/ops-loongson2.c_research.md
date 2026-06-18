# sources/distributed-fs/ceph-client/arch/mips/pci/ops-loongson2.c

## Purpose
Implements Loongson2 PCI config-space operations and CS5536 MSR access helpers.

## Important APIs, Types, And Functions
Exports `loongson_pci_ops`, `_rdmsr`, and `_wrmsr` under `CONFIG_CS5536`. `loongson_pcibios_config_access` handles type 0/type 1 cycles and special CS5536 config reads/writes.

## Control Flow
On bus 0, CS5536 config registers below `PCI_MSR_CTRL` are handled by CS5536 helper functions to avoid recursive MSR access. Other accesses program Loongson PCI map registers, use CKSEG1 config windows, and detect master/target aborts. `_rdmsr/_wrmsr` serialize via `msr_lock` and perform PCI config cycles to the CS5536 MSR address/data registers.

## State And Persistence
No general persistent state except `msr_lock`. Hardware PCI map and command registers are touched per access.

## Dependencies And Integration Points
Depends on Loongson register macros, optional CS5536 headers, PCI core ops, raw spinlocks, and exported MSR helpers consumed by Loongson fixups.

## Risks And Edge Cases
CS5536 recursion avoidance is critical. Abort wrappers return `-1` in some failure paths. MSR helpers synthesize a local `pci_bus` and assume CS5536 bus/devfn constants are correct.

## Test Signals
Loongson2E/2F PCI enumeration, CS5536 peripheral fixups, MSR read/write tests, absent-device probes, and byte/word alignment checks are important.
