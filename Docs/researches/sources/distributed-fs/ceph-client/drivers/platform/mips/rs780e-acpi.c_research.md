# sources/distributed-fs/ceph-client/drivers/platform/mips/rs780e-acpi.c

Purpose: RS780E southbridge ACPI I/O setup for Loongson systems. The driver programs PM index/data ports and ACPI I/O decode registers so SCI, GPE, and power-management blocks are available at the platform-provided I/O resource.

Important APIs, types, and functions: `pmio_write_index()` and `pmio_read_index()` implement indexed PM register access through `PM_INDEX/PM_DATA`; `pm2_iowrite()` and `pm2_ioread()` target the second index pair. `acpi_registers_setup()` writes PM status/control/GPE base registers, enables ACPI decode and SCI generation, configures GPM3/GPM9, and pull-downs. `acpi_hw_clear_status()` clears wake/power button and GPE status. `rs780e_acpi_probe()` requests the I/O resource and invokes setup. The driver is a builtin platform driver matched by `loongson,rs780e-acpi`.

Control flow: platform probe obtains `IORESOURCE_IO`, reserves it with `request_region()`, stores `acpi_iobase`, programs the southbridge, and clears pending hardware status. There is no remove path; setup is expected to be permanent for the booted system.

State and persistence: `acpi_iobase` is static and all meaningful state is in the chipset registers. No Linux-managed persistent data structure is retained after probe except the reserved I/O region.

Dependencies and integration points: uses x86-style I/O port access (`inb/outb/inw/outw/inl/outl`) on a MIPS platform, platform-device resources, and OF compatible matching. It integrates with ACPI/SCI electrical behavior rather than registering a Linux ACPI core object itself.

Risks: hard-coded PM register indices and bit positions make this tightly bound to RS780E wiring. `request_region()` has no matching release because there is no remove path. SCI/GPE configuration can break wake or power-button behavior if the I/O resource or GPM wiring is wrong. The code assumes 16-bit ACPI base programming is sufficient.

Test signals: boot with a `loongson,rs780e-acpi` platform device and verify I/O region reservation, SCI delivery, power-button status clearing, and GPE events. Use register tracing or hardware diagnostics to confirm PM index writes and GPM pull-down configuration.
