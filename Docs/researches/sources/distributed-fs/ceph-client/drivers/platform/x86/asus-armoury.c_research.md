# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-armoury.c

## Purpose
`asus-armoury.c` exposes ASUS Armoury-style BIOS/WMI settings through the firmware attributes class. It covers gaming-laptop controls that do not fit existing subsystems, including mini-LED modes, GPU MUX mode, dGPU/eGPU controls, APU memory reservation, charging and boot options, panel options, and ROG power tunables.

## Important APIs, Types, and Functions
`struct asus_armoury_priv` stores the firmware-attributes device/kset, eGPU mutex, AC/DC `struct rog_tunables`, and selected WMI device IDs for mini-LED and GPU MUX variants. `struct rog_tunables` stores current AC/DC values and a pointer to DMI-provided `struct power_limits`. The main WMI helpers are `armoury_has_devstate()`, `armoury_get_devstate()`, `armoury_set_devstate()`, `armoury_attr_uint_store()`, and `armoury_attr_uint_show()`. `asus_fw_attr_add()` creates the firmware-attributes device and conditionally creates per-feature sysfs groups. `init_rog_tunables()` matches the DMI power-limit table from `asus-armoury.h` and initializes AC/DC default values.

Feature-specific handlers include mini-LED mode mapping, `gpu_mux_mode_current_value_store()`, `dgpu_disable_current_value_store()`, `egpu_enable_current_value_store()`, APU memory show/store, and generated macro-based attributes for charge mode, boot sound, MCU powersave, panel overdrive, panel HD mode, automatic brightness, and ROG power tunables.

## Control Flow
Module init obtains the ASUS WMI ACPI device UID and rejects the legacy `ASUSWMI` DCTS path because this driver requires DSTS-style state access. It initializes DMI-based ROG tunables, then creates the firmware attributes device. Attribute creation always starts with top-level `pending_reboot`, detects which mini-LED and GPU MUX WMI IDs are present, creates their groups, then iterates `armoury_attr_groups`. A group is created only if its WMI device is present; power tunables are further gated by AC power-limit availability and non-zero max values.

Writes flow through `armoury_set_devstate()` either directly or via `armoury_attr_uint_store()`, which parses decimal input, enforces bounds, sends WMI, updates cached tunable state if requested, notifies sysfs, and signals pending reboot for BIOS settings such as GPU MUX and panel HD mode. eGPU/dGPU/MUX operations enforce sequencing under `egpu_mutex` and reject combinations known to break GPU state. eGPU enablement may trigger PCI bus rescan.

## State and Persistence
`fw_attrs.pending_reboot` is runtime kernel state exposed through sysfs and uevents; it is set when the driver knows BIOS changes need reboot but is not persistent across module reload. ROG tunable values are cached separately for AC and DC and selected dynamically by `power_supply_is_system_supplied()`. Actual settings are persisted, if at all, by ASUS firmware after WMI calls. The driver allocates AC/DC tunable structures at init and frees them at exit.

## Dependencies and Integration Points
The file depends on `asus-wmi` exported namespace, WMI management GUIDs and device IDs, the firmware attributes class, DMI power-limit data from `asus-armoury.h`, power-supply state, PCI rescanning, sysfs/kobject uevents, and ASUS platform data definitions. It shares the ASUS notebook WMI event GUID as its module alias but exposes configuration rather than hotkeys.

## Risks and Test Signals
Risk areas include firmware side effects, GPU state sequencing, DMI power-limit correctness, and generated sysfs contract drift. `armoury_set_devstate()` includes a safety block for known-dangerous APU memory values `0x100` and `0x101`. eGPU activation carefully checks connection, MUX state, return codes, and rescans PCI, but still depends on model-specific firmware behavior. The mini-LED show path reads WMI into `mode` but then uses `FIELD_GET(ASUS_MINI_LED_MODE_MASK, 0)`, which always extracts from zero and looks like a logic bug; tests should catch current-value reporting for nonzero modes. Test signals include group presence by WMI feature bit, each attribute's possible/default/min/max files, AC/DC tunable switching, pending reboot uevents, eGPU enable/disable result handling, dGPU disable rejection when MUX is in dGPU mode, and cleanup removing all conditionally created groups.
