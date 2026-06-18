# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2.h

## Purpose
`mvpp2.h` is the main shared hardware and software interface for the Marvell PPv2 Ethernet driver. It defines register maps, bitfields, descriptor layouts, queue and buffer-manager structures, per-port state, RSS/RFS/PTP/debugfs hooks, and constants for PPv2.1, PPv2.2, and PPv2.3 variants. Most PPv2 implementation files depend on this header for the controller ABI.

## Important APIs, Types, and Definitions
- Register definitions cover RX/TX DMA, parser, classifier, RSS, descriptor manager, MBUS/AXI bridges, interrupts, BM pools, counters, TX scheduler, GMAC/XLG/XPCS/FCA/PTP/TAI, system controller, and flow-control firmware memory.
- Buffer and packet sizing macros include `MVPP2_SKB_HEADROOM`, `MVPP2_RX_PKT_SIZE()`, `MVPP2_RX_BUF_SIZE()`, `MVPP2_RX_TOTAL_SIZE()`, and BM frame/pool sizing constants.
- `struct mvpp2` owns shared controller state: mapped register spaces, clocks, regmap, port list/map, TAI, thread/lock maps, aggregated TX queues, BM pools, parser shadow state, RSS tables, page pools, workqueue, debugfs state, and shared spinlocks.
- `struct mvpp2_port` owns per-netdev state: queue arrays, NAPI vectors, phylink/PCS/PHY resources, XDP program, BM pools, stats, RSS contexts, RFS rules, timestamp settings, and flow-control flags.
- Descriptor types `mvpp21_tx_desc`, `mvpp21_rx_desc`, `mvpp22_tx_desc`, `mvpp22_rx_desc`, and wrapper unions encode hardware DMA descriptor layouts.
- Queue structures `mvpp2_tx_queue`, `mvpp2_txq_pcpu`, `mvpp2_rx_queue`, and `mvpp2_queue_vector` define ring ownership, per-CPU TX accounting, NAPI/IRQ mapping, and XDP RXQ info.
- `struct mvpp2_bm_pool`, `struct mvpp2_rss_table`, `struct mvpp2_rfs_rule`, and `struct mvpp2_ethtool_fs` support BM, RSS, and ethtool flow steering.
- Declared cross-file APIs include `mvpp2_write()`, `mvpp2_read()`, debugfs lifecycle, RX FIFO flow-control enablement, and optional PTP/TAI hooks.

## Control Flow
This header does not run code except for small PTP stubs and `mvpp22_rx_hwtstamping()`, but it directs control flow across the driver. Main probe code allocates and fills `struct mvpp2`, creates `struct mvpp2_port` instances, initializes parser/classifier/BM/RSS state, wires phylink and interrupts, and uses the register macros for all hardware programming. RX/TX paths use descriptor unions and queue macros to traverse rings. Classifier code uses the RSS/RFS fields and classifier register definitions. Debugfs code consumes `dbgfs_dir` and `dbgfs_entries` from `struct mvpp2`.

## State and Persistence
Runtime state is split between global shared hardware state in `struct mvpp2`, per-port netdev state in `struct mvpp2_port`, per-CPU TX/stat state, descriptor rings, BM pool arrays, page pools, parser shadow tables, RSS indirection tables, and ethtool RFS rule slots. Hardware register state persists while the device is bound and is mostly reconstructed during probe/open/configuration. Persistent external inputs include device tree/firmware node data, Kconfig options, phylink mode, ethtool settings applied at runtime, and optional PTP configuration.

## Dependencies and Integration Points
The header integrates with Linux networking (`net_device`, NAPI, ethtool flow offload, XDP, BPF, page_pool), PHY/phylink, DMA, regmap, clock, interrupt, timestamping, workqueue, debugfs, and Marvell-specific parser/classifier modules. It is the central include for `mvpp2_main.c`, `mvpp2_prs.c`, `mvpp2_cls.c`, `mvpp2_debugfs.c`, and optionally `mvpp2_tai.c`.

## Risks and Edge Cases
The file encodes many hardware-version-specific offsets and masks; using a PPv2.2/2.3 register on PPv2.1 or vice versa can corrupt unrelated state. Descriptor layouts are hardware ABI and must not change padding or endian annotations casually. Queue and BM limits are tightly coupled to hardware table sizes, CPU/thread counts, and RSS table width. `MVPP2_SKB_HEADROOM` is capped by a 3-bit hardware packet-offset field, so XDP and SKB headroom changes must preserve the 224-byte maximum. Shared state such as parser shadows, BM pools, and TX/BM locks requires careful concurrency handling in implementation files.

## Test Signals
Build coverage should include PPv2.1 and PPv2.2/2.3 configurations where possible, with and without `CONFIG_MVPP2_PTP`, XDP, RSS, RFS, and debugfs consumers. Runtime signals include successful probe, port open/close, RX/TX traffic, NAPI interrupt distribution, ethtool RSS/RFS operations, page-pool recycling, XDP pass/drop/tx/redirect, PTP timestamp behavior when enabled, and debugfs register views matching expected hardware state.
