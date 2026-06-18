# subset-b-005452 Research

Grouped source research for Linux 8250 serial discovery drivers covering generic PCI serial boards, Microchip PCI1XXXX UARTs, shared PCI setup helpers, Pericom/ACCES PCI UARTs, legacy platform/ISA/ACPI registration, and PnP serial devices. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pci.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pci.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pci.c` is the generic PCI probe module for 8250/16550-compatible serial ports. It binds a large set of PCI serial, modem, and multiport adapter IDs, translates each device into a `pciserial_board` description, applies vendor-specific initialization/setup/exit quirks, and registers each discovered UART with the shared 8250 core. The source was read as a complete 6324-line file for this report; the long PCI ID table is data-heavy, while the key behavior is in the quirk table, board descriptor table, setup helpers, probe/remove/PM, and PCI error recovery paths.

## Important APIs, Types, and Functions

The central local types are `struct pci_serial_quirk`, which holds match keys plus optional `probe`, `init`, `setup`, and `exit` hooks, and `struct serial_private`, which stores the `pci_dev`, selected quirk, selected board descriptor, registered port count, and flexible array of 8250 line numbers. `struct f815xxa_data` stores per-port Fintek MMIO write serialization state.

Important exported APIs are `pciserial_init_ports()`, `pciserial_remove_ports()`, `pciserial_suspend_ports()`, and `pciserial_resume_ports()`, all exported in the `SERIAL_8250_PCI` namespace for sibling PCI 8250 modules. Core private helpers include `setup_port()`, `pci_default_setup()`, `find_quirk()`, `serial_pci_guess_board()`, `serial_pci_matches()`, `pciserial_init_one()`, `pciserial_remove_one()`, and the PCI error handler trio `serial8250_io_error_detected()`, `serial8250_io_slot_reset()`, and `serial8250_io_resume()`.

The file contains many hardware-specific setup/init hooks. Examples include PLX9050 interrupt enable/disable, SBS OctalPro reset/global interrupt control, SIIG clock normalization, Timedia board port-count probing, National Instruments MITE/8420/8430 interrupt and window setup, NetMos/ASIX port-count disambiguation, ITE887x IO-region discovery and config writes, Oxford/EndRun Tornado port counting and divisor programming, Quatech clock/RS422 probing, Fintek IO and MMIO setup including RS485 configuration, Intel KT Serial-over-LAN workarounds, WCH fixed-type setup, Sunix layout setup, MOXA interface-mode initialization, and Systembase interrupt masks. The large `pci_boards[]` table describes BAR selection, number of ports, base baud, UART spacing, register shift, and first offset. The large `serial_pci_tbl[]` maps PCI IDs and class-code fallbacks to `pci_boards[]` entries.

## Control Flow

Module registration installs `serial_pci_driver` through `module_pci_driver()`. On probe, `pciserial_init_one()` first finds the most specific quirk in `pci_serial_quirks[]` and runs its optional `probe` hook. It rejects invalid `driver_data`, checks the blacklist for devices that belong to other drivers such as parport, LPSS, Exar, or Pericom, enables the PCI device with managed enablement, and saves PCI state.

For explicit PCI ID matches, the selected board descriptor comes from `pci_boards[]`; for class-code fallback matches, `serial_pci_guess_board()` validates serial/modem class codes and derives BAR/port count from IO resources. For explicit entries, the same guesser is used diagnostically to warn about redundant table entries.

`pciserial_init_ports()` is the per-device registration engine. It runs the quirk `init` hook, which can fail or override the number of ports. It allocates `serial_private`, initializes a template `uart_8250_port`, chooses MSI/MSI-X or INTx interrupt vectors unless `FL_NOIRQ` is set, and iterates over ports. Each iteration calls the quirk `setup` function, which typically fills in BAR, offset, iotype, clock, type, private data, optional callbacks, and quirks, then calls `serial8250_register_8250_port()`. Registration stops at the first setup/register failure and records the successfully registered line count.

Removal unregisters each registered line and invokes the quirk `exit` hook, then frees the private object. Suspend unregisters runtime state through `serial8250_suspend_port()` and tears down quirk-programmed hardware through `exit`; resume re-runs `init` and calls `serial8250_resume_port()`. PCI AER/error recovery detaches ports on error detection, disables the device, restores PCI config after reset, and reinitializes ports on resume while preserving the selected board descriptor.

## State and Persistence Behavior

Persistent driver state is runtime-only. `serial_private` owns the registered line array and remembers the selected quirk/board for remove, suspend/resume, and PCI error recovery. Registered UART state is then owned by the 8250 serial core. Hardware programming persists only in PCI config space, UART registers, BAR-mapped bridge registers, and interrupt vector allocations until removal, suspend, reset, or driver unload. Several quirks must explicitly undo hardware writes: PLX/SBS/NI/WCH/Systembase interrupt enables, ITE IO-region reservation, and similar bridge controls.

The file also relies heavily on static tables as configuration state: `pci_serial_quirks[]`, `pci_boards[]`, `blacklist[]`, and `serial_pci_tbl[]`. These tables form an ABI-like binding contract for supported hardware. No file-backed persistence is used.

## Dependencies and Integration Points

The driver depends on the PCI core, PCI resource/BAR APIs, IRQ vector allocation, managed PCI enablement, PCI error recovery, IO port and MMIO accessors, the tty serial core, and the 8250 core. It calls the shared helper `serial8250_pci_setup_port()` from `8250_pcilib.c` and registers ports through `serial8250_register_8250_port()`. It uses `serial8250_suspend_port()`, `serial8250_resume_port()`, `serial8250_unregister_port()`, `serial8250_get_port()`, divisor/control callbacks, and several 8250-specific helpers for FIFOs and Oxford enhanced registers.

Integration with sibling drivers is explicit in the blacklist and namespace exports: Pericom/ACCES devices are delegated to `8250_pericom`, Exar/Commtech to the Exar driver, and some multi-IO serial/parallel devices to `parport_serial`. Class-code fallback allows otherwise unknown conventional serial/modem devices to bind if their resources fit expected 8250 layouts.

## Risks and Edge Cases

The highest risk is table accuracy. A wrong `driver_data`, BAR, offset, port count, register shift, or base baud can register invalid IO addresses, overlap a sibling function, or silently produce broken baud rates. Quirk matching order matters because the list terminates with a match-all default and specific entries must precede generic ones. Devices shared with other drivers require correct blacklist coverage to avoid double binding.

Hardware setup hooks perform low-level config-space, IO-port, and MMIO writes. Missing `CONFIG_HAS_IOPORT`, absent BARs, short resources, ambiguous NetMos configurations, or failed ioremaps are handled inconsistently across historical quirks. Suspend/resume and PCI error recovery depend on init/exit hooks being symmetric enough to reprogram hardware after device disable/reset. MSI selection is limited to a small allowlist, and sharing INTx is the default for most boards.

## Test Signals

Strong test signals include build coverage with and without `CONFIG_HAS_IOPORT`, probe/remove on representative single-port and multiport PCI cards, class-code fallback devices, blacklist handoff to parport/LPSS/Exar/Pericom drivers, MSI allowlist devices, suspend/resume with active ttys, PCI AER reset recovery, and repeated module load/unload for devices whose quirks toggle bridge interrupts. Device-specific validation should cover Fintek RS485 mode, Oxford Tornado baud accuracy, NetMos ambiguous subdevices, ITE IO-region reservation/release, MOXA interface initialization, and NI MITE interrupt/window programming. Runtime signals include correct `/dev/ttyS*` creation count, stable IRQ assignment, successful loopback at configured baud rates, no duplicate resource claims, and clean unregister paths under lockdep/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pci1xxxx.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pci1xxxx.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pci1xxxx.c` is a dedicated PCI driver for Microchip/Efar PCI1XXXX PCIe-to-UART devices. It handles up to four physical UART blocks, board variants with sparse logical port layouts, device revision differences, custom baud divisor programming, RS485 hardware control, burst-mode RX/TX for newer revisions, wake/D3 behavior, and multiple MSI vectors. The source was read as a complete 887-line file for this report.

