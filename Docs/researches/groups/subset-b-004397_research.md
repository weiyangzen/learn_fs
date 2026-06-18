# subset-b-004397 research

Grouped research for the Chelsio cxgb3/cxgb4 source files assigned to `subset-b-004397`. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/vsc8211.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/vsc8211.c

## Purpose
This file implements the cxgb3 PHY driver glue for the Vitesse VSC8211 10/100/1000 PHY. It provides `struct cphy_ops` implementations for copper and fiber operating modes, translates VSC8211-specific MDIO status into Linux link speed/duplex/pause values, and prepares a `struct cphy` instance during adapter initialization.

## Important APIs, Types, And Functions
- `t3_vsc8211_phy_prep()` is the exported setup entry point. It initializes `struct cphy`, waits for MDIO readiness, detects copper versus 1000BASE-X fiber mode, updates caps/description/ops, and programs VSC8211 pages/registers.
- `vsc8211_ops` and `vsc8211_fiber_ops` provide the PHY method tables. The main difference is advertising and link-status interpretation.
- `vsc8211_get_link_status()` handles copper status using BMCR/BMSR, `VSC8211_AUX_CTRL_STAT`, and pause advertisement registers.
- `vsc8211_get_link_status_fiber()` handles Clause 37/1000BASE-X status using `ADVERTISE_1000X*` bits.
- Interrupt helpers program/read `VSC8211_INTR_ENABLE` and `VSC8211_INTR_STATUS`; `vsc8211_intr_handler()` maps hardware causes to `cphy_cause_link_change` and `cphy_cause_fifo_error`.

## Control Flow
Reset and power control are thin wrappers over common MDIO helpers. Link-status paths first read BMCR/BMSR, reread BMSR when latch-low link status is clear, then either derive forced mode from BMCR or, after autoneg completion, derive negotiated properties from VSC8211 auxiliary status or fiber advertisement/LPA registers. Prep initially assumes copper, reads `VSC8211_EXT_CTRL`, programs LEDs for copper, or switches to fiber ops and configures signal-detect, Clause 37 view, reset, and a post-reset delay for fiber.

## State And Persistence
There is no filesystem or persistent software state. State lives in PHY hardware registers and the caller-owned `struct cphy`: `caps`, `desc`, and `ops` are changed when fiber mode is detected. Interrupt status is clear-on-read.

## Dependencies And Integration Points
The file depends on `common.h`, cxgb3 MDIO helpers (`t3_mdio_read`, `t3_mdio_write`, `t3_mdio_change_bits`, `t3_phy_reset`), Linux MII constants, and Chelsio `struct cphy`/`struct adapter` lifecycle code. It integrates with adapter link management through the `cphy_ops` table returned by `cphy_init()`.

## Risks
Copper/fiber detection relies on VSC8211 media-mode bits and can misconfigure advertising if those bits are unexpected. Pause resolution has separate copper and 1000BASE-X rules and is sensitive to asymmetric-pause bit combinations. Interrupts are cleared by reading status, so read ordering matters. The reset routine assumes immediate reset completion, so hardware variants with slower reset behavior would need different timing.

## Test Signals
Useful tests are PHY bring-up on copper and fiber SKUs, forced 10/100/1000 modes, autoneg restart, link up/down interrupts, FIFO error interrupts, and pause negotiation matrix checks. Regression signals include ethtool link mode reporting, successful traffic after `t3_vsc8211_phy_prep()`, and no MDIO errors during reset/page switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/vsc8211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/xgmac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/xgmac.c

## Purpose
This file implements cxgb3 XGMAC control for Chelsio T3 adapters: MAC/SERDES reset, exact and hash address filters, MTU and flow-control programming, Tx/Rx enable/disable, watchdog recovery, and RMON statistics accumulation.

## Important APIs, Types, And Functions
- `t3_mac_reset()` and `t3b2_mac_reset()` reset MAC/PCS/RGMII/XAUI/XG2G blocks, initialize receive config, and apply revision-specific workarounds.
- `t3_mac_set_address()`, `t3_mac_set_num_ucast()`, `t3_mac_set_rx_mode()`, and exact-filter enable/disable helpers program unicast/multicast reception.
- `t3_mac_set_mtu()` updates frame size, drains Rx FIFO when needed, recalculates pause watermarks, and adjusts Tx FIFO thresholds.
- `t3_mac_set_speed_duplex_fc()` programs port speed and pause-frame behavior.
- `t3_mac_enable()`, `t3_mac_disable()`, `t3b2_mac_watchdog_task()`, and `t3_mac_update_stats()` control data path activation, hang recovery, and counter rollup.

