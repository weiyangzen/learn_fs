# sources/distributed-fs/ceph-client/drivers/firmware/dmi_scan.c

Purpose: discovers SMBIOS/DMI tables early in boot, extracts stable system identity fields, exposes raw DMI data under `/sys/firmware/dmi/tables`, and provides exported match/query helpers used by quirks, drivers, and RAS code.

Important APIs/types/functions: exported symbols include `dmi_kobj`, `dmi_available`, `dmi_string_nosave()`, `dmi_check_system()`, `dmi_first_match()`, `dmi_get_system_info()`, `dmi_name_in_vendors()`, `dmi_find_device()`, `dmi_get_date()`, `dmi_get_bios_year()`, `dmi_walk()`, `dmi_match()`, and memory-device helpers `dmi_memdev_name()`, `dmi_memdev_size()`, `dmi_memdev_type()`, and `dmi_memdev_handle()`. Internal parsing is centered on `dmi_decode_table()`, `dmi_present()`, `dmi_smbios3_present()`, `dmi_scan_machine()`, and `dmi_decode()`.

Control flow: `dmi_setup()` calls `dmi_scan_machine()` before many arch/driver init consumers need DMI data. The scanner prefers EFI SMBIOS3, falls back to EFI legacy SMBIOS, then optionally scans the legacy physical window. Valid entry points set `dmi_base`, `dmi_len`, `dmi_num`, and `dmi_ver`, then walk the table with `dmi_decode()` to save BIOS, system, board, chassis, OEM string, onboard device, slot, IPMI, and extended device data. `dmi_memdev_walk()` makes a second pass for type-17 memory-device records. Later, `subsys_initcall(dmi_init)` creates sysfs binary files for the entry point and table.

State and persistence behavior: DMI identity strings, device lists, table base/length, SMBIOS entry-point bytes, and memory-device arrays are retained in kernel memory after early parsing. Raw table sysfs data is backed by a remapped DMI table and persists while the firmware sysfs tree exists; there is no dynamic rescan.

Dependencies and integration points: depends on architecture DMI remap helpers, EFI config-table addresses, memblock/DMI allocators, sysfs firmware kobjects, random seeding via `add_device_randomness()`, and `include/linux/dmi.h` match structures. CPER memory-error reporting uses the memory-device lookup helpers.

Risks and test signals: firmware tables are untrusted, so length checks, checksums, short-entry detection, end-of-table handling, and bounds-limited string walking are critical. Watch for malformed SMBIOS versions, bad physical addresses, and duplicate/empty device strings. Test signals include boot logs reporting SMBIOS version and identity, populated `/sys/firmware/dmi/tables/{smbios_entry_point,DMI}`, successful DMI quirk matches, and memory-error DIMM location decoding using type-17 handles.
