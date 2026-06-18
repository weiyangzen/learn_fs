# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_input.c

- Purpose: Registers an rc-core infrared input device and forwards UART-decoded scancodes to it.
- Important APIs/types/functions: `mantis_input_init()`, `mantis_input_exit()`, and `mantis_input_process()`.
- Control flow: Init allocates an `rc_dev`, fills PCI input IDs, device names, rc map, parent device, and registers it. UART work calls `mantis_input_process()` to emit `rc_keydown()`. Exit unregisters/frees the rc device.
- State and persistence: Stores `rc`, `device_name`, `input_phys`, and rc map pointer in `struct mantis_pci`; no persistence.
- Dependencies and integration points: Integrates with Linux rc-core and `mantis_uart.c`; rc-map names come from PCI ID driver data.
- Risks: `mantis_input_exit()` calls both `rc_unregister_device()` and `rc_free_device()`; depending on rc-core ownership this can be fragile. Unknown protocol is used for all scancodes.
- Test signals: Test rc device creation, key events from UART, empty-map boards, and unload after registration failure or no rc map.
