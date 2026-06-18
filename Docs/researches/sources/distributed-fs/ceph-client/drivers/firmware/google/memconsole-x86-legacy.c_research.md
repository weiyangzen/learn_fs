# sources/distributed-fs/ceph-client/drivers/firmware/google/memconsole-x86-legacy.c

Purpose: Locates legacy Google BIOS memory console descriptors in the x86 EBDA and exposes the associated log through `/sys/firmware/log`.

Important APIs/types/functions: `biosmemcon_ebda` models v1 and v2 EBDA descriptors. `memconsole_ebda_init()` scans EBDA byte-by-byte for v1/v2 signatures. `found_v1_header()` and `found_v2_header()` compute base address and length, then call `memconsole_setup()`. `memconsole_x86_init()` gates discovery on Google DMI matches.

Control flow: Module init checks DMI board vendor, gets EBDA physical address, reads EBDA length, scans for magic signatures, configures a read callback over the discovered physical buffer, and creates the shared sysfs file. Exit removes the sysfs file.

State and persistence behavior: Global `memconsole_baseaddr` and `memconsole_length` track the discovered BIOS log buffer. The driver reads firmware-owned memory and does not persist changes.

Dependencies and integration points: Uses x86 EBDA helpers, DMI, ACPI includes, physical-to-virtual mapping for low memory, and the shared memconsole layer.

Risks and test signals: EBDA scanning trusts the EBDA length and descriptor fields; malformed firmware can point to invalid memory. Test on legacy Google systems with v1 and v2 descriptors, absent EBDA, absent signature, and offset reads from `/sys/firmware/log`.