## Control Flow
Reset begins with register clears and FIFO/SERDES setup, then selects the appropriate reset bits based on 10G, XAUI, or RGMII mode. The B2 reset path temporarily disables MPS traffic, drains hardware, changes drop config, resets, and restores state. Rx mode first toggles promiscuous copy-all, then reserves exact filters for multicast entries and hashes overflow entries. MTU changes program max frame size directly unless Rx is active on newer revisions, where filters are disabled and FIFO drain is required before updating. The watchdog compares software and hardware Tx progress counters, toggles Tx on short stalls, and escalates to `t3b2_mac_reset()` after repeated failures.

## State And Persistence
State is in hardware registers plus cached fields in `struct cmac`: `nucast`, `txen`, watchdog counters (`tx_mcnt`, `tx_tcnt`, `tx_xcnt`, `rx_mcnt`, `rx_pause`, `rx_xcnt`, `rx_ocnt`, `toggle_cnt`), and accumulated `mac_stats`. RMON hardware counters are clear-on-read or limited width, so periodic accumulation is required.

## Dependencies And Integration Points
The implementation depends on `common.h`, `regs.h`, adapter revision/capability helpers (`uses_xaui`, `is_10G`), register access helpers, netdevice multicast lists, and Linux netdev flags. It integrates with cxgb3 port setup, ethtool statistics, multicast configuration, MTU changes, and watchdog scheduling.

## Risks
Incorrect reset sequencing can leave XAUI/PCS/RGMII blocks wedged. Active-Rx MTU changes depend on FIFO-empty polling and temporary filter changes, creating risk of dropped frames or stale filter state on errors. The B2 watchdog/reset path touches global MPS and TP drop registers and must preserve/restore them correctly. RMON counters can overflow if `t3_mac_update_stats()` is not called frequently enough.

## Test Signals
Test MTU changes with Rx enabled/disabled, promiscuous/all-multicast transitions, multicast lists beyond exact-filter capacity, speed/flow-control programming, traffic after reset on XAUI and non-XAUI adapters, and watchdog recovery under induced Tx stalls. Statistics tests should validate monotonic accumulation across 32-bit counter rollover windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/xgmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/Makefile

## Purpose
This Makefile defines how the Linux kernel builds the Chelsio T4/T5/T6 `cxgb4` Ethernet driver. It maps `CONFIG_CHELSIO_T4` to the `cxgb4.o` module/object and lists the component objects that form the driver.

## Important APIs, Types, And Functions
There are no C APIs here. The important build variables are `obj-$(CONFIG_CHELSIO_T4) += cxgb4.o`, the `cxgb4-objs` object list, and conditional additions for `CONFIG_CHELSIO_T4_DCB`, `CONFIG_CHELSIO_T4_FCOE`, `CONFIG_DEBUG_FS`, and `CONFIG_THERMAL`.

## Control Flow
Kbuild includes this file during kernel compilation. If `CONFIG_CHELSIO_T4` is disabled, no `cxgb4` object is built. If enabled, Kbuild links core objects such as `cxgb4_main.o`, `t4_hw.o`, `sge.o`, `clip_tbl.o`, `cxgb4_cudbg.o`, `cudbg_common.o`, `cudbg_lib.o`, and `cudbg_zlib.o`. Optional feature objects are appended according to their config symbols.

## State And Persistence
The file has no runtime state. It determines the persistent build artifact composition for built-in or modular kernel outputs.

## Dependencies And Integration Points
It integrates with Linux Kbuild and depends on C source/object names remaining synchronized. The CUDBG files researched in this item are linked into the driver unconditionally when `CONFIG_CHELSIO_T4` is enabled. Debugfs, DCB, FCoE, and thermal support are conditionally compiled.

## Risks
Adding a source file without updating this list prevents code from linking. Removing or renaming a listed source creates build failures. Feature objects must be behind the right config guards or references to optional subsystem headers/APIs can break configurations.

## Test Signals
Build with `CONFIG_CHELSIO_T4=m` and `=y`, and matrix optional configs for DCB, FCoE, DEBUG_FS, and THERMAL. A useful signal is that `cxgb4_cudbg.o`, `cudbg_common.o`, `cudbg_lib.o`, `cudbg_zlib.o`, and `clip_tbl.o` are present in the link when the base driver is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/clip_tbl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/clip_tbl.c

## Purpose
This file implements the cxgb4 CLIP table, a local-IP reference table used for offloaded connections, especially IPv6. It manages a software hash table of IPv4/IPv6 addresses, reference counts users, sends firmware CLIP allocate/free commands for IPv6 addresses, and exposes debugfs/seq-file display.

## Important APIs, Types, And Functions
- `t4_init_clip_tbl()` allocates `struct clip_tbl`, initializes hash buckets and the free list, and sizes the table from firmware-provided start/end indexes.
- `cxgb4_clip_get()` looks up or allocates an address entry, increments/sets its refcount, and sends `FW_CLIP_CMD_ALLOC` for IPv6.
- `cxgb4_clip_release()` decrements refcount, returns entries to the free list, and sends `FW_CLIP_CMD_FREE` for IPv6 when the final user leaves.
- `cxgb4_update_root_dev_clip()` walks the physical netdev, master upper device, and VLAN devices to install IPv6 addresses.
- `clip_tbl_show()` renders address/refcount/free-entry diagnostics.

