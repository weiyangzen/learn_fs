# sources/distributed-fs/ceph-client/drivers/virtio/virtio_pci_modern_dev.c

## Purpose
`virtio_pci_modern_dev.c` is the exported low-level modern virtio PCI capability layer. It discovers virtio vendor capabilities, maps common/ISR/notify/device config regions, validates ABI offsets, configures DMA masks, and provides typed helpers for modern feature, status, queue, MSI-X, notification, and admin-queue registers.

## Important APIs, types, and functions
- `vp_modern_map_capability()` validates BAR, length, offset, alignment, range, and maps a capability window.
- `virtio_pci_find_capability()` scans vendor capabilities for a requested virtio cfg type and records BAR ownership.
- `check_offsets()` build-time checks public virtio PCI ABI offsets against kernel struct layouts.
- `vp_modern_probe()` validates device id, discovers mandatory common/ISR/notify capabilities, optional device config, requests selected BARs, and maps register windows.
- `vp_modern_remove()` unmaps windows and releases selected BARs.
- `vp_modern_get_extended_features()`, `vp_modern_get_driver_extended_features()`, and `vp_modern_set_extended_features()` read/write feature banks.
- Status/config helpers include `vp_modern_generation()`, `vp_modern_get_status()`, and `vp_modern_set_status()`.
- Queue helpers include queue reset, vector, address, enable, size, queue count, notification mapping, admin queue number, and admin queue index.

## Control flow
Probe first validates ABI offsets, derives the virtio id either from an optional device-id callback or PCI IDs, then searches vendor capabilities. Absence of common config returns `-ENODEV` so common code can fall back to legacy. Missing ISR or notify capabilities is fatal. It sets DMA masks, finds optional device config, requests all BARs used by modern capabilities, maps common config large enough for modern optional admin fields, maps the ISR, reads notify multiplier/length/offset, either maps the whole notify area when it fits in one page or records the capability for per-queue mapping, and maps up to one page of device config if present.

Feature helpers iterate 32-bit banks to fill or write the full virtio feature array. Queue helpers select a queue in common config before reading/writing queue fields. Queue reset writes `queue_reset`, then sleeps until both reset and enable clear. Notification mapping uses the queue's notify offset and multiplier, validating against a pre-mapped notify window or mapping the per-queue 2-byte notification area from the notify capability.

## State and persistence behavior
Persistent state is stored in `struct virtio_pci_modern_device`: PCI device pointer, virtio id, modern BAR bitmask, mapped common/ISR/notify/device pointers, lengths, notify offset multiplier, notify physical address, optional notify capability offset, and optional DMA mask/device-id callback inputs. Hardware retains feature/status/queue register writes until reset.

## Dependencies and integration points
It depends on Linux PCI capability scanning and BAR mapping, public `linux/virtio_pci_modern.h`, virtio PCI UAPI layouts, delay helpers, and low-level `vp_ioread*/vp_iowrite*` accessors. `virtio_pci_modern.c` consumes these helpers to implement the generic virtio transport.

## Risks and test signals
Risks include malformed capabilities, BAR changes between scan and map, integer wraparound in offset/length arithmetic, optional notify area mapping lifetime, PAGE_SIZE assumptions for device config, sleeping waits for broken queue reset, and ABI layout drift. Test signals include modern probe with valid/invalid capabilities, transitional fallback when common config is absent, bad BAR/offset/alignment rejection, full vs per-queue notify mapping, feature bank read/write, queue reset completion, admin queue index/num reads, remove cleanup after partial mapping failure, and device config absence using nodev ops.
