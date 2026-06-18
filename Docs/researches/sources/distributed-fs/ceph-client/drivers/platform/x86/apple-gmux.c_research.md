# sources/distributed-fs/ceph-client/drivers/platform/x86/apple-gmux.c

## Purpose
`apple-gmux.c` drives Apple's gmux controller used on dual-GPU Macs. It provides gmux register access across classic PIO, indexed I/O, and T2-era MMIO variants; registers a platform backlight device when gmux owns panel brightness; integrates with `vga_switcheroo` for display/DDC muxing and discrete-GPU power control; handles ACPI notifications/GPEs; and exposes a debugfs port access interface.

## Important APIs, Types, and Functions
`struct apple_gmux_data` stores register resources, access config, backlight device, switcheroo state, ACPI/GPE data, completion state, and debugfs selection. `struct apple_gmux_config` selects read/write methods, switcheroo handler, resource type, version format, and gmux variant name. Accessors are grouped as `gmux_pio_*`, `gmux_index_*`, and `gmux_mmio_*`, with generic wrappers `gmux_read8()`, `gmux_write8()`, `gmux_read32()`, and `gmux_write32()`.

Backlight integration uses `gmux_get_brightness()`, `gmux_update_status()`, and `gmux_bl_ops`. Switcheroo integration uses `gmux_switchto()`, `gmux_switch_ddc()`, `gmux_set_power_state()`, and `gmux_get_client_id()`. Interrupt handling uses `gmux_notify_handler()`, `gmux_clear_interrupts()`, and GPE enable/disable logic. `gmux_probe()` and `gmux_remove()` own device lifetime.

## Control Flow
Probe is PNP-driven for `GMUX_ACPI_HID`. It rejects a second singleton instance, calls `apple_gmux_detect()` to identify the gmux type, allocates state, selects a config, requests and maps I/O or MMIO resources, reads the version, and optionally registers the `gmux_backlight` device depending on ACPI video backlight ownership. It obtains the ACPI handle, optionally reads `GMGP` and installs a notify handler plus GPE, determines whether the external port is fully switchable by scanning PCI Thunderbolt devices, sets the global `apple_gmux_data`, enables interrupts, reads initial switch state, registers the `vga_switcheroo` handler, and initializes debugfs.

Switch requests update cached display/DDC/external state then write gmux switch registers. Discrete power changes write the gmux power sequence and wait up to 200 ms for a power interrupt completion if a GPE is available. Suspend disables interrupts; resume reenables interrupts, rewrites switch state, and reapplies discrete-off state if needed.

## State and Persistence
The driver keeps a singleton global `apple_gmux_data` because the switcheroo callbacks do not carry per-device context. Runtime state includes selected mux owners, external switchability, discrete power state, selected debugfs port, and completion state. Hardware register values persist according to gmux/firmware behavior, but the driver rewrites cached switch and power state on resume. Backlight brightness is stored in gmux hardware and synchronized through the backlight core.

## Dependencies and Integration Points
The file integrates with PNP, ACPI video/backlight policy, `apple-gmux.h` detection and register constants, port/MMIO I/O APIs, PCI bus scanning, `vga_switcheroo`, debugfs, and ACPI GPE/notify handling. It directly affects GPU power rails and display routing.

## Risks and Test Signals
Risks are high because the driver controls display routing and discrete GPU power. Indexed/MMIO access relies on polling loops that return boolean readiness but callers do not surface timeout failures. The singleton global constrains multi-device assumptions. Debugfs permits raw gmux port writes and is intentionally powerful. T2 MMIO interrupt clearing requires ACPI `GMSP(0)` to avoid floods. Test signals include correct gmux type detection, resource request failures, backlight registration only when selected by ACPI policy, switcheroo registration and GPU classification, DDC switching on pre-retina configs, Thunderbolt external-port forcing, power-change completion timeout warnings, suspend/resume state restoration, and debugfs 1-byte/4-byte access validation.