## Control Flow
Lookups hash IPv4 into the first half of buckets and IPv6 into the second half. `cxgb4_clip_get()` first scans under `read_lock_bh`; on miss it switches to `write_lock_bh`, removes an entry from `ce_free_head`, inserts it into the selected hash list, fills the sockaddr union, and for IPv6 issues a firmware mailbox command. Release mirrors this: scan under read lock, then write-lock the table, spin-lock the entry, decrement the refcount, and if zero move it back to the free list and free IPv6 firmware state.

## State And Persistence
Runtime state lives in `adapter->clipt`: hash buckets, `ce_free_head`, `nfree`, the allocated `cl_list`, entry addresses, and `refcnt`. It is not persisted across driver unload. IPv6 CLIP state also persists in adapter firmware until released or reset.

## Dependencies And Integration Points
The file depends on Linux netdevice, IPv6 address, VLAN, jhash, list, refcount, rwlock, and seq-file facilities. It integrates with `struct adapter` via `netdev2adap()`, firmware mailbox submission via `t4_wr_mbox_meat()`, and upper-layer offload users through exported `cxgb4_clip_get()`/`cxgb4_clip_release()`.

## Risks
There is a race window after read-lock lookup miss before write-lock insertion; two callers for the same new address can allocate duplicates because the code does not recheck under write lock. On IPv6 firmware allocation failure, the entry has already been inserted and `nfree` decremented, but the error path returns without removing it, which is a leak/stale-entry risk. Firmware free return values are ignored. `clip_tbl_show()` assumes `adapter->clipt` is non-NULL.

## Test Signals
Exercise concurrent `cxgb4_clip_get()` for the same address, CLIP table exhaustion, IPv6 firmware command failure injection, release-to-zero, repeated get/release reference counts, VLAN/bond address discovery, and debugfs display. Offload tests should verify that IPv6 connections are not offloaded when CLIP allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/clip_tbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/clip_tbl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/clip_tbl.h

## Purpose
This header declares the CLIP table data structures and public functions used by cxgb4 components that need to manage local IP entries for offload.

## Important APIs, Types, And Functions
- `struct clip_entry` stores a per-address spinlock, `refcount_t`, list linkage, and an IPv4/IPv6 sockaddr union.
- `struct clip_tbl` stores firmware CLIP range metadata, an rwlock, free-entry count, free list, backing allocation, and flexible hash bucket array.
- `CLIPT_MIN_HASH_BUCKETS` enforces a minimum split hash table size.
- Prototypes expose initialization, cleanup, get/release, debug display, and root-device IPv6 update functions.

## Control Flow
The header itself has no control flow. Its structure layout drives `clip_tbl.c`: hash buckets and free list share the same `list` field in each entry, table-wide mutations are protected by `rwlock_t`, and final reference updates are additionally protected by the entry spinlock.

## State And Persistence
The declarations define in-memory driver state only. `clip_entry` instances are allocated as one backing array and recycled between hash lists and the free list. Firmware state is implied by callers, not represented directly beyond the address/refcount.

## Dependencies And Integration Points
It depends on Linux `refcount.h`, list/spinlock/rwlock/netdevice types supplied by includers, and `struct adapter`. It is included by `clip_tbl.c` and by driver code that holds `adapter->clipt` or invokes CLIP APIs.

## Risks
The flexible array is annotated with `__counted_by(clipt_size)`, so allocation must set `clipt_size` consistently before use. Because IPv4 and IPv6 share a union, callers must use the address family consistently. The same list node is used for both free and hash membership, so all transitions must be list-safe and lock-protected.

## Test Signals
Compile tests should cover configs with this header included from different translation units. Runtime validation comes from CLIP allocation/release tests, free-list count consistency, debug display, and lockdep during concurrent offload address operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/clip_tbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_common.c

## Purpose
This file provides common CUDBG buffer management helpers used by all cxgb4 debug-dump collectors. It abstracts whether entity collectors write directly into the ethtool/vmcore output buffer or into a reusable compression input buffer.

## Important APIs, Types, And Functions
- `cudbg_get_buff()` reserves a collector input buffer of a requested size. With no compression it points into the main output at the current offset; with compression it points to `pdbg_init->compress_buff`.
- `cudbg_put_buff()` releases/reset the temporary input buffer and clears the reusable compression buffer.
- `cudbg_update_buff()` advances the output buffer offset after an uncompressed direct write.

## Control Flow
Collectors call `cudbg_get_buff()` before filling entity data. The helper validates output capacity, then either returns an output slice or the compression scratch buffer. After collection, `cudbg_lib.c` calls `cudbg_write_and_release_buff()`, which either invokes `cudbg_update_buff()` or compresses and then calls `cudbg_put_buff()`.

