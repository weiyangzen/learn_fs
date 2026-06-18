# sources/distributed-fs/ceph-client/arch/mips/pci/ops-bcm63xx.c

## Purpose
Provides BCM63xx PCI, CardBus emulation, and PCIe config-space operations.

## Important APIs, Types, And Functions
Defines `bcm63xx_pci_ops`, optional `bcm63xx_cb_ops`, and `bcm63xx_pcie_ops`. Core helpers are `postprocess_read`, `preprocess_write`, `bcm63xx_setup_cfg_access`, `bcm63xx_do_cfg_read/write`, fake CardBus bridge read/write handlers, `bcm63xx_fixup`, and PCIe access gating functions.

## Control Flow
Legacy PCI config cycles program MPI L2 PCI config registers, access `pci_iospace_start`, then restore normal I/O behavior. CardBus support fakes a bridge at slot 0x1e, stores bridge config in software, remaps a single real CardBus device as type-0 access, and uses a fixup to assign the one hardware I/O window to PCI or CardBus. PCIe access only allows bridge slot 0 and endpoint slot 0 when link is up, with endpoint config offset adjustment.

## State And Persistence
Stores fake CardBus bridge config in static `fake_cb_bridge_regs`, bus tracking in `fake_cb_bridge_bus_number`, and one-time I/O window choice in `bcm63xx_fixup`. Hardware MPI/PCIe registers are programmed per access.

## Dependencies And Integration Points
Depends on `pci-bcm63xx.h`, BCM MPI/PCIe register helpers, CardBus config symbols, PCI fixup infrastructure, and shared `pci_iospace_start` from the BCM63xx controller setup.

## Risks And Edge Cases
The single I/O window means mixed PCI/CardBus I/O users are unsupported. Config write waits with fixed `udelay(500)`. Bus number handling for type 1 is noted as incomplete. Fake bridge state must match Linux PCI enumeration expectations.

## Test Signals
BCM63xx boot with PCI, CardBus, and PCIe devices; config-space byte/word/dword access tests; CardBus bridge enumeration; and link-down PCIe probes are the main signals.