## Important APIs, Types, and Functions

The central state type is `struct pci1xxxx_8250`, containing the number of logical ports, device revision, BAR0 MMIO base, and flexible array of registered 8250 line numbers. `logical_to_physical_port_idx` maps subsystem-device encodings to physical UART indexes for 1, 2, 3, and 4 port variants. `pci1xxxx_rs485_supported` declares supported RS485 flags and after-send delay capability.

Important functions include `pci1xxxx_get_num_ports()`, `pci1xxxx_get_max_port()`, `pci1xxxx_logical_to_physical_port_translate()`, `pci1xxxx_get_device_revision()`, `pci1xxxx_setup()`, `pci1xxxx_serial_probe()`, and `pci1xxxx_serial_remove()`. Hardware helpers include `pci1xxxx_acquire_sys_lock()` and `pci1xxxx_release_sys_lock()` for system-register access, custom divisor hooks `pci1xxxx_get_divisor()` and `pci1xxxx_set_divisor()`, `pci1xxxx_rs485_config()`, B0 RTS workaround `pci1xxxx_set_mctrl()`, C0 burst interrupt handler `pci1xxxx_handle_irq()`, and power-management helpers `pci1xxxx_port_suspend()`, `pci1xxxx_port_resume()`, `pci1xxxx_suspend()`, and `pci1xxxx_resume()`.