## State And Persistence
State is transient in `struct cudbg_buffer` offsets and `struct cudbg_init` compression fields. No persistent state is stored. Under compression, the scratch buffer is zeroed after each entity/chunk so it can be reused.

## Dependencies And Integration Points
It depends on `cxgb4.h`, `cudbg_if.h`, and `cudbg_lib_common.h`. The helpers are used by `cudbg_lib.c` collectors and indirectly by `cxgb4_cudbg.c` when collecting ethtool/vmcore dumps.

## Risks
Size checks use `offset + size`, which assumes no integer overflow in practical dump sizes. Compression mode rejects entity chunks larger than `compress_buff_size`, so callers must chunk large data. `cudbg_update_buff()` trusts `pin_buff->size`; if a collector writes less than reserved size without adjusting it, the output will include stale/zero padding.

## Test Signals
Test no-compression and compression modes, exact-fit buffers, too-small buffers returning `CUDBG_STATUS_NO_MEM`, chunked large entities, and repeated collector calls reusing the compression buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_entity.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_entity.h

## Purpose
This header defines the on-wire/in-buffer entity payload structures used by cxgb4 CUDBG dumps. It describes mailbox logs, CIM/TP/SGE/PM/PCIE snapshots, memory maps, TID/TCAM data, VPD, logic-analyzer captures, PBT tables, queue descriptors, and constants needed to decode them.

## Important APIs, Types, And Functions
The key types are `struct cudbg_mbox_log`, `cudbg_cim_qcfg`, `cudbg_pm_stats`, `cudbg_hw_sched`, `ireg_field`/`ireg_buf`, `cudbg_meminfo`, `cudbg_tid_info_region_rev1`, `cudbg_mps_tcam`, `cudbg_tcam`, `cudbg_tid_data`, `cudbg_ulptx_la`, `cudbg_pbt_tables`, and `cudbg_qdesc_*`. `enum cudbg_le_entry_types` classifies LE/TID entries. Revision macros such as `CUDBG_MEMINFO_REV`, `CUDBG_TID_INFO_REV`, `CUDBG_ULPTX_LA_REV`, and `CUDBG_QDESC_REV` version selected payloads.

## Control Flow
The header has no executable flow, but it defines layouts that collector functions fill. Several structures have flexible arrays (`cudbg_tp_la`, `cudbg_cim_pif_la`, `cudbg_qdesc_entry`, `cudbg_qdesc_info`) so collectors must compute exact sizes and keep these fields last.

## State And Persistence
These structures are serialized into a CUDBG dump buffer, which may be returned through ethtool or vmcore device dump. The state is a snapshot of live adapter hardware/software state at collection time, not a mutable runtime owner.

## Dependencies And Integration Points
The header depends on many constants from cxgb4/t4 register and firmware headers via includers. It is included by `cxgb4_cudbg.h`, `cudbg_lib.c`, and decoding consumers. `cudbg_region[]` is a static string table used by memory-region mapping code in `cudbg_lib.c`.

## Risks
Layout changes can break dump decoder compatibility. Flexible-array size miscalculations can corrupt subsequent entities. The `cudbg_region[]` ordering is semantically tied to memory-region indexes used by `cudbg_fill_meminfo()` and context dump logic. Endianness is mixed: collectors must explicitly encode or decode hardware data where required.

## Test Signals
Build-time structure-size checks, dump decode compatibility tests, LE/TCAM and qdesc parser tests, and sample dumps across T4/T5/T6 hardware are important. Versioned entities should be validated by old and new decoder tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_entity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_if.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_if.h

## Purpose
This header defines the public CUDBG collection interface: status codes, dump version, entity IDs, initialization context, and a size conversion helper.

## Important APIs, Types, And Functions
- Status codes include `CUDBG_STATUS_NO_MEM`, `CUDBG_STATUS_ENTITY_NOT_FOUND`, `CUDBG_STATUS_NOT_IMPLEMENTED`, `CUDBG_SYSTEM_ERROR`, `CUDBG_STATUS_CCLK_NOT_DEFINED`, and `CUDBG_STATUS_PARTIAL_DATA`.
- `enum cudbg_dbg_entity_type` assigns stable IDs for all dump entities from register dumps through flash.
- `struct cudbg_init` passes the adapter, output buffer, compression mode, compression buffer, and zlib workspace to collectors.
- `cudbg_mbytes_to_bytes()` converts hardware memory-size units to bytes.

## Control Flow
There is no executable control flow except the inline conversion helper. The enum values drive `cxgb4_cudbg.c` entity arrays, `cudbg_get_entity_hdr()` indexing, and `cudbg_get_entity_length()` sizing.

