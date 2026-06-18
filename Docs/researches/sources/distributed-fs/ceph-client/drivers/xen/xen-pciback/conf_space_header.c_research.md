# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/conf_space_header.c

## Purpose
`conf_space_header.c` defines pciback overlays for the standard PCI configuration header. It makes identity, command, interrupt, BAR, ROM, and selected header fields safe for a guest driver domain.

## Important APIs, types, and functions
The public entry point is `xen_pcibk_config_header_add_fields`. Internal types `struct pci_cmd_info` and `struct pci_bar_info` cache command and BAR state. Key callbacks are `command_init/read/write`, `bar_init/read/write/reset/release`, `rom_write`, vendor/device/interrupt readers, and `bist_write`. Field arrays `header_common`, `header_0`, and `header_1` describe common, normal-device, and bridge overlays.

## Control flow
Header initialization adds common fields, then adds BAR/ROM fields based on PCI header type. Command writes translate selected guest bits into `pci_enable_device`, `pci_disable_device`, bus-master changes, MWI changes, and optional INTx control; direct config writes happen only in permissive mode and only for guest-controlled bits. BAR writes allow sizing probes and restoration of cached values, while reads return either cached BAR value or length value depending on the last sizing write. Unsupported header types fail initialization.

## State and persistence
Per-field callback data caches original command and BAR/ROM values. Hardware state may change when enabling/disabling devices, bus mastering, MWI, INTx, BIST, cache line size, or restored BAR values. The overlay state is per-device runtime memory.

## Dependencies and integration points
It depends on Linux PCI core helpers, pciback policy flags, and the config-space field abstraction. It integrates with pciback config initialization to prevent guest drivers from moving host resources while preserving expected PCI probing semantics.

## Risks and test signals
Risks include BAR sizing emulation errors, 64-bit BAR high-half handling, command-bit masking, permissive writes to unsafe fields, interrupt control policy, device enable/disable side effects, and bridge header differences. Test signals include guest BAR probing, 64-bit memory BARs, ROM BAR reads/writes, command register toggles, bus-master enable/disable, INTx disable control, BIST writes, bridge passthrough, and reset/free of field data.
