# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_driver.c

## Purpose
`jsm_driver.c` is the shared PCI and module lifecycle layer for the Digi JSM Neo and Classic multiport serial driver. It registers the UART driver, matches supported Digi PCI IDs, maps resources, selects Classic or Neo `board_ops`, initializes tty/UART ports, handles removal, and provides PCI error recovery callbacks.

## Important APIs, types, and functions
`jsm_uart_driver` is the shared serial-core driver with device name `ttyn`. `jsm_probe_one()` performs PCI enablement, region acquisition, board allocation, model classification, BAR mapping, IRQ request, tty initialization, and UART port initialization. `jsm_remove_one()` disables Classic interrupts, removes UART ports, frees IRQ/MMIO/channel queues, releases PCI regions, disables the device, and frees the board. `jsm_pci_tbl` lists supported IDs. PCI error handling is `jsm_io_error_detected()`, `jsm_io_slot_reset()`, and `jsm_io_resume()`.

## Control flow
Module init registers `jsm_uart_driver`, then the PCI driver. Probe enables the PCI device and regions, allocates `jsm_board`, assigns a board number, computes `maxports`, records revision/IRQ, and branches by device ID. Classic uses BAR4 memory plus BAR1 I/O control, selects `jsm_cls_ops`, UART spacing 8, and dividend 921600, then enables PLX local/PCI interrupts. Neo uses BAR0 memory, selects `jsm_neo_ops`, UART spacing 0x200, and the same dividend. Probe then requests the shared IRQ, initializes tty and UART ports, logs the board, stores drvdata, and saves PCI state.

## State and persistence behavior
One allocated `jsm_board` is owned per PCI device. State includes resources, remapped MMIO, selected ops, IRQ, channel pointers, and board numbering. `adapter_count` is static and monotonic; `jsm_debug` is a module parameter. PCI config state is saved/restored through PCI APIs.

## Dependencies and integration points
Dependencies include PCI core, serial core, IRQ handling, MMIO mapping, `jsm.h`, `jsm_tty.c`, and chip-specific `jsm_cls_ops`/`jsm_neo_ops`.

## Risks and test signals
Risks include a documented `jsm_tty_init()` resource leak if `jsm_uart_port_init()` fails, monotonic board numbering after failures/removes, Classic interrupt side effects, AER resume reinitialization, and wrong BAR/ops selection for a PCI ID. Test module load/unload, Classic/Neo probe/remove, all failure paths, AER callbacks, shared IRQ, dynamic major allocation, and debug logging.
