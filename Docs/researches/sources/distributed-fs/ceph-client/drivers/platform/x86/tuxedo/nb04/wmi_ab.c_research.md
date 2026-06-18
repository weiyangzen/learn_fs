# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/wmi_ab.c

Purpose: WMI-backed virtual HID LampArray driver for tested TUXEDO NB04 notebooks. It registers on WMI GUID `80C9BAA6-AC48-4538-9234-9F81A55E7C85`, creates a virtual HID device named `TUXEDO NB04 RGB Lighting`, and translates HID Lighting and Illumination feature reports into NB04 WMI keyboard-backlight commands.

Important APIs and types: `tux_report_descriptor` describes LampArray feature reports. `struct tux_kbl_map_entry_t` maps HID lamp IDs to keyboard usage codes and physical positions for Sirius 16 ANSI/ISO layouts. `struct tux_hdev_driver_data_t` stores lamp count, selected key map, next attribute response lamp, and a pending `TUX_KBL_SET_MULTIPLE_KEYS` WMI input buffer. The HID low-level driver implements `.start`, `.parse`, and `.raw_request`; WMI probe/remove allocate and destroy the virtual HID device.

Control flow: module init first DMI-gates to Sirius 16 Gen1/Gen2 board names, then registers the WMI driver. HID start calls `tux_wmi_xx_8in_80out(TUX_GET_DEVICE_STATUS)` to choose ANSI or ISO layout. GET_REPORT returns array attributes and per-lamp attributes. SET_REPORT handles attribute requests, multi updates, range updates, and a no-op array-control report. Multi/range updates accumulate key RGB values in the 496-byte WMI input and flush only when `LAMP_UPDATE_COMPLETE` is set.

State and dependencies: state is per HID device and device-managed, with WMI output not persisted by the driver. Integration spans WMI, HID core, DMI matching, and the helper ABI in `wmi_util.h`.

Risks and test signals: lamp ID bounds, duplicate detection, and deferred flush behavior are critical. The multi-update check uses `rep->lamp_id[i] > driver_data->lamp_count`, so `lamp_id == lamp_count` should be tested because valid indices end at `lamp_count - 1`. Tests should cover ANSI/ISO detection, HID descriptor parsing, GET/SET feature report sizes, range splitting into batches of eight, intensity scaling, WMI failure propagation, remove-time HID destruction, and DMI refusal on untested machines.