## State And Persistence
`struct cudbg_init` is per-collection transient state. The major/minor version (`1.14`) is written into `struct cudbg_hdr` and persists in generated dumps for decoder compatibility.

## Dependencies And Integration Points
The file depends on `struct adapter` being visible through includers. It is included by CUDBG common, zlib, library, and cxgb4 glue files. Entity IDs must remain synchronized with collector tables and userspace dump decoders.

## Risks
Changing entity numeric values or versioning without decoder coordination breaks compatibility. The helper uses integer multiplication; very large memory-size units would overflow `unsigned int`, though hardware values are expected to fit the driver dump model.

## Test Signals
Compile coverage for all CUDBG translation units, decoder compatibility against version `1.14`, and entity table tests verifying every collected entity has a matching length and header slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib.c

## Purpose
This file is the main cxgb4 CUDBG collector library. It calculates entity sizes and implements collectors for registers, firmware logs, CIM queues and logic analyzers, adapter memories, RSS, PM/hardware scheduler stats, indirect register banks, SGE contexts, MPS/LE TCAMs, VPD, mailbox logs, queue descriptors, flash, and T6-specific blocks.

## Important APIs, Types, And Functions
- `cudbg_get_entity_length()` returns the expected payload size for each entity based on chip version, firmware parameters, memory BARs, queue sizes, and software state.
- Buffer helpers `cudbg_do_compression()`, `cudbg_write_and_release_buff()`, `cudbg_align_debug_buffer()`, and `cudbg_get_entity_hdr()` support the collection framework.
- `cudbg_fill_meminfo()`, memory-region helpers, `cudbg_memory_read()`, and `cudbg_read_fw_mem()` map and read EDC/MC/HMA memory while skipping large Tx/Rx payload regions.
- Collector families include `cudbg_collect_cim_*`, `cudbg_collect_*_meminfo`, `cudbg_collect_*_indirect`, `cudbg_collect_dump_context()`, `cudbg_collect_mps_tcam()`, `cudbg_collect_le_tcam()`, `cudbg_collect_qdesc()`, and `cudbg_collect_flash()`.

## Control Flow
The top-level caller in `cxgb4_cudbg.c` selects an entity and calls the matching function. Most collectors allocate a temporary CUDBG buffer, fill it via `t4_*` hardware/firmware helpers, set `cudbg_err` on failures, then write/release the buffer with optional chunked compression. Memory dumps first build a memory map, flush firmware cache when available, then read in `CUDBG_CHUNK_SIZE` chunks and periodically `schedule()` to avoid CPU-stall warnings. Context dumps prefer firmware reads/flushes, but fall back to backdoor register access. TCAM collectors read every table index and use firmware mailbox reads for replicate maps when possible, falling back to direct registers.

## State And Persistence
The library does not own long-lived state. It snapshots `struct adapter` fields, mailbox logs, SGE queues, ULD queue arrays, firmware memory, flash, and hardware registers into the caller-provided dump buffer. It uses locks for shared state: `win0_lock` for memory windows, `uld_mutex` for ULD queues, and `tc_mqprio->mqprio_mutex` for ETHOFLD queue descriptors.

## Dependencies And Integration Points
It depends heavily on `cxgb4.h`, `t4_regs.h`, firmware APIs, CUDBG headers, zlib wrapper, Linux `sort`, allocation, mutex, and scheduling primitives. It integrates with ethtool dump and vmcore dump through `cxgb4_cudbg.c`. It also depends on hardware generation helpers (`is_t4/t5/t6`, `CHELSIO_CHIP_VERSION`) to choose register arrays and memory semantics.

## Risks
Entity length and actual collector output must stay aligned; mismatches can truncate or leave unused space. Many collectors read live hardware and may perturb state or race with traffic; `cudbg_collect_sge_indirect()` intentionally avoids certain T6 registers while ports are running. Partial-data handling varies between collectors. `cudbg_collect_qdesc()` reserves a worst-case buffer capped to `CUDBG_DUMP_BUFF_SIZE`, so large live queue sets can yield partial output. Memory-window reads require alignment and locking; bad region math can read wrong adapter memory.

## Test Signals
Validation should collect dumps on T4, T5, and T6 with compression enabled/disabled, ports idle/running, firmware attached/unattached, and large memory/flash sizes. Decoder tests should verify all entity headers, sizes, padding, partial-data warnings, qdesc counts, TCAM/TID boundaries, and memory-map regions. Fault injection for mailbox, PCI config, VPD, flash, and memory reads is useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib.h

## Purpose
This header declares the CUDBG collector API implemented by `cudbg_lib.c` and provides inline helpers for mapping cxgb4 queue types into CUDBG qdesc entries.

