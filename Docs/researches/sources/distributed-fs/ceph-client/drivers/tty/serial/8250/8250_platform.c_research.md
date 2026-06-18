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