## Control Flow

Probe enables the PCI device, determines logical port count from the subsystem device, allocates `pci1xxxx_8250`, maps BAR0, reads the hardware revision under the device syslock, enables bus mastering, calculates the maximum physical port index needed for the variant, and allocates one or multiple interrupt vectors. If vectors match the physical-port requirement, the driver enables multiple-MSI routing in `UART_PCI_CTRL_REG`; otherwise all logical ports share vector 0.

For each logical port, probe translates logical to physical index, assigns the corresponding IRQ, calls `pci1xxxx_setup()`, and registers the configured `uart_8250_port`. Setup marks the port fixed and skip-test, uses `PORT_MCHP16550A`, assigns a synthetic 64 MHz UART clock for 4 Mbps calculations, installs custom divisor and RS485 callbacks, selects revision-specific callbacks, invokes `serial8250_pci_setup_port()` with BAR0 and `PORT_OFFSET * physical_index`, then marks the UART active and configures wake status/mask registers.

Interrupt flow for C0 and later revisions reads the burst status register. If an interrupt is pending, the handler locks the UART port, bulk-reads available RX bytes from the burst FIFO or byte FIFO into a temporary buffer, pushes them into the tty flip buffer, and bulk-writes TX data from the tty xmit kfifo into burst or byte FIFOs. Error bits update `icount` and overrun is cleared through the FIFO control register. Power management suspends each registered 8250 line, configures per-port wake state, disables D3 reset and optionally hot reset, enables D3 clocking when wake sources require it, and arms PCI D3 wake. Resume reverses reset-disable bits, marks each UART active, restores OUT2 when appropriate, and resumes the 8250 line.

## State and Persistence Behavior

Runtime state lives in `pci1xxxx_8250`, each registered 8250 line, tty fifos, UART hardware registers, and PCI IRQ vector allocation. Device revision affects persistent callback selection for the port lifetime: C0+ uses burst IRQ handling, B0 uses the RTS `set_mctrl` workaround. RS485 configuration persists in the ADCL config register and can rewrite the requested after-send delay to the hardware-achievable value. Suspend/resume deliberately leaves wake and reset-control register state programmed across low-power entry.

## Dependencies and Integration Points

The driver depends on PCI, MMIO accessors, `readx_poll_timeout()`, tty flip buffers, kfifo helpers, runtime UART/serial core structures, and the shared `serial8250_pci_setup_port()` helper from `8250_pcilib.c`. It registers lines through `serial8250_register_8250_port()` and uses `serial8250_suspend_port()`, `serial8250_resume_port()`, and `serial8250_get_port()` for PM. It imports the `SERIAL_8250_PCI` namespace.