## Important APIs, Types, And Functions
It declares every `cudbg_collect_*()` function used by `cxgb4_cudbg.c`, plus sizing and helper functions such as `cudbg_get_entity_length()`, `cudbg_get_entity_hdr()`, `cudbg_align_debug_buffer()`, `cudbg_cim_obq_size()`, `cudbg_dump_context_size()`, `cudbg_fill_meminfo()`, `cudbg_fill_le_tcam_info()`, and `cudbg_fill_qdesc_num_and_size()`. Inline helpers map ULD TX/RX/FL/CI queues to `enum cudbg_qdesc_qtype` and copy TX, RX, and freelist descriptors into a `cudbg_qdesc_entry`.

## Control Flow
The header has no standalone flow. Its inline qdesc helpers are invoked by `cudbg_collect_qdesc()` to populate descriptor metadata and data, then advance via `cudbg_next_qdesc()`.

## State And Persistence
The header defines access patterns for snapshotting live queue descriptor rings. It does not allocate or persist state itself. The copied descriptor bytes become persistent only inside the generated CUDBG dump.

## Dependencies And Integration Points
It depends on CUDBG entity definitions, cxgb4 queue structures (`sge_txq`, `sge_rspq`, `sge_fl`), and constants for ULD IDs. It is included by `cxgb4_cudbg.h` so the ethtool/vmcore glue can see collector prototypes and callback types.

## Risks
The qdesc helpers blindly `memcpy()` descriptor memory based on queue size and descriptor size, so callers must ensure queues are initialized and buffers are sized. Unknown ULD IDs map to `CUDBG_QTYPE_UNKNOWN`, which may reduce decoder usefulness. Prototype drift between this header and `cudbg_lib.c` will break builds.

## Test Signals
Compile tests across optional ULD feature configs, CUDBG collection with NIC/ULD/ETHOFLD queues present and absent, and decoder checks for qdesc entry sizing/order are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib_common.h

## Purpose
This header defines common CUDBG dump headers, entity headers, buffer/error structures, compression constants, and common buffer helper prototypes.

## Important APIs, Types, And Functions
- `struct cudbg_hdr` is the top-level dump header with signature, version, total data length, entity count, chip version, dump type, and compression type.
- `struct cudbg_entity_hdr` describes each entity's type, start offset, size, error/warning fields, padding, and extension metadata.
- `struct cudbg_ver_hdr` versions selected entity payloads.
- `struct cudbg_buffer` and `struct cudbg_error` are the common collection data/error carriers.
- `CDUMP_MAX_COMP_BUF_SIZE` and `CUDBG_CHUNK_SIZE` define compression chunk sizing.

## Control Flow
There is no executable flow here. The structure definitions drive `cxgb4_cudbg_collect()` header initialization, per-entity collection, alignment, and error propagation.

## State And Persistence
Instances of `cudbg_hdr`, `cudbg_entity_hdr`, and versioned payload headers are serialized into ethtool/vmcore dumps. `cudbg_buffer` and `cudbg_error` are transient in-kernel structures.

## Dependencies And Integration Points
It depends on `struct cudbg_init` being declared by `cudbg_if.h` before the helper prototypes are used. It is included by `cudbg_common.c`, `cudbg_lib.c`, `cudbg_zlib.c`, and `cxgb4_cudbg.c`.

## Risks
Changing header layout or constants can break userspace decoders. Entity headers are indexed by entity ID minus one, so `max_entities` and enum values must remain compatible. Compression chunk size affects maximum temporary buffer requirements and output format.

## Test Signals
Dump-header parser tests, entity-offset/padding validation, compression and no-compression collection tests, and compatibility checks against existing CUDBG decoder tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_lib_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_zlib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_zlib.c

## Purpose
This file implements zlib compression for CUDBG entity data. It prepends a CUDBG compression header and deflates a collector input buffer into the output dump buffer.

## Important APIs, Types, And Functions
- `cudbg_get_compress_hdr()` reserves space in the output buffer for `struct cudbg_compress_hdr`.
- `cudbg_compress_buff()` initializes a kernel zlib deflate stream with `pdbg_init->workspace`, compresses `pin_buff`, fills compressed/decompressed sizes, and advances the output offset.

## Control Flow
The caller passes an input chunk and output buffer. The function reserves the compression header, sets `compress_id`, initializes zlib with CUDBG window/memory parameters, points zlib at input and remaining output space, calls `zlib_deflate(..., Z_FINISH)`, ends the stream, records sizes, and updates `pout_buff->offset`.

## State And Persistence
State is transient in `struct z_stream_s` and the caller-provided workspace. The compression header and compressed payload persist inside the CUDBG dump.

## Dependencies And Integration Points
It depends on Linux `zlib.h`, `cxgb4.h`, `cudbg_if.h`, `cudbg_lib_common.h`, and `cudbg_zlib.h`. It is invoked from `cudbg_lib.c` through `cudbg_do_compression()` when `cxgb4_cudbg.c` selected zlib compression.

