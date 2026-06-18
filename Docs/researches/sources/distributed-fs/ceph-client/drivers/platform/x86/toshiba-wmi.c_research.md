# sources/distributed-fs/ceph-client/drivers/platform/x86/toshiba-wmi.c

Purpose: Registers a small Toshiba WMI hotkey driver for WMI event GUID `59142400-C6A3-40FA-BADB-8A2652834100`. At this revision it mainly claims the event source, creates an input device, and logs unknown WMI events because concrete key event values are still TODO.

Important APIs and types: The global `toshiba_wmi_input_dev` stores the input device. `toshiba_wmi_keymap` is an empty sparse-keymap terminated by `KE_END`. `toshiba_wmi_notify` is the WMI event callback. `toshiba_wmi_dmi_table` restricts init to systems with DMI system vendor `TOSHIBA`. Setup and teardown are `toshiba_wmi_input_setup` and `toshiba_wmi_input_destroy`.

Control flow: Module init first requires both `wmi_has_guid(WMI_EVENT_GUID)` and a Toshiba DMI match. It allocates an input device named "Toshiba WMI hotkeys", sets BUS_HOST identity, initializes the sparse keymap, installs a WMI notify handler for the GUID, and registers the input device. The notify handler currently returns on null objects and logs object type at debug level otherwise. Exit removes the notify handler and unregisters the input device if the GUID is present.

State and persistence: No persistent hardware state is changed. Runtime state is limited to the global input-device pointer and the installed WMI notify handler. Because the keymap is empty, received events are not translated into input events.

Dependencies and integration points: Depends on the WMI core, ACPI object delivery, DMI matching, input, and sparse-keymap. It coordinates indirectly with `toshiba_acpi.c`, which detects the same WMI GUID and avoids monitoring ACPI hotkeys on machines where this WMI path exists.

Risks: The driver intentionally has incomplete event decoding, so loading it may suppress Toshiba ACPI hotkey monitoring without producing useful key events if users expect `toshiba_acpi.c` to handle them. Notify payload validation is minimal because event formats are unknown. Exit checks only `wmi_has_guid`; because init also checks DMI and setup success, this is normally fine, but teardown assumptions depend on init having completed.

Test signals: On a Toshiba machine with the GUID, module init logs "Toshiba WMI Hotkey Driver" and creates an input device. WMI notifications should call `toshiba_wmi_notify` and produce debug logs without crashes for null or unexpected ACPI objects. On non-Toshiba systems or systems without the GUID, init returns `-ENODEV`. Verify `toshiba_acpi.c` hotkey suppression behavior when the GUID is present.
