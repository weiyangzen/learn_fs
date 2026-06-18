<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip.h

Purpose: Shared header defining Tulip chip identities, register offsets, descriptor formats, private driver state, media-table structures, prototypes, and inline RX/TX control helpers.

Important APIs and types: `struct tulip_chip_table` drives per-chip capabilities, interrupt masks, media timers, and media work callbacks. `enum chips`, `enum tbl_flag`, `enum status_bits`, `enum tulip_mode_bits`, and CSR enums provide shared hardware vocabulary. `struct tulip_rx_desc` and `struct tulip_tx_desc` describe DMA rings. `struct mediatable` and `struct medialeaf` model parsed EEPROM media descriptions. `struct tulip_private` is the central netdev private state for rings, DMA addresses, locks, timers, NAPI, EEPROM, media selection, PHYs, WOL, and device pointers. Inline helpers `tulip_start_rxtx()`, `tulip_stop_rxtx()`, `tulip_restart_rxtx()`, and `tulip_tx_timeout_complete()` centralize CSR6 start/stop behavior.

Control flow: The header is included by all Tulip submodules. The core driver fills `tulip_private`, selects function pointers from `tulip_chip_table`, and calls media, EEPROM, interrupt, and timer functions declared here. Inline stop waits for transmit/receive process-state bits to clear before changing hardware mode.

State and persistence: `tulip_private` holds all volatile driver state: descriptor rings, skb mappings, `cur_*` and `dirty_*` cursors, locks, media flags, EEPROM bytes, WOL settings, PHY address arrays, media table, timers, work item, PCI device, and MMIO base. EEPROM contents are cached but not modified here.

Dependencies and integration: Depends on Linux netdevice, ethtool, timer, PCI, spinlock, IO, and unaligned helpers. It binds modules `21142.c`, `eeprom.c`, `interrupt.c`, `media.c`, `pnic.c`, `pnic2.c`, `timer.c`, and `tulip_core.c`.

Risks: Chip enum ordering is explicitly used as an array index and must not drift from `tulip_tbl[]`. Descriptor bit definitions are shared across DMA paths, so endian and ownership mistakes have broad impact. `tulip_stop_rxtx()` timeout values assume 10/100 Ethernet frame timing.

Test signals: Compile coverage across MMIO/PIO, NAPI/non-NAPI, Tulip chip variants, descriptor ring wrap behavior, RX/TX stop timeouts, and consistency between enum chip values and `tulip_tbl[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/tulip.h -->