## Risks and Edge Cases

Sparse subsystem-device port maps are risk-prone: wrong logical-to-physical translation gives wrong BAR offsets and IRQ vectors. Syslock acquisition can time out and prevents probe from reading revision. Multiple-MSI setup assumes vector count equals the maximum physical port count; fallback sharing must still work for all active logical ports. Burst RX uses a fixed 512-byte stack buffer and intentionally ignores counts that are zero or not less than the buffer size. TX accounting increments once per loop rather than per byte, so statistics are approximate. PM wake logic depends on wake-mask polarity and on checking `port->suspended` under the tty mutex.

## Test Signals

Validation should cover all supported device IDs and subsystem port layouts, one-vector and per-port MSI modes, B0 RTS toggling, C0 burst RX/TX, 4 Mbps and lower baud divisor programming, RS485 polarity and after-send delay clamping, suspend/resume with wake sources, D3 wake, remove after partial port-registration failure, syslock timeout injection, and tty loopback with parity/frame/overrun error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pci1xxxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.c` is the small shared PCI helper library for 8250 PCI serial drivers. It centralizes the common conversion from PCI BAR resources into `uart_8250_port` IO/MMIO fields and provides a common warning/error path for systems built without IO-port support. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

The exported functions are `serial_8250_warn_need_ioport()` and `serial8250_pci_setup_port()`, both exported with `EXPORT_SYMBOL_NS_GPL(..., "SERIAL_8250_PCI")`. `serial_8250_warn_need_ioport()` logs that a serial port is unsupported because IO resources are unavailable and returns `-ENXIO`. `serial8250_pci_setup_port()` fills `port->port.iotype`, `iobase`, `mapbase`, `membase`, and `regshift` from a selected PCI BAR, offset, and optional mapped MMIO base.

## Control Flow

`serial8250_pci_setup_port()` first rejects BAR indexes beyond `PCI_STD_NUM_BARS`. If the BAR is memory-backed, it marks the UART as `UPIO_MEM`, clears `iobase`, records the physical map base as `pci_resource_start() + offset`, sets `membase` to the caller-provided mapping plus offset, and preserves the requested register shift. If the BAR is not memory-backed and `CONFIG_HAS_IOPORT` is enabled, it marks the UART as `UPIO_PORT`, computes `iobase` from the BAR start plus offset, clears MMIO fields, and forces `regshift` to zero. If IO ports are unavailable, it delegates to `serial_8250_warn_need_ioport()`.

## State and Persistence Behavior

This file owns no long-lived state. Its only state mutation is caller-provided `uart_8250_port` initialization. MMIO mapping lifetime remains owned by the caller, which is why the function accepts `void __iomem *iomem` rather than mapping resources itself.

## Dependencies and Integration Points

It depends on PCI resource APIs, IORESOURCE flags, the 8250 internal `struct uart_8250_port` definition, and kernel module export namespaces. It is used by the generic PCI driver and dedicated PCI sibling drivers such as Microchip PCI1XXXX to keep BAR setup behavior consistent.

## Risks and Edge Cases

The helper assumes that memory BAR callers pass a valid mapping covering `offset`; it does not check resource length or null `iomem` before doing pointer arithmetic. IO BAR setup ignores the requested `regshift` by design, which is correct for standard port IO but wrong if a caller expected shifted port IO. A non-memory BAR on no-IO-port architectures fails with `-ENXIO`, so callers must propagate that rather than trying to register a partial port.

## Test Signals

Test signals include compile/link coverage of `SERIAL_8250_PCI` namespace users, probe of MMIO and port-IO PCI UARTs, no-IOPORT builds where IO BAR devices fail cleanly with the warning, invalid BAR index rejection, and successful tty registration using the fields populated by this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.h` is the declaration header for the shared 8250 PCI helper library. The source was read as a complete 17-line file for this report.

## Important APIs, Types, and Functions

The header forward declares `struct pci_dev` and `struct uart_8250_port`, then declares `serial8250_pci_setup_port()` and `serial_8250_warn_need_ioport()`. It intentionally exposes only the small helper API needed by PCI 8250 drivers.

