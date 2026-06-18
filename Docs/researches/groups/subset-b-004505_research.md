# Research: subset-b-004505

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta_bm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta_bm.c

## Purpose
`mvneta_bm.c` implements the platform driver for the Marvell NETA Buffer Manager used by Armada 380-class NETA Ethernet controllers. It owns the BM device lifetime, maps BM registers, enables the clock, allocates the BPPI SRAM window, initializes four hardware buffer-pointer pools, and exposes pool operations to the main `mvneta` network driver through exported GPL symbols. Its role is hardware resource management rather than packet processing: it prepares DMA-backed arrays of buffer pointers and feeds/empties those pools through the BM indirect SRAM access window.

## Important APIs, Types, and Functions
- `mvneta_bm_probe()` / `mvneta_bm_remove()` are the platform-driver entry points for `marvell,armada-380-neta-bm`.
- `mvneta_bm_get()` and `mvneta_bm_put()` let a consumer driver obtain and release the BM controller from a device-tree node-backed platform device.
- `mvneta_bm_pool_use()` validates pool sharing rules, initializes a free pool, creates the hardware pool, and pre-fills it via `hwbm_pool_add()`.
- `mvneta_bm_construct()` is the HWBM allocator callback; it writes the buffer virtual address into the first word, DMA maps the buffer, then releases the physical address to hardware with `mvneta_bm_pool_put_bp()`.
- `mvneta_bm_bufs_free()` drains hardware buffer pointers, unmaps DMA buffers, and returns them to HWBM.
- `mvneta_bm_pool_destroy()` tears down one pool when its port map reaches zero.
- Local register helpers `mvneta_bm_read()`, `mvneta_bm_write()`, `mvneta_bm_config_set()`, and `mvneta_bm_config_clear()` centralize MMIO accesses.

## Control Flow
Probe allocates `struct mvneta_bm`, maps the register resource, enables the clock, allocates BPPI SRAM using the `internal-mem` genpool, then calls `mvneta_bm_init()`. Initialization masks/clears interrupts, tunes the BM burst size, allocates the `bm_pools` array, starts the BM unit, resets read/write pointers, and reads optional per-pool `poolN,capacity` and `poolN,pkt-size` properties. When the Ethernet port later calls `mvneta_bm_pool_use()`, a free pool is configured with packet and fragment sizing, bound to the HWBM pool abstraction, given a coherent BPPE array, assigned MBUS target/attribute metadata, enabled in hardware, and filled with DMA-mapped receive buffers. Removal iterates all pools with an all-ports mask, frees SRAM, stops the BM unit, and disables the clock.

## State and Persistence
Runtime state is held in `struct mvneta_bm` and `struct mvneta_bm_pool`: register base, clock, platform device, genpool allocation, per-pool type, packet size, DMA buffer size, BPPE virtual/DMA addresses, port use map, and HWBM counters. Hardware state persists only while the device is bound: pool base/size/read/write registers, XBAR target attributes, interrupt masks/causes, command state, and config bits. Device-tree properties provide boot-time persistent configuration for pool capacity and optional packet size.

## Dependencies and Integration Points
The file depends on Linux platform-driver, OF, DMA, clock, genalloc, MBUS, netdevice, SKB, and `net/hwbm.h` APIs. It integrates with `mvneta_bm.h` for register definitions and inline BPPI accessors, with the main NETA Ethernet driver through exported BM symbols, with device-tree `internal-mem`, and with `mvebu_mbus_get_dram_win_info()` to program crossbar target attributes for coherent pool memory.

## Risks and Edge Cases
`mvneta_bm_construct()` stores a virtual address in the first four bytes using a `u32` cast, which matches the intended 32-bit platform assumptions but is not portable to arbitrary 64-bit virtual addresses. `mvneta_bm_bufs_free()` works around zero BPPI reads and uses `phys_to_virt()` on DMA addresses, so correctness depends on the platform memory mapping model. Partial `hwbm_pool_add()` failure in `mvneta_bm_pool_use()` returns `NULL` after warning but does not fully unwind the newly created pool. Pool sharing rules are strict: long pools cannot be shared by ports and short pools cannot be mixed with other types. Capacity values are clamped or aligned, but invalid `pool_id` values are not guarded inside `mvneta_bm_pool_use()` and must be validated by callers.

