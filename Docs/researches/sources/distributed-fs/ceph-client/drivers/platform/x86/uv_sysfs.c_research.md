# sources/distributed-fs/ceph-client/drivers/platform/x86/uv_sysfs.c

Purpose: builds `/sys/firmware/sgi_uv` topology for HPE SGI UV systems. It exposes partition/coherency/type attributes, hub objects, hub ports, and PCI bus topology derived from UV BIOS calls; hubless systems receive a smaller base group.

Important APIs and control flow: init first rejects non-UV systems, creates `sgi_uv`, and branches to hubless or full setup. Full setup creates base attributes, installs the UV BIOS heap, enumerates hub objects (`uv_bios_enum_objs`), ports (`uv_bios_enum_ports`), and PCI topology text (`uv_bios_get_pci_topology`). Custom kobject types expose hub attributes (`name`, `location`, `this_partition`, `shared`, `nasid`, `cnode`), port connection attributes, and parsed PCI topology attributes (`type`, `location`, `iio_stack`, `ppb_addr`, `slot`).

State and persistence: globals hold ksets, BIOS buffers, kobject arrays, object-to-cnode cache, BIOS heap, counts, and master NASID for the module lifetime. Data is generated at init and released in reverse order on exit.

Dependencies and integration: depends on UV architecture helpers and BIOS interfaces from `asm/uv/*`, kobject/sysfs APIs, and firmware kobject hierarchy. PCI topology parsing mutates BIOS text lines to construct kobject names.

Risks and test signals: unwind paths are complex and must avoid leaks or double puts. Firmware text parsing is format-sensitive, and object ID/count assumptions must stay within allocated arrays. Tests should boot full UV and hubless UV configurations, inspect sysfs tree shape and attribute values, inject BIOS errors for each setup stage if possible, and run module unload/reload with leak and kobject warnings enabled.
