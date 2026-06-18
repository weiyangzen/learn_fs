# sources/distributed-fs/ceph-client/arch/mips/pci/ops-gt64xxx_pci0.c

## Purpose
Implements GT64120/Galileo PCI0 config-space operations.

## Important APIs, Types, And Functions
Exports `gt64xxx_pci0_ops`; `gt64xxx_pci0_pcibios_config_access` performs the actual config cycle and wrappers handle byte/word/dword extraction and read-modify-write.

## Control Flow
The access helper rejects Galileo slot 31 on bus 0, clears master/target abort causes, writes config address with enable bit, accesses config data with special raw/nonraw handling for the host controller at bus 0 slot 0, then checks and clears aborts.

## State And Persistence
No persistent software state; hardware config address/data and interrupt cause registers are modified for each access.

## Dependencies And Integration Points
Depends on `asm/gt64120.h`, GT register access macros, and PCI core ops.

## Risks And Edge Cases
Host bridge slot 0 special handling and slot 31 hardware bug are easy to regress. Wrappers do not explicitly validate alignment. Abort detection controls absent-device behavior.

## Test Signals
GT64xxx board enumeration, absent slot probes, host bridge config access, and byte/word writes validate behavior.
