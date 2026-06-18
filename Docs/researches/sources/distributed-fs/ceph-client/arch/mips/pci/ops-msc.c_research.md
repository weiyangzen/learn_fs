# sources/distributed-fs/ceph-client/arch/mips/pci/ops-msc.c

## Purpose
Implements MIPS MSC01 PCI config-space operations.

## Important APIs, Types, And Functions
Exports `msc_pci_ops`; `msc_pcibios_config_access` programs MSC01 config address/data and wrappers perform size extraction and read-modify-write.

## Control Flow
Before each access it clears master/target abort status, writes bus/device/function/register fields to `MSC01_PCI_CFGADDR`, performs read or write through `MSC01_PCI_CFGDATA`, reads interrupt status, and clears abort bits on error.

## State And Persistence
No persistent software state. Hardware config and status registers are updated per access.

## Dependencies And Integration Points
Depends on MSC01 PCI register macros and generic PCI ops.

## Risks And Edge Cases
Alignment checks exist in wrappers, but config-access failures return `-1` rather than canonical PCIBIOS error in some paths. Abort handling defines absent-device semantics.

## Test Signals
MSC platform config enumeration and absent-device probes should validate read/write behavior.
