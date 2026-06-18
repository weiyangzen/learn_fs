# sources/distributed-fs/ceph-client/drivers/platform/x86/xiaomi-wmi.c

Purpose: WMI input driver for Xiaomi laptop hotkey notification GUIDs. It converts firmware WMI events into Linux input key press/release sequences.

Important APIs/types/functions: `struct xiaomi_wmi` stores one input device, a mutex protecting key event sequences, and the key code for the bound GUID. `XIAOMI_DEVICE()` associates GUID strings with key codes in `xiaomi_wmi_id_table`. `xiaomi_wmi_probe()` allocates/registers the input device, and `xiaomi_wmi_notify()` reports a press and release. The active GUIDs map Fn to `KEY_PROG1` and Fn+F7 to `KEY_CUT`; other known GUID mappings are present but commented out.

Control flow: WMI core matches each GUID and passes the table context to probe. Probe rejects missing context, allocates state, initializes the mutex and input device, sets EV_KEY capability for the configured key, and registers the device. On notification, the driver locks, emits key down/sync and key up/sync, then unlocks.

State and persistence: state is per-WMI-device and in memory only. The mutex serializes event emission so overlapping WMI notifications do not interleave key sequences. There is no persistent configuration.

Dependencies/integration: depends on WMI bus, devm-managed input allocation, Linux input key codes, module WMI driver registration, and firmware exposing one of the GUIDs. `no_singleton = true` allows multiple GUID-backed WMI devices.

Risks: the payload is ignored and `min_event_size` is zero, so any notification on a matched GUID produces a key event. Commented GUIDs indicate some keys may be intentionally disabled to avoid duplicate or incorrect input reports. Synthetic press/release cannot represent key hold duration.

Test signals: WMI event injection or real hotkey use should create exactly one input event pair for each active GUID, multiple matched GUIDs should register independently, and disabled GUIDs should not produce events unless explicitly re-enabled and validated against duplicate firmware paths.
