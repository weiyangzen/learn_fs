<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-sparcio.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-sparcio.h

## Purpose
`i8042-sparcio.h` is the SPARC low-level backend for `i8042.c`. It discovers Open Firmware 8042 keyboard/mouse nodes, maps the keyboard register resource, obtains IRQs, and handles a special hardcoded JavaStation "MrCoffee" path.

## Important APIs, types, and functions
- Static globals `i8042_kbd_irq`, `i8042_aux_irq`, `kbd_iobase`, and `kbd_res` back generic register and IRQ macros.
- Inline accessors use `readb()`/`writeb()` at offsets `0x60` and `0x64`.
- `sparc_i8042_probe()` walks child OF nodes, recognizes keyboard names `kb_ps2`/`keyboard` and mouse names `kdmouse`/`mouse`, maps the keyboard resource with `of_ioremap()`, and records IRQs.
- `sparc_i8042_remove()` unmaps the keyboard resource.
- `i8042_is_mr_coffee()` detects the JavaStation-1 root node.
- `i8042_platform_init()` either uses hardcoded JavaStation register/IRQ values or registers the OF platform driver, validates discovered IRQs, sets reset policy, and returns readiness to generic i8042.

## Control flow
On PCI-capable SPARC builds, the generic i8042 init calls this platform init. JavaStation systems bypass OF child probing and map a fixed register range. Other systems register a small platform driver that probes OF `8042` nodes. If either keyboard or AUX IRQ is missing after probe, init unmaps any partial mapping and fails with `-ENODEV`. Platform exit unregisters the platform driver except on JavaStation.

## State and persistence
The header keeps mapped MMIO and IRQs in static globals for the lifetime of the generic driver. It does not persist settings. JavaStation mappings are not explicitly unmapped in the exit path.

## Dependencies and integration points
It depends on OF/platform-device APIs, SPARC prom/oplib headers, MMIO helpers, and generic i8042 globals. It bridges Open Firmware device nodes into the generic i8042 controller driver.

## Risks
- `of_find_device_by_node()` return values are assumed usable; malformed OF/platform-device state can lead to invalid resource or IRQ access.
- Partial discovery cleanup handles `kbd_iobase` but can be fragile if child resources are unusual.
- JavaStation hardcoded values are platform-specific and bypass normal resource management.
- Without `CONFIG_PCI`, platform init always returns `-ENODEV`.

## Test signals
- Build with SPARC `CONFIG_PCI` enabled and disabled.
- OF tests should cover keyboard/mouse child names, child IRQ fallback to parent IRQ, missing IRQs, mapping failure, and driver unregister cleanup.
- JavaStation tests should verify hardcoded IRQ/base operation and reset policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-sparcio.h -->
