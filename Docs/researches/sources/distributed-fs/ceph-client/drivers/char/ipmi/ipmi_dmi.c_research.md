# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_dmi.c

Purpose: SMBIOS/DMI IPMI decoder that creates platform devices for IPMI interfaces and supplies slave-address lookup for ACPI-described SI devices.

Important APIs, types, and functions: `struct ipmi_dmi_info`, `dmi_decode_ipmi()`, `dmi_add_platform_ipmi()`, `ipmi_dmi_get_slave_addr()`, and `scan_for_dmi_ipmi()`.

Control flow: subsys init scans DMI devices of type IPMI, decodes interface type, base address, address space, register spacing, IRQ, and slave address. It builds `struct ipmi_plat_data`, records a lookup entry, and calls `ipmi_platform_add()` for SI or SSIF platform devices. SSIF decoding has special handling for broken systems that store I2C address in the slave-address field.

State and persistence: global linked list of decoded DMI interface info and an init-only counter for platform instance numbering. Entries persist for later ACPI slave-address lookup.

Dependencies and integration: DMI subsystem, platform-device IPMI helpers, `ipmi_plat_data.h`, `ipmi_dmi.h`, and SI type definitions.

Risks and test signals: no freeing path is needed for init-time data but malformed DMI can create wrong devices. Tests should cover old/new DMI lengths, KCS/SMIC/BT/SSIF type decoding, I/O vs memory address bits, invalid offset/type, zero base address, broken SSIF address fallback, and ACPI lookup matches.
