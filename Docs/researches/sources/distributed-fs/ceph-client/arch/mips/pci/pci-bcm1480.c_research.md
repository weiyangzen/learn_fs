# sources/distributed-fs/ceph-client/arch/mips/pci/pci-bcm1480.c

## Purpose
Implements Broadcom BCM1480/BCM1x55 native PCI-X host-controller glue.

## Important APIs, Types, And Functions
Defines `bcm1480_pci_ops`, `bcm1480_controller`, `pcibios_map_irq`, `pcibios_plat_dev_init`, and `bcm1480_pcibios_init`.

## Control Flow
Init sets probe-only mode, adjusts global I/O and memory limits, maps 16 MiB config space, detects host versus device mode from system config and bridge command bits, enables ExpMemEn, maps PCI I/O space, sets I/O port base, registers the PCI controller, and optionally takes over VGA console. Config access checks bus mode, reads/writes the mapped config window, and handles byte/word/dword extraction.

## State And Persistence
Global `cfg_space` and `bcm1480_bus_status` persist after init. Hardware config space, I/O mapping, and controller command bits are programmed for the boot lifetime.

## Dependencies And Integration Points
Depends on SiByte BCM1480 register definitions, CFE firmware resource assignment, MIPS I/O mapping, generic PCI controller registration, and optional VGA console support.

## Risks And Edge Cases
Assumes firmware assigned resources (`PCI_PROBE_ONLY`). The 16 MiB config mapping is large. Device mode hides bus 0. Writes to disallowed devices return bad-register rather than not-found. Global resource limit changes affect the whole PCI subsystem.

## Test Signals
BCM1480 host-mode boot with CFE-initialized PCI, device-mode boot, config scanning, I/O mapping, and VGA console takeover are signals.
