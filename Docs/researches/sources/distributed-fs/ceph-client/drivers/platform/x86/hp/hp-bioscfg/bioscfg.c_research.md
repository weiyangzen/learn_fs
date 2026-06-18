# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp-bioscfg/bioscfg.c

Purpose: main hp-bioscfg module core. It creates the firmware-attributes class device, enumerates BIOS WMI attribute instances, parses package or buffer encodings, creates per-attribute kobjects, and tears everything down.

Important APIs/types/functions: global `bioscfg_drv` owns all runtime state. Parsing helpers include `hp_get_integer_from_buffer()`, `hp_get_string_from_buffer()`, `hp_get_common_data_from_buffer()`, and `hp_convert_hexstr_to_str()`. `hp_init_bios_attributes()` enumerates WMI instances by GUID; `hp_init_bios_package_attribute()` and `hp_init_bios_buffer_attribute()` create kobjects and dispatch to type-specific populate functions. `hp_wmi_error_and_message()` maps firmware codes to Linux errors. `hp_set_reboot_and_signal_event()` sets `pending_reboot` and emits a uevent.

Control flow: module init checks required HP WMI GUIDs, registers the attribute-set WMI interface, creates `hp-bioscfg` under `firmware_attributes_class`, creates `attributes` and `authentication` ksets, creates `pending_reboot`, then enumerates string, integer, enumeration, ordered-list, and password WMI GUIDs. It also adds synthetic SPM and Sure Start objects. Exit calls type-specific cleanup, destroys ksets, unregisters the class device, and unregisters the WMI driver.

State and persistence: in-kernel state mirrors firmware data in allocated typed arrays and kobjects. BIOS setting changes are persistent only when WMI set operations succeed; `pending_reboot` is an in-memory signal for settings that require physical presence/reboot.

Dependencies and integration: integrates ACPI WMI with `firmware_attributes_class`, sysfs kobjects, typed attribute source files, password/SPM/Sure Start helpers, and NLS conversion.

Risks: malformed firmware data can desynchronize element positions, especially optional prerequisite/value lists. Some per-attribute failures are logged but enumeration continues, so partially populated sysfs trees are possible. Test signals include WMI GUID absence, package and buffer object formats, duplicate attribute names, maximum count clamping, cleanup idempotence, and uevent emission on reboot-required writes.
