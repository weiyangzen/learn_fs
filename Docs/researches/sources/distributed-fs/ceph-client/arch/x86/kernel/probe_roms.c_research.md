# sources/distributed-fs/ceph-client/arch/x86/kernel/probe_roms.c

## Purpose
Discovers and reserves legacy BIOS, video, extension, and adapter option ROM memory regions, and provides PCI helpers to map a discovered BIOS option ROM that matches a device.

## APIs, Types, And Functions
Key resources are `system_rom_resource`, `extension_rom_resource`, `adapter_rom_resources[]`, and `video_rom_resource`. Exported APIs are `pci_map_biosrom()`, `pci_unmap_biosrom()`, and `pci_biosrom_size()`. Helpers include `match_id()`, `probe_list()`, `find_oprom()`, `romsignature()`, `romchecksum()`, and `probe_roms()`.

## Control Flow
`probe_roms()` scans the video ROM window in 2 KiB increments, validates the `0xaa55` signature and checksum-derived length, then requests the video ROM resource. It always requests the system ROM range, optionally requests the extension ROM if signature and checksum match, and scans adapter ROMs below the next reserved upper boundary. PCI mapping helpers search the recorded adapter resources, parse PCI data structures in ROM images using fault-tolerant reads, match vendor/device IDs or device lists, and map the resource with `ioremap()`.

## State And Persistence
Discovered ROMs persist as busy, read-only iomem resources. Mapping calls create transient ioremap mappings owned by callers until `pci_unmap_biosrom()`.

## Dependencies And Integration
Depends on ISA bus virtual mapping, `iomem_resource`, PCI driver/device IDs, fault-safe kernel reads, E820/setup memory reservations, and `setup.c` calling `x86_init.resources.probe_roms()`.

## Risks And Test Signals
Legacy ROM memory may contain malformed data, so fault-safe reads and checksum checks are important. Bad resource bounds could reserve usable memory or expose the wrong ROM to PCI drivers. Test signals include `/proc/iomem` ROM resources, PCI ROM consumers successfully mapping expected images, and booting systems with old VGA/option ROM layouts.
