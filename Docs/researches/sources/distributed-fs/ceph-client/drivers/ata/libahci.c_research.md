# sources/distributed-fs/ceph-client/drivers/ata/libahci.c

## Purpose
`libahci.c` is the common AHCI SATA engine used by PCI, platform, and other AHCI host drivers. It owns AHCI capability normalization, controller reset/init, port DMA/FIS setup, command preparation and issue, interrupt handling, libata error recovery integration, power management, port multiplier/FBS support, enclosure-management LED support, and host activation.

## Important APIs, Types, And Functions
The primary exported operation table is `ahci_ops`, with `ahci_pmp_retry_srst_ops` as a soft-reset workaround variant. Exported helpers include `ahci_save_initial_config()`, `ahci_reset_controller()`, `ahci_init_controller()`, `ahci_dev_classify()`, `ahci_fill_cmd_slot()`, `ahci_kick_engine()`, `ahci_do_softreset()`, `ahci_check_ready()`, `ahci_do_hardreset()`, `ahci_qc_issue()`, `ahci_error_handler()`, `ahci_port_resume()`, `ahci_print_info()`, `ahci_set_em_messages()`, and `ahci_host_activate()`. The file exports sysfs attribute groups `ahci_shost_groups` and `ahci_sdev_groups`.

Key state is carried in `struct ahci_host_priv`, `struct ahci_port_priv`, `struct ahci_em_priv`, libata `ata_port`, `ata_link`, and `ata_queued_cmd`. Module parameters include `skip_host_reset`, `ignore_sss`, `ahci_em_messages`, and `devslp_idle_timeout`.

## Control Flow
Host setup starts with a caller-populated `ahci_host_priv`. `ahci_save_initial_config()` enables AHCI mode, reads CAP/CAP2/version/ports-implemented, applies platform/quirk overrides, fabricates legacy port maps when needed, saves per-port command capability bits, and installs default `start_engine`, `stop_engine`, and IRQ handler callbacks. `ahci_reset_controller()` performs a global reset unless skipped, reenables AHCI mode, and restores saved hardware-init fields when allowed. `ahci_init_controller()` deinitializes each real port, clears pending SError/IRQ state, and enables global host interrupts.

Port startup allocates coherent DMA memory for command slots, received FIS area, and command tables; detects FBS capability; optionally switches to per-port locks for multi-MSI; then resumes the port. Resume powers up/spins up the link, starts FIS reception, starts the DMA engine unless delayed, restores enclosure-management LEDs, initializes software activity timers, and attaches/detaches PMP/FBS state according to current topology.

For command execution, `ahci_qc_prep()` converts ATA taskfiles into command FISes, copies ATAPI CDBs, fills AHCI scatter/gather entries, and writes command slot options. `ahci_qc_issue()` records the active link, marks NCQ commands in `PORT_SCR_ACT`, selects the FBS PMP device when needed, writes `PORT_CMD_ISSUE`, and updates software activity. Completion reads `PORT_SCR_ACT` and/or `PORT_CMD_ISSUE` depending on FBS and NCQ state, then calls libata multi-completion and fills result taskfiles from D2H, PIO setup, or SDB FIS areas.

Reset and error handling paths stop/kick engines, issue software-reset FIS pairs with deadline handling, perform SATA hardreset after clearing D2H receive state, classify devices from `PORT_SIG`, set ATAPI command bits after reset, clear SError, map AHCI IRQ bits into libata error masks/actions, handle hotplug/PHY changes, abort/freeze ports, and delegate recovery to `sata_pmp_error_handler()`. Host IRQ handling supports both shared single-level interrupts and one-MSI-per-port mode.

## State And Persistence
`hpriv` stores normalized capabilities, saved hardware-init register values, port map, MMIO base, IRQ vectors, EM buffer metadata, and quirk flags. `pp` stores DMA pointers, interrupt mask, active link, FBS state, optional IRQ descriptions, and per-port EM state. Hardware state is in AHCI global registers, per-port command/interrupt/SCR/FBS/DEVSLP registers, DMA command lists, received FIS buffers, and EM buffers. Sysfs writes can persist runtime LED/activity choices in `ahci_em_priv` until port teardown.

## Dependencies And Integration Points
The file is the bridge between libata core and AHCI MMIO hardware. It depends on DMA mapping, runtime PM, SCSI host attributes, PCI/platform callers, SATA PMP helpers, libata EH, ACPI storage D3 checks, timer APIs, and AHCI register definitions from `ahci.h`. `libahci_platform.c` and PCI AHCI drivers call its exported reset/init/activate/resource-independent routines.

## Risks And Edge Cases
Many operations depend on strict ordering: engines must stop before CLO/DEVSLP/FBS changes, FIS RX must be programmed before command issue, HOST_IRQ_STAT must be cleared after port status, and SError must be cleared to avoid lockups. Hardware quirks can force 32-bit DMA, disable NCQ/PMP/SNTF/DEVSLP/FBS/SXS, or change ALPM behavior. Hot-unplug can make registers read `0xffffffff`. FBS changes result-FIS ownership and PMP error routing. Sysfs EM buffer access must reject busy or unsupported states. DEVSLP programming stops the engine and may fail device feature commands. Global host reset can be skipped by parameter, which avoids broken firmware but leaves stale state possible.

## Test Signals
Useful tests include AHCI capability normalization for quirk flags and firmware-supplied port maps, reset timeout/failure paths, DMA mask selection, port start/stop leaks, NCQ and non-NCQ completion, ATAPI CDB paths, PMP with and without FBS, BAD_PMP retry softreset, hotplug/PHYRDY interrupts, SNotification fallback, multi-MSI interrupt registration, runtime/system suspend with SSS and DEVSLP, EM LED and SGPIO sysfs operations, and EH recovery from TF, host-bus, interface, unknown-FIS, and command-timeout errors.
