# sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/slic.h

## Purpose
`slic.h` is the private hardware and state header for the Alacritech SLIC non-accelerated Gigabit Ethernet driver. It defines register offsets, interrupt/error bits, firmware names, descriptor formats, EEPROM layouts, statistics, queues, and the `struct slic_device` runtime object.

## Important APIs, types, and constants
- Hardware status and control macros cover RX/TX frame errors, ISR bits, PHY/link fields, MAC configuration, RX/TX enable/reset bits, register offsets, PCI IDs, and firmware file names.
- Queue constants define RX descriptors/buffers, TX descriptors, status descriptors, alignment constraints, and completion limits.
- `struct slic_upr`/`slic_upr_list` model asynchronous card "UPR" requests for configuration and link status.
- `struct slic_mojave_eeprom` and `struct slic_oasis_eeprom` map EEPROM contents used to extract MAC addresses and validate checksums.
- `struct slic_stats` stores synchronized 64-bit software counters and hardware/error categories exported through netdev/ethtool stats.
- `struct slic_shmem`, `slic_rx_info_*`, `slic_stat_desc`, `slic_tx_desc`, `slic_rx_desc`, and queue/buffer structs define DMA-visible and software queue state.
- `struct slic_device` links PCI/netdev, MMIO registers, locks, NAPI, RX/TX/status queues, stats, UPR queue, link state, model, and fiber/copper mode.
- Inline `slic_read()`, `slic_write()`, and `slic_flush_write()` wrap MMIO access and posted-write flushing.

## Control flow and integration
The header is consumed by `slicoss.c`, which allocates `struct slic_device` in netdev private data, uses the constants to program hardware, fills descriptor structures for DMA, and uses EEPROM structures during initialization.

## State and persistence behavior
Most defined state is runtime-only: queues, DMA addresses, stats, locks, NAPI, and link status. EEPROM structures describe persistent card data read through firmware/UPR requests, especially MAC addresses and checksums. Firmware filenames refer to required runtime-loaded microcode.

## Dependencies and integration points
The header depends on PCI, DMA mapping, netdevice, list, spinlock, and u64 stats APIs. It is tightly coupled to the SLIC hardware ABI and to the firmware blobs declared in `slicoss.c`.

## Risks and edge cases
Descriptor and EEPROM layouts must match hardware/firmware exactly. Alignment constants are enforced manually in allocation paths. Stats macros require correct `u64_stats_sync` usage. The driver uses 32-bit DMA masks, so address handling and upper address registers are constrained.

## Test signals
Compile `slicoss`, probe Mojave/Oasis IDs, validate EEPROM parsing and MAC selection for multi-function devices, check firmware load, exercise RX/TX/status queues, and confirm ethtool stats match error injection or traffic counters.
