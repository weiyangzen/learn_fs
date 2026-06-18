## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-aio.c

Purpose: provides legacy WMI hotkey support for Dell all-in-one systems exposing either `EVENT_GUID1` or `EVENT_GUID2`. It maps volume, mute, brightness, display-toggle, and video-switch scancodes into Linux input events.

Important APIs, types, and functions: `struct dell_wmi_event` describes the newer buffer event format with length, type, and event array. `dell_wmi_aio_keymap` is a sparse-keymap table. `dell_wmi_aio_event_check()` validates buffer events with type `0` or `0xf` and at least one payload word. `dell_wmi_aio_notify()` accepts either integer ACPI objects, new-format buffers, or broken one-byte buffers and reports scancodes through `sparse_keymap_report_event()`. `dell_wmi_aio_find()` selects the first known GUID present.

Control flow: module init searches for a GUID, allocates/registers one global input device, and installs a WMI notify handler. Notify dispatch decodes the ACPI object and emits a sparse-keymap event if a scancode is found. Exit removes the handler for the currently present GUID and unregisters the input device.

State and persistence: only a global `input_dev` pointer is retained. Firmware state is not modified; the driver only translates notifications. There is no per-device private data and no suspend/resume state.

Dependencies and integration: integrates with the old `wmi_install_notify_handler()` API rather than `struct wmi_driver`, input core, and sparse-keymap. It is separate from `dell-wmi-base` and targets all-in-one GUIDs.

Risks: global state and GUID rediscovery on exit assume the same GUID remains available. The buffer fallback for broken firmware treats the first byte as a scancode, which is intentionally permissive but can report spurious keys from malformed data. Test signals include module load on systems with each GUID, integer and buffer event decoding, unknown scancode behavior through sparse-keymap, and clean handler removal.