## Control Flow

There is no executable control flow in this header. Including drivers call the implementation in `8250_pcilib.c` while preserving type opacity outside the include requirements.

## State and Persistence Behavior

No state is owned by the header. It contributes compile-time API declarations only.

## Dependencies and Integration Points

The header includes `<linux/types.h>` for fixed-width and `__iomem` related declarations. It is included by `8250_pci.c`, `8250_pci1xxxx.c`, and the library implementation.

## Risks and Edge Cases

Because it has no include guard, repeated inclusion depends on the declarations being harmless. The prototypes must stay synchronized with `8250_pcilib.c`; signature drift would break all namespace users at build time.

## Test Signals

Build coverage of all `SERIAL_8250_PCI` users is the main signal. Header include-order tests are implicit in compiling both generic and dedicated PCI drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pcilib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pericom.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pericom.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pericom.c` is a dedicated PCI driver for Pericom PI7C9X795 UARTs and many ACCES I/O products based on that family. These devices are blacklisted from the generic 8250 PCI driver so this driver can provide Pericom-specific port counting, register spacing, and baud divisor behavior. The source was read as a complete 214-line file for this report.

## Important APIs, Types, and Functions

The local state type is `struct pericom8250`, storing the BAR mapping pointer, number of registered ports, and flexible array of 8250 line numbers. `pericom_do_set_divisor()` is the key custom UART callback; it searches supported sample-clock ratios and writes divisor latch plus a sample-clock register to approximate the requested baud within a 2 percent tolerance. `pericom8250_probe()` and `pericom8250_remove()` implement device lifecycle. `pericom8250_pci_ids[]` lists Pericom and ACCES I/O PCI device IDs, and `pericom8250_pci_driver` registers the PCI driver.

## Control Flow

Probe enables the PCI device, estimates the maximum number of ports from BAR0 length divided by eight, computes requested port count from vendor/device encoding, allocates `pericom8250`, maps BAR0 with `pcim_iomap()`, and initializes a template `uart_8250_port`. The template uses port IO, a 14.7456 MHz effective clock (`921600 * 16`), skip-test/autoconf/share-IRQ flags, the PCI IRQ, and the custom divisor setter. It then iterates over ports while respecting the BAR-derived maximum. Pericom 7954-style quad devices use an offset jump for logical port 3 (`0x38` instead of `3 * 8`); others use eight-byte spacing. Each port is registered with `serial8250_register_8250_port()`. Remove unregisters every successfully registered line.

## State and Persistence Behavior

Runtime state is limited to the devm-managed `pericom8250` object, the managed BAR mapping, and registered 8250 line numbers. Divisor programming persists in UART registers until changed by termios, reset, or removal. The driver does not implement suspend/resume or explicit PCI error recovery; it relies on PCI core and 8250 core behavior available for simple devices.

## Dependencies and Integration Points

The driver depends on PCI probe/remove, managed resource allocation, BAR mapping, 8250 internals, `serial8250_register_8250_port()`, `serial8250_unregister_port()`, and divisor latch helpers. It integrates with the generic PCI driver through the generic driver's blacklist entries for Pericom and ACCES I/O vendors.

## Risks and Edge Cases

Port count decoding is compact but hardware-specific: Pericom uses low device-id bits, while ACCES I/O derives count from bits 5:3. Bad IDs or unexpected encodings can produce the wrong `nr`. The divisor search silently returns without programming if no ratio is within tolerance, leaving prior UART settings intact. The driver uses `pdev->irq` directly rather than allocating vectors, so interrupt setup depends on PCI core defaults. Quad offset handling is special-cased by port count and index, which must match the hardware layout.

## Test Signals

Validation should include Pericom 1/2/4/8-port devices, ACCES I/O 2/4/8-port products, the quad port-3 offset jump, baud accuracy across common and high rates, remove after partial registration, BAR length limiting, and confirmation that the generic 8250 PCI driver does not bind the same IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pericom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_platform.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_platform.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_platform.c` is the universal and legacy platform driver for 8250/16550 serial ports. It initializes built-in ISA-compatible ports, registers the global 8250 UART driver, starts PnP probing, creates the legacy `serial8250` platform device, handles platform-data and ACPI-described UARTs, and tears everything down at module exit. The source was read as a complete 386-line file for this report.