## Test Signals
Useful signals are successful BM probe logs, DT-driven capacity warnings, absence of DMA mapping errors, stable receive traffic using BM-backed pools, clean module/device removal without `cannot free all buffers` warnings, and register-level evidence that BM command/config/pool base/size/read/write registers are programmed. Fault tests should exercise missing `internal-mem`, clock enable failure, illegal pool capacities, DMA mapping failure, pool sharing conflicts, and repeated port open/close cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta_bm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta_bm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta_bm.h

## Purpose
`mvneta_bm.h` is the public and private contract for the Marvell NETA Buffer Manager driver. It defines BM register offsets and bitfields, pool sizing constants, packet-buffer size macros, core BM data structures, exported function declarations, and no-op stubs for builds without `CONFIG_MVNETA_BM`.

## Important APIs, Types, and Definitions
- Register groups cover BM configuration/activation, XBAR target attributes, pool base/read/write/size registers, and interrupt cause/mask registers.
- Constants define four pools, capacity minimum/default/maximum/alignment, 32-byte pool pointer alignment, BPPI SRAM size, and `MVNETA_RX_BUF_SIZE()`.
- `enum mvneta_bm_type` tracks whether a pool is free, long-buffer, or short-buffer.
- `struct mvneta_bm` stores global mapped register/SRAM/clock/platform state and the pool array.
- `struct mvneta_bm_pool` stores HWBM pool metadata, packet and buffer sizes, coherent BPPE allocation, port-use bitmap, and backpointer to the controller.
- Inline accessors `mvneta_bm_pool_put_bp()` and `mvneta_bm_pool_get_bp()` write/read pool-specific BPPI slots.
- The conditional API block exposes real declarations when enabled and stubbed functions otherwise.

## Control Flow
This header does not execute control flow directly, but it shapes how `mvneta_bm.c` and the main NETA driver interact. Consumers call `mvneta_bm_get()` to resolve a BM controller, `mvneta_bm_pool_use()` to attach a port to a pool, `mvneta_bm_pool_put_bp()` to return buffer physical addresses to hardware, `mvneta_bm_pool_get_bp()` to drain them, and destroy/free helpers during teardown. If BM support is disabled, callers can still compile against the same names and receive inert or failure-returning stubs.

## State and Persistence
The structures model all mutable software state for the BM controller and pools. Hardware state is represented by macros rather than stored values, with register persistence limited to device lifetime. The inline BPPI accessors encode the pool ID into an SRAM offset via `pool->id << MVNETA_BM_POOL_ACCESS_OFFS`, so the pool ID must remain stable after initialization.

## Dependencies and Integration Points
The header assumes Linux kernel types including `struct clk`, `struct platform_device`, `struct gen_pool`, `dma_addr_t`, `struct hwbm_pool`, `struct device_node`, and MMIO helpers. It is included by `mvneta_bm.c` and by NETA Ethernet code that optionally uses BM acceleration. It also encodes device-tree-facing sizing behavior indirectly through constants consumed during pool initialization.

## Risks and Edge Cases
The inline BPPI helpers take and return 32-bit values even though `dma_addr_t` may be wider on some architectures, reflecting the original Armada NETA constraints. Stub functions hide disabled-BM behavior at compile time, so call sites must treat `mvneta_bm_pool_use()` returning `NULL` as a normal unsupported path. The header declares `mvneta_bm_pool_refill()`, but this source subset does not contain its implementation, so users must verify the main NETA driver supplies it under the same config assumptions.

