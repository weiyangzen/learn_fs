# sources/distributed-fs/ceph-client/arch/mips/pci/pci-alchemy.c

## Purpose
Implements Au1500/Au1550 Alchemy PCI host-mode controller support, including config-space access through a wired TLB entry, platform probing, IRQ delegation, and suspend/resume register save/restore.

## Important APIs, Types, And Functions
Defines `struct alchemy_pci_context`, `alchemy_pci_ops`, `alchemy_pci_probe`, `alchemy_pci_init`, `pcibios_map_irq`, and syscore suspend/resume hooks. Helpers include `mod_wired_entry`, `alchemy_pci_wired_entry`, `config_access`, and board IDSEL callback support.

## Control Flow
Probe validates platform data, claims and maps controller registers, enables the PCI clock, maps I/O space, handles old Au1500 noncoherent mode, installs board IRQ/IDSEL callbacks, allocates a VM area for config space, creates a wired TLB mapping, applies board config bit masks, registers syscore ops, and registers the PCI controller. Config access asserts board IDSEL, creates or reuses a wired TLB mapping for the target config page, reads/writes through the VM window, checks/clears PCI errors, and deasserts IDSEL.

## State And Persistence
Global `__alchemy_pci_ctx` stores the single controller for syscore operations. `alchemy_pci_context` caches last TLB entry values and saves twelve PCI controller registers across suspend. Hardware PCI config and TLB state persist until changed or reset.

## Dependencies And Integration Points
Depends on Alchemy platform data, clock framework, MIPS TLB helpers, PCI controller registration, DMA coherency state, syscore ops, and board-provided IRQ/IDSEL callbacks.

## Risks And Edge Cases
Wired TLB manipulation is fragile, especially across firmware resume paths that reset C0_wired. Config access runs with interrupts disabled and assumes board IDSEL callbacks are safe. Old Au1500 coherency workaround changes PCI config behavior. Only one controller is supported by the global context.

## Test Signals
Au1500/Au1550 boot, suspend/resume, PCI config scanning from atomic contexts, DMA coherency tests, and board-specific IRQ routing are needed signals.