## Risks
If the remaining output buffer is too small, zlib returns something other than `Z_STREAM_END` and the code reports `CUDBG_SYSTEM_ERROR`; there is no precomputed compressed bound. Errors before `zlib_deflateEnd()` can skip cleanup of zlib state. The code assumes the workspace pointer and size were allocated according to `cudbg_get_workspace_size()`.

## Test Signals
Exercise compression of empty, small, exactly chunk-sized, and multi-chunk entities; too-small output buffers; zlib unavailable path in caller; and decoder decompression using `compress_id`, `compress_size`, and `decompress_size`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_zlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_zlib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_zlib.h

## Purpose
This header defines the CUDBG zlib compression format constants, compression header layout, workspace sizing helper, and compression function prototype.

## Important APIs, Types, And Functions
- `CUDBG_ZLIB_COMPRESS_ID`, `CUDBG_ZLIB_WIN_BITS`, and `CUDBG_ZLIB_MEM_LVL` identify and parameterize zlib compression.
- `struct cudbg_compress_hdr` records compression ID, decompressed size, compressed size, and reserved space.
- `cudbg_get_workspace_size()` wraps `zlib_deflate_workspacesize()`.
- `cudbg_compress_buff()` is implemented in `cudbg_zlib.c`.

## Control Flow
The inline helper computes workspace size for the configured zlib parameters. The rest of the header declares data used by compression flow in `cudbg_zlib.c` and allocation flow in `cxgb4_cudbg.c`.

## State And Persistence
The compression header is serialized before each compressed chunk. Workspace size is transient and used to allocate per-dump compression memory.

## Dependencies And Integration Points
It includes Linux `zlib.h` and is included by `cxgb4_cudbg.c`, `cudbg_lib.c`, and `cudbg_zlib.c`. Dump decoders need to recognize `CUDBG_ZLIB_COMPRESS_ID` and the header layout.

## Risks
Changing zlib parameters changes workspace requirements and may affect decoder expectations. The large reserved array in `struct cudbg_compress_hdr` is part of the serialized format and should not be casually resized.

## Test Signals
Compile tests with zlib enabled, workspace allocation tests, compressed dump decode tests, and compatibility checks for `struct cudbg_compress_hdr` size/field interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_zlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4.h

## Purpose
This is the central cxgb4 driver header. It defines adapter-wide constants, hardware/firmware parameter structures, port and queue state, filter specifications, helper inlines for register and netdev access, and prototypes shared across cxgb4 translation units.

## Important APIs, Types, And Functions
Key structures include `struct adapter_params`, `struct port_info`, `struct sge`, `struct sge_rspq`, `struct sge_fl`, `struct sge_txq`, `struct adapter`, `struct ch_filter_specification`, and `struct filter_entry`. Important helpers include `t4_read_reg()`, `t4_write_reg()`, `t4_read_reg64()`, `t4_write_reg64()`, `netdev2pinfo()`, `netdev2adap()`, `mk_adap_vers()`, `qtimer_val()`, mailbox wrappers, `hash_mac_addr()`, and feature tests such as `is_offload()`, `is_uld()`, and `is_ethofld()`. The prototype section exposes SGE, firmware, RSS, memory-window, filter, port, PTP, TC, ULD, thermal, and MAC-filter operations.

## Control Flow
The header has no main runtime flow, but its inlines directly perform MMIO and object translation. Register helpers wrap `readl`/`writel` and `readq`/`writeq`. Mailbox wrappers select sleeping or non-sleeping submission. Netdev helpers recover `port_info` and `adapter` from Linux network devices. Queue descriptor structures define how SGE allocation, interrupt handling, and CUDBG descriptor copying traverse rings.

## State And Persistence
`struct adapter` is the main persistent in-memory driver object for a PCI function. It owns MMIO bases, PCI/device pointers, mailbox identity, flags, hardware params, SGE queues/maps, netdev ports, CLIP/L2T/SMT tables, ULD handles, TID state, workqueues, mailbox logs, debugfs, PTP, TC offloads, HMA, SRQ, vmcore dump registration, thermal state, ethtool filters, and the ethtool dump descriptor. `struct port_info` persists per netdev port link/RSS/MAC/scheduler/mirror state.

## Dependencies And Integration Points
It integrates almost every cxgb4 source with Linux networking, PCI, interrupts, timers, PTP, crash dump, thermal, rhashtable, and Chelsio firmware/register APIs. Files in this work item use it for `struct adapter`, register helpers, mailbox helpers, CLIP table access, CUDBG collection, and queue descriptor layouts.

## Risks
Because this header is widely included, layout or prototype changes have broad blast radius. MMIO helpers assume valid mapped BARs and correct register offsets. Bit-field filter structures are host shadow copies and must not be treated as firmware layout. `struct adapter` has many cross-subsystem locks and lifecycle-owned pointers, so dumps and offload paths must respect initialization and teardown ordering.

