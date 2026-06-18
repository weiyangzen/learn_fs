# sources/distributed-fs/ceph-client/drivers/platform/x86/redmi-wmi.c

Purpose: This WMI driver handles Xiaomi Redmibook keyboard events identified by GUID `46C93E13-EE9B-4262-8488-563BCA757FEF`. It maps vendor WMI payloads to Linux input keys and ignores firmware events that other components handle.

Important APIs, types, and functions: `redmi_wmi_keymap` maps 32-bit scancodes to input keycodes or ignores. `struct redmi_wmi` stores an input device and a mutex protecting key-event sequences. `redmi_wmi_probe()` allocates state and registers the input device. `redmi_wmi_notify()` validates WMI buffer events, decodes the first little-endian u32 payload, looks up the sparse keymap entry, and reports it.

Control flow: The WMI core binds the driver by GUID and minimum event size. Probe sets up `Redmibook WMI keys`. Notify rejects non-buffer or too-short events, decodes payload, ignores unknown events at debug level, applies the AI-key press/release quirk, and reports the event under `key_lock`.

State and persistence: State is per-WMI-device and devm-managed. There is no persistent hardware state; all behavior is event translation. AI key value state is derived from `AI_KEY_VALUE_MASK`.

Dependencies and integration points: Dependencies include WMI, ACPI object buffers, input sparse-keymap, mutexes, and Linux input-event codes. `no_singleton = true` permits multiple matching WMI devices.

Risks and edge cases: Payload matching relies on exact 32-bit values and a hard-coded minimum length of 32 bytes. Unknown events are debug-only and can be missed during field validation. AI key behavior disables autorelease, so incorrect payload bit handling can leave the key logically stuck.

Test signals: Feed known payloads for screenshot, app launcher, config, video mode, refresh toggle, vendor key, Fn keys, ignored keyboard-backlight/power/Fn-lock events, and both AI key positions. Validate bad ACPI object types and short buffers are rejected.
