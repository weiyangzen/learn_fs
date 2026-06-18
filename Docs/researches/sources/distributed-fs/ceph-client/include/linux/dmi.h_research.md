# sources/distributed-fs/ceph-client/include/linux/dmi.h

## Purpose
This header exposes Desktop Management Interface and SMBIOS table discovery helpers. It lets drivers match systems, read firmware strings, enumerate DMI devices, walk raw DMI entries, and query memory-device metadata.

## Important APIs, types, and functions
Important types are `enum dmi_device_type`, `enum dmi_entry_type`, `struct dmi_header`, `struct dmi_device`, `struct dmi_a_info_entry`, `struct dmi_a_info`, and `struct dmi_dev_onboard` under `CONFIG_DMI`. APIs include `dmi_check_system()`, `dmi_first_match()`, `dmi_get_system_info()`, `dmi_find_device()`, `dmi_setup()`, `dmi_get_date()`, `dmi_get_bios_year()`, `dmi_name_in_vendors()`, `dmi_name_in_serial()`, `dmi_walk()`, `dmi_match()`, `dmi_memdev_name()`, `dmi_memdev_size()`, `dmi_memdev_type()`, `dmi_memdev_handle()`, and `dmi_string_nosave()`.

## Control flow, state, and persistence
The persistent state is populated from firmware tables during setup and exposed through `dmi_kobj`, global availability state, and internal DMI device lists. `dmi_walk()` provides callback-driven table traversal. `dmi_string_nosave()` returns transient strings from a DMI record rather than saved copies.

## Dependencies and integration points
It depends on list handling, kobjects, and `mod_devicetable.h` for system ID fields. It is integrated with platform quirks, firmware drivers, memory inventory, and onboard-device discovery. Without `CONFIG_DMI`, most helpers become conservative stubs.

## Risks and test signals
Risks are malformed firmware tables, missing DMI support, lifetime confusion around non-saved strings, and quirk matching that is too broad. Tests should include positive and negative `dmi_system_id` matches, date parsing, raw table walking, memory-device queries, and disabled-config fallback values.
