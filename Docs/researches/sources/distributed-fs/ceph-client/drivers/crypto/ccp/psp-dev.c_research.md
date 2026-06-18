# sources/distributed-fs/ceph-client/drivers/crypto/ccp/psp-dev.c

## Purpose

`psp-dev.c` is the central AMD Platform Security Processor subdevice driver. It initializes PSP capability state, mailbox access, interrupts, and optional subdevices for SEV, TEE, SFS, platform access, DBC, and HSTI.

## Important APIs, Types, And Functions

Global `psp_master` tracks the selected master PSP. Public functions include `psp_dev_init()`, `psp_dev_destroy()`, `psp_mailbox_command()`, `psp_extended_mailbox_cmd()`, `psp_set_sev_irq_handler()`, `psp_clear_sev_irq_handler()`, `psp_get_master_device()`, `psp_restore()`, `psp_pci_init()`, and `psp_pci_exit()`. `psp_irq_handler()` fans PSP interrupts to the registered SEV handler. `psp_get_capability()` reads and validates the feature register.

## Control Flow

`psp_dev_init()` allocates `struct psp_device`, attaches PSP vdata and MMIO registers, initializes the mailbox mutex, reads capability bits, disables/clears interrupts, requests the PSP IRQ, selects the master device through bus callbacks, initializes supported subdevices, and finally enables interrupts. Mailbox commands serialize on `psp->mailbox_mutex`, check ready state, write optional command-buffer addresses, trigger the command register, and poll for completion. Teardown destroys subdevices, frees the IRQ, and clears master state.

## State And Persistence Behavior

Per-device state lives in `sp->psp_data`. Capability bits are cached in `psp->capability`; subdevice pointers store owned feature modules. The master pointer is derived from `sp_get_psp_master_device()` and cached in `psp_pci_init()` for SEV PCI setup.

## Dependencies And Integration Points

It integrates with `sp-dev.c` for IRQ allocation and master selection, with `sev-dev.c`, `tee-dev.c`, `sfs.c`, `platform-access.c`, `dbc.c`, and `hsti.c` for subdevice lifecycles, and with PSP register offsets supplied by PCI/platform vdata.

## Risks And Test Signals

Risks include partially initialized subdevices on mid-probe failures, capability misreads on systems whose BIOS blocks register access, interrupt enable ordering, and shared mailbox races with consumers. Test by probing devices with different capability combinations, suspend/restore TEE ring reinit, subdevice init failures, IRQ delivery to SEV commands, and module unload/remove cleanup.