## Important APIs, Types, and Functions

Global configuration includes module parameter `share_irqs`, exported runtime limit `nr_uarts`, `old_serial_port[]` from `SERIAL_PORT_DFNS`, exported configurator pointer `serial8250_isa_config`, and global platform device pointer `serial8250_isa_devs`. `serial8250_set_isa_configurator()` lets platform code install ISA port customization. `serial8250_isa_init_ports()` wraps `__serial8250_isa_init_ports()` with `DO_ONCE()`.

Probe helpers are `serial8250_probe_acpi()` and `serial8250_probe_platform()`. Lifecycle functions are `serial8250_probe()`, `serial8250_remove()`, `serial8250_suspend()`, `serial8250_resume()`, module init `serial8250_init()`, and module exit `serial8250_exit()`. `serial8250_isa_driver` binds platform devices named `serial8250` and ACPI ID `RSCV0003`.

## Control Flow

At module init, the driver rejects `nr_uarts == 0`, initializes ISA port slots once, logs configured port count and IRQ sharing state, registers the global `serial8250_reg` UART driver or SPARC minors, initializes PnP support through `serial8250_pnp_init()`, allocates/adds a legacy `serial8250` platform device, pre-registers ISA ports through `serial8250_register_ports()`, then registers the platform driver. Failure unwinds in reverse order.

ISA initialization clamps `nr_uarts` to `UART_NR`, calls `serial8250_setup_port()` for runtime slots, chains RSA-capable port ops, and copies architecture-provided `old_serial_port[]` data into each early `uart_8250_port`. Optional IRQ sharing sets `IRQF_SHARED`, and the installed ISA configurator may mutate each port and capability set.

Platform probe with platform data iterates a `plat_serial8250_port` array until a zero flags sentinel, copies all port parameters and optional callbacks into a temporary `uart_8250_port`, applies shared IRQ flags, and registers each port. ACPI probe allocates a single UART, reads a memory or IO resource, sets defaults for a 16550A at 1.8432 MHz, validates firmware properties through `uart_read_and_validate_port_properties()`, tolerates no-IRQ polling, and registers the port. Remove, suspend, and resume scan the global 8250 line array and act only on ports whose `port.dev` matches the platform device.

## State and Persistence Behavior

The driver owns process-wide 8250 registration state: global UART driver registration, legacy platform device lifetime, ISA port templates, PnP driver lifetime, and the runtime `nr_uarts` limit. Individual port state moves into the 8250 core after registration. Module parameters persist for the module lifetime. `serial8250_isa_devs` is set to NULL before unregistering on exit so `serial8250_unregister_port()` does not recreate legacy ISA ports during teardown.

## Dependencies and Integration Points

Dependencies include platform bus, ACPI, PnP entry points from `8250_pnp.c`, architecture `asm/serial.h`, the serial core `uart_register_driver()`/`uart_unregister_driver()`, SPARC sunserial integration, and 8250 core helpers. The platform-data path integrates with board files or devices that create `plat_serial8250_port` arrays; the ACPI path currently matches RISC-V generic 16550A UARTs.

## Risks and Edge Cases

The platform-data loop relies on a nonzero `flags` sentinel; malformed platform data can skip or overrun expected entries. Remove/suspend/resume scan global UART slots, so correct `port.dev` association is essential. ACPI probe only handles one resource and supports ACPI-based standard discovery, not a general DT path in this file. IRQ sharing is module-wide and unsafe for edge-triggered interrupts, as documented. Init ordering must keep PnP and platform device cleanup symmetric on failure.

## Test Signals

