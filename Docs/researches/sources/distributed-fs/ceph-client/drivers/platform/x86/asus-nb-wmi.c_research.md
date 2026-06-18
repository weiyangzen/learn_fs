# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-nb-wmi.c

## Purpose
`asus-nb-wmi.c` is the ASUS notebook WMI hotkey driver. It supplies DMI-specific quirks, a large WMI event keymap, optional i8042 filtering, and key filtering for the shared ASUS WMI core driver.

## Important APIs, Types, and Functions
The file defines module parameters `wapf` and `tablet_mode_sw`, global quirk pointer `quirks`, and `atkbd_reports_vol_keys`. `asus_i8042_filter()` observes PS/2 keyboard scancodes to detect volume keys already reported by atkbd and optionally filters E1 extended codes on affected models. `asus_nb_wmi_quirks()` selects the default or DMI-specific `struct quirk_entry`, applies module parameter overrides, and attaches quirks to the shared `struct asus_wmi_driver`.

The DMI table maps many ASUS models to quirk structures controlling WAPF, WMI backlight behavior, display-toggle suppression, USB charging register, forced ALS writes, tablet switch mode, ignored fan, WLAN event remapping, and Armoury-key behavior. `asus_nb_wmi_keymap[]` maps WMI event codes to Linux input keys or ignores known duplicate/status events. `asus_nb_wmi_key_filter()` suppresses brightness events handled by ACPI video, suppresses duplicate volume keys when atkbd reports them, and rewrites WLAN console events according to quirks.

## Control Flow
Module init calls `asus_wmi_register_driver()` with `asus_nb_wmi_driver`. The shared ASUS WMI core calls `detect_quirks`, sets up the keymap and input device, and dispatches events through the key filter. DMI matching uses `dmi_check_system()` and `dmi_matched()` to update the global `quirks` pointer. The i8042 filter is available to the shared driver to watch raw keyboard traffic; when it sees E0 volume scancodes, later WMI volume events are ignored.

## State and Persistence
State is module-global and runtime-only: selected `quirks`, effective `wapf`, optional tablet switch override, and `atkbd_reports_vol_keys`. No user settings are persisted by this file. DMI quirks are static compiled data.

## Dependencies and Integration Points
The implementation depends on the shared ASUS WMI core (`asus-wmi.h`), sparse keymap semantics, DMI, i8042 filtering, ACPI video brightness-key ownership, and the ASUS notebook WMI event GUID. It is primarily an adapter that configures and constrains shared WMI behavior for notebook models.

## Risks and Test Signals
Risk is concentrated in quirk correctness and duplicate input suppression. Incorrect DMI matches can change WAPF radio behavior, tablet mode detection, or event remapping. The i8042 filter uses static state for E0/E1 prefix tracking and must avoid consuming unrelated keyboard data; it ignores AUX data explicitly. Tests should cover representative DMI quirk selection, module parameter overrides, brightness-key suppression when ACPI video handles keys, volume duplicate suppression after observed atkbd scancodes, WLAN event remapping for Zenbook Duo and ROG Z13 quirks, tablet mode override behavior, and clean unregister through `asus_wmi_unregister_driver()`.
