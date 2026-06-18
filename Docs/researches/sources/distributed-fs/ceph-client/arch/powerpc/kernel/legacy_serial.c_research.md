
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/legacy_serial.c

Purpose: discovers Open Firmware-described legacy 8250-compatible serial ports very early on PowerPC, initializes an early firmware console when possible, and later registers platform `serial8250` ports with fixed-up IRQ and I/O resources.

Important APIs/types/functions: `legacy_serial_ports`; `legacy_serial_infos`; `find_legacy_serial_ports`; `add_legacy_port`; `add_legacy_soc_port`; `add_legacy_isa_port`; `add_legacy_pci_port`; `setup_legacy_serial_console`; `ioremap_legacy_serial_console`; `serial_dev_init`; `check_legacy_serial_console`; TSI-specific `tsi_serial_in/out`.

Control flow: early discovery checks `/chosen` stdout path, scans `ns16550` children under known SoC/simple-bus parents, ISA/LPC serial nodes, and PCI serial nodes. Each accepted node records clock, current speed, register shift, translated address, and provisional port data in an array of up to eight entries. If the firmware stdout matches a discovered node, the file maps or uses PIO for the port and initializes `udbg` for early console output. Later init remaps the early console to normal `ioremap`, resolves IRQs with `irq_of_parse_and_map`, adjusts PCI/PIO offsets, maps MMIO, applies Freescale IRQ workaround hooks when available, and registers the platform 8250 device.

State and persistence: static arrays preserve discovered device nodes and port metadata from early boot to device init. The only persistent effects are OF node references, early/normal mappings, preferred console selection, and registered platform devices.

Dependencies and integration: depends on device tree properties (`clock-frequency`, `current-speed`, `reg-shift`, `linux,stdout-path`, `stdout-path`), OF address/IRQ translation, PCI host bridges, `udbg`, `serial8250`, `fsl8250_handle_irq`, and early ioremap.

Risks: array slot replacement can reorder ports; early address translation is incomplete for some LPC/PIO cases; clock-frequency is mandatory for SoC/PCI early use; stale OF properties can choose the wrong default console; device-node references are retained for boot lifetime.

Test signals: boot boards with SoC, ISA/LPC, and PCI serial devices; verify early console before normal driver probe; check `ttyS` numbering and preferred console; confirm IRQ fixups and Freescale workaround activation in logs.
