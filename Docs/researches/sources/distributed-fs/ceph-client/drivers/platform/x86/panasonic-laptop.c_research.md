# sources/distributed-fs/ceph-client/drivers/platform/x86/panasonic-laptop.c

Purpose: This ACPI platform driver supports Panasonic Let's Note hotkeys, vendor brightness control, optional optical-drive power control, mute/sticky-key/eco-mode settings, and related sysfs state on MAT0012/MAT0013/MAT0018/MAT0019 ACPI devices.

Important APIs, types, and functions: `struct pcc_acpi` stores the ACPI handle, SINF table, input device, backlight device, optical-drive platform device, and cached settings restored on resume. `acpi_pcc_write_sset()`, `acpi_pcc_get_sqty()`, and `acpi_pcc_retrieve_biosdata()` wrap the vendor `SSET`, `SQTY`, and `SINF` ACPI methods. Backlight integration uses `pcc_backlight_ops`; input uses `sparse_keymap` and `acpi_pcc_generate_keyinput()`. Sysfs attributes expose `numbatt`, `lcdtype`, `mute`, `sticky_key`, `eco_mode`, brightness registers, and `cdpower`.

Control flow: Probe reads `SQTY`, allocates an extra SINF slot for firmware off-by-one packages, initializes input, retrieves BIOS data, registers a vendor backlight only when ACPI video selects vendor backlight, resets sticky key mode, caches settings, creates sysfs attributes, installs ACPI notification handling, and optionally creates a separate `panasonic` platform device for optical drive power. Notifications query `HINF` and report sparse key events, suppressing brightness keys if ACPI video already handles them. Resume replays cached SSET values.

State and persistence: Firmware state is in ACPI methods and the SINF package. Software caches `sticky_key`, `eco_mode`, mute, AC/DC/current brightness for resume restoration. `sleep_keydown_seen` is a static workaround for firmware that sends missing sleep/hibernate key-down events. Optical-drive power is queried and set through global ACPI paths.

Dependencies and integration points: The driver integrates with ACPI companion devices, the input subsystem, i8042 serio filtering for duplicate volume keys, ACPI video backlight arbitration, backlight class, platform devices, and sysfs. Optional optical-drive support uses `\_SB.STAT`, `\_SB.FBAY`, `\_SB.CDDI`, and `\_SB.CDDR`.

Risks and edge cases: ACPI packages and SINF indices vary by model, so visibility checks gate only some attributes. Several store paths accept out-of-range values by silently doing nothing and still returning `count`. Optical-drive paths are hard-coded and one notifier path is model-specific. The i8042 filter is global and static state must not leak across unrelated devices. Probe has many manual unwind labels, so lifecycle regressions are likely if features are added.

Test signals: Validate hotkey event mapping, brightness keys with and without ACPI video handling, vendor backlight registration, sysfs visibility based on `num_sifr`, resume restoration, i8042 duplicate filtering for volume keys, and optical-drive power if ACPI methods exist. Firmware error tests should cover bad `SQTY`, malformed `SINF`, and notification events other than `0x80`.