## Test Signals
Full-driver build matrix across optional configs, sparse/lockdep for MMIO and locking use, probe/remove tests, netdev open/close, SGE queue allocation, firmware mailbox tests, offload registration, filter programming, PTP/thermal/debugfs paths, and CUDBG dump collection all exercise contracts from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_cudbg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_cudbg.c

## Purpose
This file is the cxgb4 integration layer for CUDBG collection. It selects which CUDBG entities belong to hardware, memory, and flash dumps; computes dump lengths; initializes CUDBG headers; runs collectors; enables optional compression; and registers vmcore device dumps.

## Important APIs, Types, And Functions
- `cxgb4_collect_hw_dump`, `cxgb4_collect_mem_dump`, and `cxgb4_collect_flash_dump` map entity IDs to collector callbacks.
- `cxgb4_get_dump_length()` sums entity lengths and caps large compressed dumps to `CUDBG_DUMP_BUFF_SIZE`.
- `cxgb4_cudbg_collect_entity()` iterates entity arrays, fills entity headers, invokes collectors, aligns buffers, and records errors/warnings.
- `cxgb4_cudbg_collect()` builds the top-level CUDBG header and performs selected HW/MEM/FLASH collection.
- `cxgb4_init_ethtool_dump()` initializes `adapter->eth_dump`.
- `cxgb4_cudbg_vmcore_add_dump()` registers a crash dump callback.

## Control Flow
Collection starts with caller-supplied buffer size and flags. The function writes `cudbg_hdr`, validates minimum space for all entity headers, probes zlib workspace availability, allocates compression buffers when possible, then advances the data offset past the header table. Each selected group is collected in order. Per-entity failures reset the data offset to the entity start and preserve failure status in the entity header, allowing later entities to continue.

## State And Persistence
Persistent driver state touched here is `adapter->eth_dump` and `adapter->vmcoredd`. Dump contents persist in the caller-provided buffer. Compression scratch state is allocated per collection and freed before return. Entity errors are persisted in `cudbg_entity_hdr`.

## Dependencies And Integration Points
It depends on `t4_regs.h`, `cxgb4.h`, `cxgb4_cudbg.h`, and `cudbg_zlib.h`. It integrates with ethtool dump operations through `eth_dump` fields and with kdump/vmcore through `vmcore_add_device_dump()`.

## Risks
`cudbg_free_compress_buff()` is called unconditionally even when compression allocation was skipped; `vfree(NULL)` is safe, but any future allocator change must preserve that. Buffer length estimates must match collector behavior, especially when compression caps output. Continuing after entity failure is intentional, but consumers must inspect per-entity `hdr_flags`, `sys_err`, and `sys_warn`.

## Test Signals
Collect dumps for each flag combination, with too-small buffers, zlib allocation failure, collector failure injection, and vmcore registration. Verify header versions, entity offsets/sizes/padding, compressed versus uncompressed final `buf_size`, and ethtool `eth_dump` initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_cudbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_cudbg.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_cudbg.h

## Purpose
This header defines cxgb4-specific CUDBG glue: dump buffer sizes, callback type, entity/callback mapping structure, ethtool dump flag bits, and public cxgb4 CUDBG entry points.

## Important APIs, Types, And Functions
- `CUDBG_DUMP_BUFF_SIZE` is the 32 MB capped dump buffer used for compressed and vmcore scenarios.
- `CUDBG_COMPRESS_BUFF_SIZE` is the 4 MB reusable input buffer for compression.
- `cudbg_collect_callback_t` is the collector callback signature.
- `struct cxgb4_collect_entity` pairs `enum cudbg_dbg_entity_type` with a collector callback.
- `enum CXGB4_ETHTOOL_DUMP_FLAGS` defines memory, hardware, flash, and all-dump selections.
- Prototypes expose dump length, collection, ethtool initialization, and vmcore registration.

## Control Flow
The header has no executable flow. Its types are consumed by `cxgb4_cudbg.c` to build static entity arrays and dispatch collectors.

## State And Persistence
No state is stored here. The constants determine allocation sizes and serialized dump availability. Flags persist in `adapter->eth_dump.flag` when ethtool dump configuration is stored.

## Dependencies And Integration Points
It includes CUDBG interface/common/entity/library headers and depends on Linux ethtool dump flag definitions through cxgb4 include context. It is the boundary between generic CUDBG collector code and cxgb4 ethtool/vmcore integration.

## Risks
Changing buffer constants affects memory pressure and truncation behavior. Adding a new dump flag requires matching length and collection logic. The `CXGB4_ETH_DUMP_ALL` macro excludes flash by design, so callers expecting full flash data must request `CXGB4_ETH_DUMP_FLASH` separately.

## Test Signals
Compile tests, dump flag combination tests, memory allocation behavior around 32 MB/4 MB limits, and vmcore dump sizing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_cudbg.h -->
