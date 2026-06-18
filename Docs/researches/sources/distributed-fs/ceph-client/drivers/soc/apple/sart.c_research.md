# sources/distributed-fs/ceph-client/drivers/soc/apple/sart.c

## Purpose
This driver manages Apple SART DMA address filters. It lets client drivers add or remove physical memory ranges that coprocessors may access when a full IOMMU is not used.

## Important APIs, Types, And Functions
`struct apple_sart_ops` abstracts SART v0, v2, and v3 register encodings. `struct apple_sart` stores device, MMIO, ops, protected entries, and used entries. Exports are `devm_apple_sart_get()`, `apple_sart_add_allowed_region()`, and `apple_sart_remove_allowed_region()`. Version-specific helpers get/set entries.

## Control Flow
Probe maps registers, selects ops from DT match data, scans all 16 entries, and marks bootloader-populated entries as protected. Clients get the provider through the `apple,sart` phandle. Adding a region skips protected and used entries, atomically claims a free bit, validates alignment/size, writes allow flags/address/size, and returns. Removing scans non-protected entries for exact address and size, clears the hardware entry, and clears the used bit. Shutdown clears all non-protected entries.

## State, Persistence, And Dependencies
Persistent hardware state exists in SART registers; software mirrors protected and used entries in bitmaps. Dependencies include platform MMIO, OF phandles, device links, bit operations, and public SART header definitions.

## Integration Points
Apple NVMe and other coprocessor clients use SART to permit DMA buffers. Bootloader entries remain protected to avoid breaking firmware-reserved mappings.

## Risks
`sart_set_entry()` shifts `paddr` by `size_shift` and `size` by `paddr_shift`; current values match, but the naming is error-prone if future variants differ. There is no mutex around used-entry scanning beyond atomic bit operations; duplicate exact mappings are possible if clients request the same region. Device link return is not checked. Exact match is required for removal.

## Test Signals
Probe all SART compatibles, preserve bootloader entries, add aligned and reject unaligned regions, exhaust 16 entries, remove exact regions, ensure protected entries survive shutdown, and validate client DMA succeeds only with allowed ranges.