Test signals include boot with legacy ISA ports, `nr_uarts` clamping, `share_irqs` parameter behavior, platform-data registration with multiple ports and custom callbacks, ACPI `RSCV0003` probing with IO and MMIO resources, no-IRQ polling fallback, suspend/resume of platform-owned ports only, module init unwind injection, and module unload without ISA port re-registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pnp.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pnp.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pnp.c` probes ISA Plug and Play 8250/16550 serial ports, legacy PnP modems, touchscreens/tablets that expose serial-compatible resources, and special consumer-IR resources that should be reserved away from the legacy serial driver. It is initialized and exited by the platform driver rather than through an independent module entry point. The source was read as a complete 537-line file for this report.

## Important APIs, Types, and Functions

The large `pnp_dev_table[]` maps many PnP IDs to driver flags. `UNKNOWN_DEV` marks generic unknown modem patterns that require heuristic validation, and `CIR_PORT` marks IR resources that should be tracked but not exposed as regular serial ports. `modem_names[]`, `check_name()`, `check_resources()`, and `serial_pnp_guess_board()` implement unknown-modem heuristics. Main lifecycle functions are `serial_pnp_probe()`, `serial_pnp_remove()`, `serial_pnp_suspend()`, `serial_pnp_resume()`, `serial8250_pnp_init()`, and `serial8250_pnp_exit()`.

## Control Flow

`serial8250_pnp_init()` registers `serial_pnp_driver` with the PnP core. On match, `serial_pnp_probe()` checks whether `UNKNOWN_DEV` requires heuristic confirmation: the device or card name must contain a modem-like substring, and possible IO configurations must include a conventional COM base (`0x2f8`, `0x3f8`, `0x2e8`, or `0x3e8`) with eight bytes.

Probe then builds a temporary `uart_8250_port`. For CIR devices with a valid third port resource, it uses PnP port index 2; otherwise it prefers PnP IO resource 0, then memory resource 0 with `UPF_IOREMAP`. It sets a 1.8432 MHz UART clock, assigns the PnP device, sets skip-test/autoconf flags, reads firmware port properties with `uart_read_port_properties()`, and accepts `-ENXIO` as polling mode. CIR devices are marked fixed port/fixed type as `PORT_8250_CIR`. The port is registered with `serial8250_register_8250_port()`, but if registration fails or the device was CIR, probe returns `-ENODEV`; this keeps CIR resources from becoming regular tty serial ports. For normal ports, the 8250 line number is stored as PnP driver data and console capability is set if the registered port is the active UART console.

Remove clears `PNP_CONSOLE` and unregisters the stored 8250 line. Suspend/resume call `serial8250_suspend_port()` and `serial8250_resume_port()` for that line. `serial8250_pnp_exit()` unregisters the PnP driver.

## State and Persistence Behavior

The PnP ID table and modem-name table are static match state. Runtime state per device is just the stored 8250 line number in PnP driver data plus the optional `PNP_CONSOLE` capability bit. Registered UART state is owned by the 8250 core. No file-backed persistence is used.

## Dependencies and Integration Points

The file depends on the PnP core, device property parsing, serial core, and 8250 registration/suspend/resume helpers. It is called from `8250_platform.c` during global 8250 driver initialization. It coordinates with legacy probing by reserving CIR resources and setting console capability for PnP devices backing the console.

## Risks and Edge Cases

The unknown-modem heuristic is intentionally rough and can miss valid modems or accept non-modems with matching names/resources. CIR probe returns `-ENODEV` after registering a fixed CIR-flavored 8250 port, which is subtle and relies on the intended resource-reservation behavior; changes here risk either exposing IR ports as tty devices or allowing the legacy serial driver to bind them. Storing a line number through a `void *` cast is historical and assumes line values fit safely. Probe accepts polling if no IRQ is provided, which can hide firmware resource omissions until runtime performance suffers.

## Test Signals

Validation should cover known PNP0500/PNP0501 COM ports, known modem IDs, unknown PNPCXXX/PNPDXXX modem heuristics, memory-backed PnP resources, no-IRQ polling fallback, console capability marking and clearing, CIR IDs `WEC1022` and `SMCF010`, suspend/resume of registered PnP lines, and interaction with the platform driver's init/exit ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pnp.c -->
