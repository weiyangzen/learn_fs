<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-acpipnpio.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-acpipnpio.h

## Purpose
`i8042-acpipnpio.h` is the x86/IA64/LoongArch ACPI/PNP low-level platform layer included by `i8042.h`. It supplies I/O port accessors, default IRQ/register values, large DMI quirk handling, optional PNP resource discovery, firmware IDs, and platform init/exit hooks for the generic `i8042.c` controller driver.

## Important APIs, types, and functions
- It defines the physical path strings, `I8042_KBD_IRQ`, `I8042_AUX_IRQ`, `I8042_COMMAND_REG`, `I8042_STATUS_REG`, and `I8042_DATA_REG` used by `i8042.c`.
- Inline accessors `i8042_read_data()`, `i8042_read_status()`, `i8042_write_data()`, and `i8042_write_command()` wrap `inb()`/`outb()`.
- X86 quirk bits `SERIO_QUIRK_*` mirror i8042 module parameters such as `nokbd`, `noaux`, `nomux`, `unlock`, `probe_defer`, reset policy, direct mode, dumb keyboard, no loop, no timeout, keyboard reset, Dritek, no PNP, and no restore.
- `i8042_dmi_quirk_table[]` is a first-match DMI table for system-specific i8042 behavior overrides.
- `i8042_pnp_kbd_probe()` and `i8042_pnp_aux_probe()` collect PNP port, IRQ, name, firmware ID, and keyboard fwnode information.
- `i8042_pnp_init()` registers synchronous PNP keyboard/AUX drivers, validates or falls back to default resources, handles laptop AUX IRQ-test bypass, and updates the global register/IRQ variables.
- `i8042_check_quirks()` applies the matched DMI quirk to `i8042.c` globals.
- `i8042_platform_init()` sets defaults, checks platform absence, applies quirks, invokes PNP detection, and sends x86 A20/null commands for firmware compatibility.

## Control flow
When the generic driver calls `i8042_platform_init()`, this header first rejects platforms known not to have an i8042. It assigns default ISA IRQs, applies IA64 reset policy, processes DMI quirks, logs the active quirk set, then attempts PNP detection unless disabled. PNP probes run synchronously and may provide alternate I/O ports, IRQs, firmware names, and fwnodes.

If PNP finds no devices, the code either returns `-ENODEV` on platforms that require firmware enumeration or falls back to direct probing when legacy i8042 is expected. If PNP resources are malformed, it warns and substitutes defaults. On x86 it also sets `i8042_bypass_aux_irq_test` for laptop DMI matches when PNP data looks reliable. Platform exit unregisters PNP drivers.

## State and persistence
This header mutates global driver configuration variables before `i8042.c` creates the platform device. It persists no state outside the running kernel. PNP driver registration state and discovered device counts are kept in static booleans/counters until platform exit.

## Dependencies and integration points
It depends on ACPI, PNP, DMI, architecture IRQ mapping, x86 legacy platform flags, I/O port access, and globals declared in `i8042.c` before including `i8042.h`. It supplies firmware IDs and the keyboard fwnode used later when the serio ports are created.

## Risks
- The DMI quirk table is order-dependent; a broad vendor entry before a specific model entry can change behavior for many machines.
- PNP resource validation intentionally falls back to defaults for common firmware bugs, which can mask real resource conflicts.
- `i8042_bypass_aux_irq_test` trusts PNP and laptop DMI data, so bad firmware can cause false AUX presence.
- The header writes `i8042_*` globals defined in the including C file, making include order and configuration guards important.
- x86 A20 and null-command firmware workarounds touch legacy controller state even before full probe.

## Test signals
- Build with combinations of `CONFIG_X86`, `CONFIG_IA64`, `CONFIG_LOONGARCH`, and `CONFIG_PNP`.
- DMI tests should confirm first-match quirk behavior and module-parameter override of default reset policy.
- PNP tests should cover no devices, keyboard-only, AUX-only, invalid ports, missing IRQs, laptop AUX IRQ-test bypass, firmware ID propagation, and fwnode assignment.
- Boot tests should verify direct-probe fallback only occurs on platforms where legacy i8042 is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-acpipnpio.h -->