## Test Signals
Compile coverage should include both `CONFIG_MVNETA_BM=y/m` and disabled builds to validate real declarations and stubs. Runtime tests should confirm pool IDs map to correct BPPI offsets, register macros match hardware documentation, and pool capacity/alignment constants align with the controller limits used by `mvneta_bm.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvneta_bm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/Makefile

## Purpose
This Makefile defines the object composition for the Marvell PPv2 Ethernet driver. It builds the composite `mvpp2.o` module or built-in object when `CONFIG_MVPP2` is enabled and conditionally adds PTP support when `CONFIG_MVPP2_PTP` is selected.

## Important APIs, Types, and Functions
There are no C APIs in this file. The important build contracts are:
- `obj-$(CONFIG_MVPP2) := mvpp2.o`
- `mvpp2-y := mvpp2_main.o mvpp2_prs.o mvpp2_cls.o mvpp2_debugfs.o`
- `mvpp2-$(CONFIG_MVPP2_PTP) += mvpp2_tai.o`

## Control Flow
Kbuild evaluates the config symbols and links the listed objects into the single PPv2 driver object. The classifier (`mvpp2_cls.o`), parser (`mvpp2_prs.o`), main driver (`mvpp2_main.o`), and debugfs support (`mvpp2_debugfs.o`) are always part of the driver when PPv2 is enabled. Timestamp/TAI code is included only for PTP-enabled builds.

## State and Persistence
The file holds build-time state only. It does not create runtime state, but it determines whether runtime PTP hooks in `mvpp2.h` resolve to real functions or inline stubs.

## Dependencies and Integration Points
It integrates with Linux Kbuild and the `CONFIG_MVPP2` / `CONFIG_MVPP2_PTP` Kconfig symbols. The listed object files depend on each other through shared headers such as `mvpp2.h`, `mvpp2_prs.h`, and `mvpp2_cls.h`.

## Risks and Edge Cases
Missing an object here can create link errors or silently remove features. `mvpp2_debugfs.o` is always linked with the driver, so debugfs-related code must remain safe even when debugfs is disabled or unavailable at runtime. Conditional PTP object inclusion must stay synchronized with the `CONFIG_MVPP2_PTP` stubs in `mvpp2.h`.

## Test Signals
Build the driver with `CONFIG_MVPP2` disabled, built-in, and modular; then repeat with `CONFIG_MVPP2_PTP` both disabled and enabled. Link success, absence of unresolved PTP symbols, and successful module load/probe are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_cls.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_cls.c

## Purpose
`mvpp2_cls.c` implements PPv2 classifier, RSS, and ethtool receive-flow-steering helpers. It initializes classifier flow/lookup/C2 TCAM tables, maps parser result-info patterns to classifier flows, configures hash extraction fields for RSS, manages RSS contexts and indirection tables, and translates ethtool RXNFC rules into C2 TCAM entries for queue steering or drop actions.

## Important APIs, Types, and Functions
- `cls_flows[]` is the static flow catalog tying internal flow types, parser flow IDs, supported HEK fields, and parser result-info masks for IPv4/IPv6, TCP/UDP, fragmented/non-fragmented, tagged/untagged, and non-IP traffic.
- Register inspection APIs: `mvpp2_cls_flow_hits()`, `mvpp2_cls_lookup_hits()`, `mvpp2_cls_c2_hit_count()`, `mvpp2_cls_flow_read()`, `mvpp2_cls_lookup_read()`, and `mvpp2_cls_c2_read()`.
- Initialization APIs: `mvpp2_cls_init()`, `mvpp2_cls_port_config()`, `mvpp2_cls_oversize_rxq_set()`, and `mvpp22_port_rss_init()`.
- RSS APIs: `mvpp22_port_rss_enable()`, `mvpp22_port_rss_disable()`, `mvpp22_port_rss_ctx_create()`, `mvpp22_port_rss_ctx_delete()`, `mvpp22_port_rss_ctx_indir_set()`, `mvpp22_port_rss_ctx_indir_get()`, `mvpp2_ethtool_rxfh_set()`, and `mvpp2_ethtool_rxfh_get()`.
- RFS APIs: `mvpp2_ethtool_cls_rule_get()`, `mvpp2_ethtool_cls_rule_ins()`, and `mvpp2_ethtool_cls_rule_del()`.
- Internal helpers manipulate flow table fields, C2 entries, HEK field lists, ethtool flow type conversion, TCAM match construction, and hardware RSS table programming.

## Control Flow
`mvpp2_cls_init()` enables the classifier, clears the flow table, lookup table, and C2 TCAM, bypasses C2 FIFO stages, then initializes all parser/lookup/flow sequences from `cls_flows[]`. `mvpp2_cls_port_config()` configures a port's default lookup behavior and creates the per-port C2 RSS/default-RXQ entry. `mvpp22_port_rss_init()` allocates RSS context 0, fills its indirection table with `ethtool_rxfh_indir_default()`, writes hardware RSS table entries, and configures default hash keys for IP/TCP/UDP flows. Ettool hash-option changes are converted to HEK field masks, constrained by each flow's supported fields, and written into port-specific hash flow-table entries. Ettool classification insertion creates a kernel flow rule, validates the action, builds a 64-bit C2 TCAM key/mask from VLAN and L4 port match keys, programs the C2 entry, and then wires all compatible classifier flow-table entries to that lookup type.

## State and Persistence
Classifier hardware state lives in flow table registers, lookup table registers, C2 TCAM/action/attribute registers, RSS table registers, and hit counters. Software state lives in `priv->rss_tables[]`, `port->rss_ctx[]`, and `port->rfs_rules[]` / `port->n_rfs_rules`. RSS context deletion invalidates any RFS rules that reference the context before freeing the shared table. Ettool RFS rules are stored as copies of `struct ethtool_rxnfc`; temporary `flow_rule` objects are destroyed after programming hardware.

## Dependencies and Integration Points
This file depends on `mvpp2.h`, `mvpp2_cls.h`, `mvpp2_prs.h`, the parser API `mvpp2_prs_add_flow()`, the shared `mvpp2_read()` / `mvpp2_write()` MMIO helpers, Linux ethtool RX flow rule parsing, flow action validation, CPU topology (`num_possible_cpus()`, `cpu_online()`), and netdev warning paths. Debugfs consumes many read/hit helpers from this file. Main port setup and ethtool operations call the initialization and RSS/RFS APIs.

## Risks and Edge Cases
The static `cls_flows[]` table relies on entries with the same `flow_id` being contiguous for the iteration macros in the header. C2 matching is limited to a 64-bit TCAM key and currently builds matches only for VLAN ID/priority and L4 source/destination ports; unsupported dissector keys/actions return errors. Fragmented flows intentionally mask out L4 hashing to avoid packet reordering. RSS queue mapping divides by `port->nrxqs / num_possible_cpus()`, so configurations with fewer RX queues than possible CPUs require scrutiny. `mvpp22_port_rss_ctx_create()` allocates a table before checking `WARN_ON_ONCE(port->rss_ctx[port_ctx] >= 0)`, which can leak the newly allocated global RSS table on that error path. RFS insertion stores port bits with `mvpp2_cls_flow_port_add(&fe, 0xf)`, relying on the macro shape rather than passing `BIT(port->id)` as in other call sites.

## Test Signals
Key tests are classifier initialization without register faults, debugfs hit counters changing under traffic, ethtool `--config-nfc` insertion/deletion/get for queue and drop actions, invalid rule rejection for unsupported dissector/action combinations, RSS enable/disable, RSS context create/delete, indirection table set/get round trips, hash option set/get for IPv4/IPv6/TCP/UDP, and traffic distribution across RXQs matching the RSS table. Regression tests should include VLAN+L4 rules, fragmented traffic, offline CPUs, low RXQ counts, and deletion of an RSS context used by active RFS rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_cls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_cls.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_cls.h

## Purpose
`mvpp2_cls.h` defines the classifier/RSS/RFS interface for the PPv2 driver. It provides table sizes, engine IDs, header-extracted-key option bits, C2 action encodings, flow IDs, flow-table index macros, iteration macros over classifier flows, table-entry structures, and exported classifier/RSS/ethtool helper prototypes.

## Important APIs, Types, and Definitions
- Table constants define 512 classifier flow entries, three data words per flow entry, 64 lookup entries, and 256 classifier RX queues.
- `enum mvpp2_cls_engine` identifies supported classifier engines, especially C2 and hash engines C3HA/C3HB.
- `MVPP22_CLS_HEK_OPT_*` bits describe selectable hash/match fields such as MAC DA, VLAN, IPv4/IPv6 addresses, and L4 ports.
- `enum mvpp2_cls_field_id` maps those logical fields to hardware HEK field IDs.
- `struct mvpp2_cls_c2_entry`, `struct mvpp2_cls_flow_entry`, and `struct mvpp2_cls_lookup_entry` model C2 TCAM/action entries, flow table entries, and lookup table entries.
- `enum mvpp2_prs_flow` assigns parser/classifier flow IDs for traffic classes.
- Index macros such as `MVPP2_CLS_FLT_FIRST()`, `MVPP2_CLS_FLT_C2_RFS()`, `MVPP2_CLS_FLT_C2_RSS_ENTRY()`, `MVPP2_CLS_FLT_HASH_ENTRY()`, and `MVPP22_CLS_C2_RFS_LOC()` encode how flow table and C2 TCAM ranges are partitioned by flow and port.
- Prototypes expose RSS context operations, ethtool hash/rule operations, classifier initialization, hit counters, table reads, and oversize RXQ configuration.

## Control Flow
This header supplies the macros used by `mvpp2_cls.c` to walk classifier flow definitions and to calculate hardware table indices. The `for_each_cls_flow_id*` macros depend on the `cls_flows` array in the C file and skip duplicate contiguous flow IDs. Public prototypes are called from main driver setup, ethtool handlers, and debugfs readers.

## State and Persistence
The header defines the shape of transient software copies of hardware entries. Persistent runtime state is stored elsewhere (`struct mvpp2`, `struct mvpp2_port`, hardware tables), but the macros here determine where each flow, per-port hash entry, RFS entry, and RSS/default C2 entry is stored in those tables.

## Dependencies and Integration Points
It includes `mvpp2.h` and `mvpp2_prs.h`, so it is tightly coupled to global PPv2 register definitions and parser result-info definitions. It is consumed by `mvpp2_cls.c`, `mvpp2_debugfs.c`, and any main-driver ethtool glue that forwards RSS/RFS operations.

## Risks and Edge Cases
The flow iteration macros reference `cls_flows` by name, so they are only usable in scopes where that symbol exists. Flow table partitioning is dense and arithmetic-heavy; off-by-one errors can overlap RSS, RFS, and hash entries. `MVPP22_CLS_C2_PORT_RANGE` reserves only `MVPP2_N_RFS_ENTRIES_PER_FLOW + 1` C2 entries per port, so ethtool rule limits must remain synchronized. The C2 attribute word count is defined as five while implementation currently reads/writes four attribute registers, so any future use of a fifth word must audit the hardware accessors.

## Test Signals
Compile tests should catch prototype drift and macro visibility issues. Runtime validation should confirm classifier table indices are unique across all flows/ports/rule locations, C2 entry ranges stay below 256 entries, flow iteration covers each intended flow ID once where required, and debugfs/ethtool readers decode the same fields that setters wrote.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_cls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_debugfs.c

## Purpose
`mvpp2_debugfs.c` builds a debugfs inspection tree for PPv2 parser, classifier, C2 TCAM, flow table, per-port filters, VLAN filters, and per-port flow hash settings. It is diagnostic-only: files are read-only from the driver's perspective despite some mode bits allowing write permissions, and show functions read hardware/shadow state through parser and classifier helper APIs.

## Important APIs, Types, and Functions
- Private entry structures bind debugfs files to parser TIDs, C2 IDs, classifier flow IDs, flow-table IDs, ports, and the shared `struct mvpp2`.
- `struct mvpp2_dbgfs_entries` preallocates per-entry backing storage for all parser, C2, flow-table, flow, and per-port flow debugfs nodes.
- Show functions expose flow table hits, lookup hits, flow type/id, per-port hash options and engine, C2 hits/default RXQ/RSS enable, parser VLAN IDs, parser entries active on a port, MAC filters, parser lookup ID, port map, AI, header data, SRAM bytes, parser hits, and parser validity.
- Initialization helpers create nested debugfs directories: parser entries, classifier C2 entries, classifier flow table entries, per-port summaries, and logical flow directories.
- Public lifecycle functions are `mvpp2_dbgfs_init()`, `mvpp2_dbgfs_cleanup()`, and `mvpp2_dbgfs_exit()`.

## Control Flow
`mvpp2_dbgfs_init()` lazily creates the global `mvpp2` root, creates a per-device directory, allocates `priv->dbgfs_entries`, initializes parser and classifier subtrees, creates per-port directories, then creates flow directories with per-port subdirectories. Each debugfs file uses `DEFINE_SHOW_ATTRIBUTE()` plumbing to call a small show function. Cleanup removes the per-device tree recursively and frees the backing entries; global exit removes the top-level root.

## State and Persistence
Debugfs state is held in `priv->dbgfs_dir`, `priv->dbgfs_entries`, and static `mvpp2_root`. The files expose live hardware and shadow state rather than storing independent data. Parser validity and lookup values come from `priv->prs_shadow` plus hardware reads. C2/default queue/RSS data comes from C2 registers. Flow hash fields and engine values come from classifier flow-table entries. State persists only for the device lifetime and debugfs mount lifetime.

## Dependencies and Integration Points
The file depends on Linux debugfs, seq_file show helpers, slab allocation, `mvpp2.h`, parser helpers from `mvpp2_prs.h`, and classifier helpers from `mvpp2_cls.h`. Main driver probe/setup calls `mvpp2_dbgfs_init()`, teardown calls `mvpp2_dbgfs_cleanup()`, and module/driver exit calls `mvpp2_dbgfs_exit()`. The diagnostics are useful for validating parser/classifier/RSS/RFS behavior implemented in `mvpp2_prs.c` and `mvpp2_cls.c`.

## Risks and Edge Cases
The code does not check `debugfs_create_dir()` or `debugfs_create_file()` return values in most places, which is common for debugfs but can leave partial trees. Some parser files are created with `0644` even though only show operations are defined by `DEFINE_SHOW_ATTRIBUTE()`, so writes are not meaningful. `mvpp2_dbgfs_flow_type_show()` switches on ethtool flow constants while `mvpp2_cls_flow.flow_type` stores internal `MVPP22_FLOW_*` bitmasks, so displayed names may degrade to `other` unless values happen to match. `port_flow_entries` has one slot per port but is reused while creating every flow's per-port directory, so all flow per-port debugfs files for a given port can point at the most recently initialized flow entry rather than the directory's intended flow. `mvpp2_dbgfs_exit()` removes only `mvpp2_root` non-recursively, while per-device cleanup uses recursive removal.

## Test Signals
Mount debugfs and confirm the expected tree appears under `/sys/kernel/debug/mvpp2/<device>/`. Read parser entry files, classifier C2 files, flow table hit files, port filter files, and per-flow per-port hash/engine files under traffic. Verify hit counters increase, parser port maps match configured ports, VLAN/MAC filters reflect netdev settings, C2 default RXQ and RSS enable match ethtool RSS state, and cleanup removes device directories without use-after-free warnings. Specific regression checks should validate flow type names and per-flow per-port hash files across multiple flow directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_debugfs.c -->
