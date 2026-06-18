# sources/distributed-fs/ceph-client/arch/mips/pci/ops-mace.c

## Purpose
Implements SGI IP32 MACE PCI config-space operations.

## Important APIs, Types, And Functions
Exports `mace_pci_ops`; helper `mkaddr` builds config addresses, and read/write callbacks access `mace->pci.config_data` byte/word/long views.

## Control Flow
Reads temporarily disable master-abort interrupts, program config address, read the requested size with big-endian byte/word lane adjustment, acknowledge possible master abort, restore control, and fake the ultra bit for onboard SCSI devices. Writes program the config address and size-specific data lane.

## State And Persistence
No software persistence. MACE control/error registers are modified around reads.

## Dependencies And Integration Points
Depends on IP32 MACE register definitions and PCI ops used by `pci-ip32.c`.

## Risks And Edge Cases
Suppressing master-abort interrupts around reads must be balanced. The SCSI ultra-bit fakery is device/devfn-specific. No explicit invalid-device rejection is present here.

## Test Signals
SGI O2 PCI enumeration, onboard SCSI behavior, and config access to absent slots are the core signals.
