# subset-b-004336 research

Grouped research for the requested Airoha, Alacritech, Allwinner, and Altera Ethernet driver files. Each section preserves the source path in its title and is wrapped for reconciliation into per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_eth.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_eth.h

## Purpose
`airoha_eth.h` is the shared internal interface for the Airoha Ethernet driver family. It defines QDMA ring sizing, GDM port constants, PPE flow-table geometry, hardware-offload table layouts, runtime device structures, MMIO helper wrappers, and exported cross-file entry points used by the main Ethernet, NPU, PPE, and debugfs code.

## Important APIs, types, and constants
- `AIROHA_MAX_*`, `TX_DSCP_NUM`, `RX_DSCP_NUM()`, `PPE_*_NUM_ENTRIES`, and `PPE_ENTRY_SIZE` define queue, descriptor, MTU, and hardware offload table dimensions.
- `struct airoha_queue`, `struct airoha_tx_irq_queue`, and `struct airoha_qdma` model TX/RX descriptor rings, interrupt completion queues, NAPI state, page-pool RX buffers, and per-QDMA MMIO state.
- `struct airoha_gdm_port` links a netdev to a QDMA, hardware GDM id, stats, QoS channel bitmap, DSA metadata, and CPU/forwarded TX counters.
- `struct airoha_foe_entry` and related `airoha_foe_*` structs encode the PPE forwarding/offload entry formats for bridge, IPv4, DS-Lite, and IPv6 routes. Bitfields such as `AIROHA_FOE_IB1_BIND_*` and `AIROHA_FOE_IB2_*` define hardware control words.
- `struct airoha_flow_table_entry` is the software shadow for offloaded flows, with rhashtable nodes, L2 subflow lists, stats, cookie, hash, type, and embedded FOE entry.
- `struct airoha_ppe`, `struct airoha_eth_soc_data`, and `struct airoha_eth` are the central device objects spanning FE registers, QDMA blocks, PPE state, NPU RCU pointer, resets, ports, and SoC-specific callbacks.
- MMIO helpers `airoha_rr()`, `airoha_wr()`, `airoha_rmw()` and wrappers such as `airoha_fe_rr()` and `airoha_qdma_wr()` standardize register access.
- Exported prototypes include PPE lifecycle/offload functions (`airoha_ppe_init()`, `airoha_ppe_deinit()`, `airoha_ppe_setup_tc_block_cb()`), flow-entry helpers, and optional debugfs initialization.

## Control flow and integration
This header is not executable by itself. It establishes the contracts used by `airoha_ppe.c`, `airoha_npu.c`, debugfs, and the Ethernet datapath. The main driver allocates `struct airoha_eth`, populates SoC data and ports, initializes QDMA/GDM state, then calls into PPE helpers using the declared APIs. PPE code uses the FOE layout definitions to translate tc/netfilter flow rules into hardware table entries. NPU and WLAN offload users reach the PPE through `struct airoha_ppe_dev`.

## State and persistence behavior
All state described here is volatile kernel runtime state: rings, NAPI, rhashtables, DMA buffers, stats, and RCU-managed NPU pointers. The header defines no persistent on-disk or firmware state. Hardware state persists only until reset/power-cycle and is represented through MMIO register writes elsewhere.

## Dependencies and integration points
The header depends on Linux networking, DSA, debugfs, page-pool/NAPI patterns, reset controls, and `linux/soc/airoha/airoha_offload.h`. It is tightly coupled to `airoha_regs.h` and to the PPE/NPU implementation files. DSA support and debugfs are conditional through kernel configuration.

## Risks and edge cases
The FOE structs are hardware ABI layouts; packing, field order, endian conversions, or `PPE_ENTRY_SIZE` changes can break offload silently. Queue sizes and descriptor-count macros must remain consistent with hardware limits. RCU access to `eth->npu`, spinlocks around queue/flow state, and stats synchronization are core correctness points. SoC version helpers currently encode specific EN7581/EN7583 behavior.

## Test signals
Useful validation includes compile coverage with Airoha Ethernet/PPE/NPU configs, boot/probe on EN7581/EN7583, QDMA RX/TX traffic, DSA port traffic, flowtable offload add/delete/stats, debugfs entry dumps, lockdep/RCU checks, and ethtool/netdev stats stability under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_eth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_npu.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_npu.c

## Purpose
`airoha_npu.c` is the platform driver for Airoha Network Processor Unit firmware. It loads RV32/data firmware into reserved memory/MMIO SRAM, boots NPU cores, services mailbox and watchdog interrupts, and exposes NPU-backed PPE and WLAN offload operations to Ethernet and wireless consumers.

## Important APIs and functions
- `airoha_npu_probe()` maps the NPU register space, creates a regmap, resolves reserved memory and IRQs, initializes operation callbacks, loads/starts firmware, boots cores, queries firmware version, and stores driver data.
- `airoha_npu_run_firmware()` loads either `firmware-name` entries from devicetree or SoC-default firmware names into reserved memory and local SRAM.
- `airoha_npu_send_msg()` is the central mailbox path. It DMA-maps a request object, writes mailbox buffer address/size/doorbell fields, waits for `MBOX_MSG_DONE`, checks status, and unmaps the buffer.
- PPE operations include `airoha_npu_ppe_init()`, `airoha_npu_ppe_deinit()`, `airoha_npu_ppe_flush_sram_entries()`, `airoha_npu_foe_commit_entry()`, and `airoha_npu_ppe_stats_setup()`.
- WLAN operations include `airoha_npu_wlan_msg_send()`, `airoha_npu_wlan_msg_get()`, `airoha_npu_wlan_init_memory()`, queue-address helpers, and IRQ status/mask helpers.
- `airoha_npu_get()` and `airoha_npu_put()` are exported supplier lookup/module-reference helpers used by consumers through an `airoha,npu` phandle.
- IRQ paths: `airoha_npu_mbox_handler()` acknowledges firmware mailbox interrupts; `airoha_npu_wdt_handler()` schedules `airoha_npu_wdt_work()`, which emits a small devcoredump with PC/SP/LR.

## Control flow
Probe first maps hardware and installs callback function pointers into `npu->ops`. It then requests one mailbox IRQ, per-core watchdog IRQs, and stores WLAN IRQ numbers. Firmware loading validates sizes, writes images, programs NPU MIB/boot registers, sets all boot bases to reserved memory start, and triggers cores. Consumers later call `airoha_npu_get()`, which resolves the phandle platform device, pins the module, and creates a device link. PPE or WLAN requests are packaged as mailbox payloads and synchronously sent to core 0.

## State and persistence behavior
The driver owns volatile firmware images in device memory, a regmap, per-core locks/work items, cached WLAN IRQ numbers, and an optional `npu->stats` IO mapping returned by firmware for PPE stats. It persists no host-side data across reload. Reserved-memory names such as `tx-bufid`, `pkt`, `tx-pkt`, and optional `ba` are used to pass physical addresses to firmware.

## Dependencies and integration points
This file depends on platform/OF infrastructure, firmware loading, reserved-memory APIs, regmap MMIO, DMA mapping, devcoredump, and `airoha_offload` NPU/PPE/WLAN contracts. It is a supplier for Airoha Ethernet PPE setup and likely WLAN drivers. Firmware files are declared through `MODULE_FIRMWARE`.

## Risks and edge cases
`airoha_npu_send_msg()` uses a fixed core index marked `FIXME`, so multicore mailbox routing is not generalized. It waits up to 100 seconds in an atomic poll while holding a spinlock, which makes firmware stalls high impact. Firmware names and reserved-memory regions are mandatory unless devicetree overrides are complete. `airoha_npu_get()` must balance module/device references through `airoha_npu_put()`. Watchdog coredumps are intentionally small and may not capture enough state for deep firmware failures.

## Test signals
Probe should log firmware version when `WLAN_FUNC_GET_WAIT_NPU_VERSION` succeeds. Tests should cover missing firmware returning probe defer, reserved-memory lookup failures, mailbox timeout/error status, PPE init/deinit, PPE stats setup, WLAN reserved-memory setup, watchdog interrupt coredump generation, module reference balancing, and consumer device-link behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_npu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_ppe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_ppe.c

## Purpose
`airoha_ppe.c` implements Airoha Packet Processing Engine flow offload. It allocates hardware forwarding-entry memory, initializes PPE register tables, translates tc/netfilter flow rules into FOE entries, commits entries to SRAM/DRAM through MMIO/NPU cooperation, tracks software flow state, exposes stats, and coordinates PPE startup/shutdown with the NPU.

## Important APIs, types, and functions
- `airoha_ppe_init()` allocates `struct airoha_ppe`, coherent FOE memory, optional stats memory, flow hash arrays, check-time arrays, initializes rhashtables, flushes SRAM entries, and creates debugfs.
- `airoha_ppe_deinit()` detaches the NPU under `flow_offload_mutex`, calls firmware deinit, drops references, destroys rhashtables, and removes debugfs.
- `airoha_ppe_setup_tc_block_cb()` gates flow offload until all netdevs are registered, lazy-initializes NPU/PPE offload, and dispatches flow commands.
- `airoha_ppe_flow_offload_replace()`, `destroy()`, and `stats()` implement `FLOW_CLS_REPLACE`, `FLOW_CLS_DESTROY`, and `FLOW_CLS_STATS`.
- `airoha_ppe_foe_entry_prepare()` builds common FOE metadata for bridge, IPv4, and IPv6 flows, including VLAN/PPPoE, DSA, WDMA, PSE port, NBQ, QoS, multicast, and source MAC id handling.
- `airoha_ppe_foe_entry_set_ipv4_tuple()` and `set_ipv6_tuple()` populate hardware tuple fields from dissector keys and mangle actions.
- `airoha_ppe_foe_get_entry_hash()`, `commit_entry()`, `commit_sram_entry()`, and `get_entry()` manage hardware hash calculation and SRAM/DRAM interaction.
- `airoha_ppe_check_skb()` is the packet-path hook that rate-limits checks by hash and lazily commits matching software flows when hardware exposes a candidate PPE hash.
- `airoha_ppe_foe_entry_get_stats()` combines software high-word stats with NPU-mapped low-word counters.

## Control flow
Initialization creates the software/hardware backing state but defers NPU-backed PPE enablement until the first offload request. A replace command validates supported flower keys/actions, derives the offload type, builds a FOE entry, applies mangle data, inserts the software shadow into either the L4 hash bucket or L2 rhashtable, and then inserts the cookie into `eth->flow_table`. Packets later call `airoha_ppe_check_skb()` with a hardware hash; the PPE reads the FOE entry at that hash, compares it to software candidates, commits the prepared entry if matched, or builds L2 subflows from bridge rules. Destroy invalidates hardware state if a hash was committed and removes all related software nodes. Stats read idle time from hardware timestamps and flow counters from the NPU stats mapping.

## State and persistence behavior
State is volatile and split across coherent FOE memory, hardware SRAM/DRAM tables, NPU stat memory, `eth->flow_table`, `ppe->l2_flows`, per-hash `foe_flow` hlist buckets, and `foe_check_time` debounce bytes. The active NPU pointer is RCU-managed in `eth->npu`. `flow_offload_mutex` serializes setup/commands/deinit; `ppe_lock` protects FOE table and flow-list mutation.

## Dependencies and integration points
The file depends on flow dissector/classifier APIs, netfilter flowtable offload via flower commands, DSA, WDMA forward-path metadata, Airoha NPU firmware ops, FE/PPE registers from `airoha_regs.h`, and `airoha_offload` device export. `airoha_ppe_get_dev()` exports the PPE device by `airoha,eth` phandle for external consumers.

## Risks and edge cases
Unsupported flow keys/actions return `-EOPNOTSUPP`; bridge, IPv4 NAT, and IPv6 5-tuple paths have different hardware layouts. Hash collisions are handled by software candidate lists, but stale hardware entries can cause invalidation paths. The code contains a likely important limitation: SRAM flushing without NPU falls back to MMIO one entry at a time. Flow stats are disabled for EN7583 and when `CONFIG_NET_AIROHA_FLOW_STATS` is off. Correctness depends on RCU pointer lifetime, spinlock ordering, memory barriers before hardware commits, and endian/field preparation matching hardware ABI.

## Test signals
Exercise flowtable offload replace/destroy/stats for bridge, IPv4 NAT, IPv6 route, VLAN push/pop, PPPoE push, DSA, and WDMA paths. Validate that offload is rejected before all netdevs are registered, unsupported dissector/action combinations return expected errors, debugfs entries reflect committed state, stats monotonically increase, idle timestamps update, lockdep stays clean, and teardown removes NPU references and debugfs without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_ppe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_ppe_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_ppe_debugfs.c

## Purpose
`airoha_ppe_debugfs.c` exposes read-only debugfs views of Airoha PPE forwarding entries. It formats all non-empty entries and a bind-only subset for manual inspection of hardware offload state.

## Important APIs and functions
- `airoha_ppe_debugfs_init()` creates `/sys/kernel/debug/ppe/entries` and `/sys/kernel/debug/ppe/bind` and stores the directory dentry in `ppe->debugfs_dir`.
- `airoha_ppe_debugfs_foe_show()` iterates `airoha_ppe_get_total_num_entries()`, fetches each entry with `airoha_ppe_foe_get_entry()`, decodes state/type, prints original and translated tuples, L2 metadata, VLANs, IB words, and packet/byte stats.
- `airoha_debugfs_ppe_print_tuple()` prints IPv4/IPv6 address and optional port pairs, converting the stored CPU-order IPv6 words back to network-order display form.
- `DEFINE_SHOW_ATTRIBUTE` creates file operations for both all-entry and bind-only views.

## Control flow
Opening either debugfs file invokes the seq-file show callback. The show code skips missing entries, invalid state, and non-bind state when requested. It selects tuple/L2 fields based on FOE packet type and calls `airoha_ppe_foe_entry_get_stats()` to include counter values.

## State and persistence behavior
The file owns only the debugfs dentry pointer stored in `struct airoha_ppe`; the displayed state comes from live PPE FOE memory/hardware and NPU stats. Removing the PPE calls `debugfs_remove()` in `airoha_ppe_deinit()`.

## Dependencies and integration points
It depends on debugfs/seq-file helpers and the PPE API declared in `airoha_eth.h`. It is conditionally compiled by `CONFIG_DEBUG_FS`; otherwise the header provides a no-op initializer.

## Risks and edge cases
The dump iterates the full PPE entry count, which can be large, and each SRAM entry read may involve MMIO polling. Output is diagnostic only and has no locking beyond what `airoha_ppe_foe_get_entry()` provides. Formatting assumes FOE type-specific layouts are valid for nonzero state; corrupted hardware entries may produce confusing tuple or MAC output.

## Test signals
With debugfs enabled, verify `entries` shows non-invalid offloads, `bind` filters to bound entries, IPv4/IPv6 and VLAN fields decode as expected, stats match flow offload counters, and removing the driver removes the debugfs directory without stale dentries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_ppe_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_regs.h

## Purpose
`airoha_regs.h` is the Airoha Ethernet hardware register map. It defines FE, PSE, CDM, GDM, PPE, QDMA, QoS, trTCM, descriptor, and interrupt register offsets plus bit masks used by the Airoha Ethernet/PPE datapath.

## Important APIs, types, and constants
- Base-address macros (`PSE_BASE`, `CDM*_BASE`, `GDM*_BASE`, `PPE*_BASE`) and selector macros (`CDM_BASE()`, `GDM_BASE()`) encode per-block register layout.
- FE/GDM/PSE macros configure forwarding, ingress, length, loopback, VIP ports, WAN ports, multicast VLAN tables, PSE buffer reservations, and GDM MIB counters.
- PPE macros define global enable, flow configuration, protocol checks, table base/sizing, bind rates/limits, aging, hash seed, default CPU ports, MTU, SRAM RAM access, and update-memory registers.
- QDMA macros define global DMA enable/reset, interrupt status/enable banks, TX/RX ring registers, IRQ rings, descriptor count/low-threshold controls, QoS/trTCM registers, and congestion settings.
- `struct airoha_qdma_desc` and `struct airoha_qdma_fwd_desc` define the on-memory hardware descriptor layouts and message/control fields.

## Control flow and integration
The header has no runtime control flow. Driver code uses these macros with `airoha_fe_rr/wr/rmw()` and `airoha_qdma_rr/wr/rmw()` to initialize hardware, set up queues, enable interrupts, program PPE tables, collect stats, and fill/parse QDMA descriptors.

## State and persistence behavior
All named state is hardware register or DMA descriptor state. Register state is volatile and reset by device reset/power-management paths. Descriptor structs represent DMA-visible memory shared between CPU and QDMA hardware.

## Dependencies and integration points
The header depends only on Linux types and common bit macros. It is included by Airoha implementation files, especially `airoha_ppe.c`, and must remain consistent with hardware documentation and the descriptor layouts declared in `airoha_eth.h`.

## Risks and edge cases
Register macros are hardware ABI. Incorrect offsets, masks, or shift assumptions can break traffic, offload, interrupts, or stats with little compile-time signal. Some macros encode split register spaces for low/high RX/TX rings and interrupt banks; off-by-one errors can target the wrong register block. Descriptor fields mix CPU and little-endian storage, so callers must preserve correct conversions.

## Test signals
Compile all Airoha users, boot on supported SoCs, validate DMA reset/enable, RX/TX rings, interrupt masking/unmasking, QDMA descriptor ownership, GDM MIB counters, PPE table programming, SRAM read/write polling, and QoS/trTCM programming under real traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/Kconfig

## Purpose
This Kconfig file defines the Alacritech Ethernet vendor menu and the `SLICOSS` driver option for Alacritech SLIC-based Gigabit adapters.

## Important configuration
- `NET_VENDOR_ALACRITECH` is a boolean vendor gate, defaulting to `y`, that controls visibility of Alacritech device options.
- `SLICOSS` is a tristate driver option depending on `PCI` and selecting `CRC32`. Its help text documents Mojave and Oasis copper/fiber cards and the `slicoss` module name.

## Control flow and integration
Kconfig selection controls whether `drivers/net/ethernet/alacritech/Makefile` builds `slicoss.o`. Selecting `SLICOSS=m` builds a loadable module; selecting `y` builds it into the kernel.

## State and persistence behavior
There is no runtime state in this file. It persists only the build-time configuration decisions.

## Dependencies and integration points
The file integrates into the kernel networking driver Kconfig tree. It exposes the SLIC driver only under the vendor gate and pulls in CRC32 for multicast hash filtering in the driver.

## Risks and edge cases
Because the vendor gate defaults to enabled, distribution configs will usually show the SLIC option. Missing `PCI` prevents the driver from being selectable. CRC32 is selected rather than depended on, so it is automatically available when the driver is enabled.

## Test signals
Validate `CONFIG_NET_VENDOR_ALACRITECH=n` hides `SLICOSS`, `CONFIG_SLICOSS=m` produces `slicoss.ko`, and built-in/module builds include CRC32 support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/Makefile

## Purpose
The Makefile wires the Alacritech SLIC driver into kbuild.

## Important build rules
- `obj-$(CONFIG_SLICOSS) += slicoss.o` builds `slicoss.c` as the module or built-in object selected by Kconfig.

## Control flow and integration
kbuild evaluates `CONFIG_SLICOSS` and includes or omits the driver object accordingly. There are no composite objects or generated files in this directory.

## State and persistence behavior
No runtime state exists. The file affects build artifacts only.

## Dependencies and integration points
It depends on `Kconfig` for `CONFIG_SLICOSS` and on `slicoss.c`/`slic.h` for the actual driver source.

## Risks and edge cases
The rule is intentionally minimal. Renaming the C file or config symbol requires updating this line or the driver will silently disappear from builds.

## Test signals
Build with `CONFIG_SLICOSS=y` and `m`, confirm `slicoss.o` or `slicoss.ko` is produced, and verify `CONFIG_SLICOSS=n` omits it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/slic.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/slic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/slicoss.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/slicoss.c

## Purpose
`slicoss.c` is the non-accelerated Linux PCI netdev driver for Alacritech SLIC Mojave/Oasis Gigabit Ethernet adapters. It handles firmware loading, EEPROM MAC discovery, PCI probe/remove, netdev open/stop, TX/RX DMA queues, NAPI interrupt processing, link status UPRs, multicast filtering, and ethtool/netdev stats.

## Important APIs and functions
- PCI/netdev lifecycle: `slic_probe()`, `slic_remove()`, `slic_init()`, `slic_open()`, and `slic_close()`.
- Firmware paths: `slic_load_firmware()` downloads main card microcode sections and validates firmware structure; `slic_load_rcvseq_firmware()` downloads receive sequencer firmware.
- EEPROM path: `slic_read_eeprom()` uses a temporary shared-memory/UPR setup, validates magic/checksum via `slic_eeprom_valid()`, and sets the netdev MAC.
- DMA queue setup: `slic_init_rx_queue()`, `slic_init_tx_queue()`, `slic_init_stat_queue()` allocate RX buffers, TX descriptor pool entries, and status descriptor arrays; corresponding free functions undo mappings and buffers.
- Datapath: `slic_xmit()` maps an SKB head and posts a TX command buffer; `slic_xmit_complete()` consumes status completions; `slic_handle_receive()` validates RX descriptors, handles errors, and passes packets through GRO.
- Interrupt/NAPI: `slic_irq()` masks interrupts and schedules NAPI; `slic_poll()` dispatches shared-memory ISR bits and reenables interrupts; `slic_handle_irq()` fans out RX, TX, UPR, link, and error paths.
- Link and filtering: `slic_set_link_autoneg()`, `slic_handle_link_irq()`, `slic_configure_link*()`, `slic_set_rx_mode()`, and `slic_set_mac_address()`.

## Control flow
Probe enables PCI, configures DMA mask/regions, allocates a netdev, maps registers, initializes hardware enough to load firmware and read EEPROM, then registers the netdev. Opening resets/reloads firmware, initializes RX/TX/status/shared-memory state, enables NAPI, programs ISP/interrupt aggregation/MAC/filter/link autoneg, requests IRQ, enables interrupts, and queues an initial link-status UPR. Interrupts write-mask the card, inspect shared-memory ISR, and schedule NAPI. NAPI handles RX frames until budget, TX completions through status descriptors, link events through UPRs, and error counters, then reenables interrupts. Close stops queue/carrier, disables NAPI/interrupts, powers down PHY/MAC, clears UPRs, frees all DMA resources, and resets the card.

## State and persistence behavior
Runtime state includes TX/RX/status queues, coherent shared memory for ISR/link, firmware-loaded card microcode, UPR list state, stats, NAPI, link speed/duplex, and multicast/promiscuous settings. EEPROM stores persistent MAC/FRU/card configuration but is read only. Firmware must be available at each initialization path because open reloads the card.

## Dependencies and integration points
The driver depends on PCI, firmware loader, DMA API, NAPI/netdev, ethtool, MII definitions, CRC32 multicast hashing, and SLIC hardware register/descriptor definitions from `slic.h`. It exposes standard netdev ops and ethtool stats.

## Risks and edge cases
The driver maps only `skb_headlen()` for TX, so fragmented SKBs rely on upper layers/features not advertising scatter-gather. Firmware parsing has multiple sanity checks but malformed firmware can still exercise complex section loops. RX buffers combine a hardware descriptor immediately before packet data and require 256-byte DMA alignment. UPR retries on errors can reorder expectations if link/config requests stack up. Interrupt handling relies on shared-memory ISR visibility and memory barriers. Open/close reload and free all volatile resources, so error unwinds must stay exact.

## Test signals
Test PCI probe/remove for Mojave and Oasis IDs, firmware missing/invalid paths, EEPROM checksum failure and MAC selection, open/close cycles, link up/down/autoneg for copper/fiber, multicast/promiscuous filter programming, RX error counters, TX completion wakeups, NAPI budget handling, IRQ sharing/spurious IRQ, ethtool stats, and DMA API debug on allocation/unmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/slicoss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/Kconfig

## Purpose
This Kconfig file defines the Allwinner Ethernet vendor menu and the `SUN4I_EMAC` option for the Allwinner A10 EMAC driver.

## Important configuration
- `NET_VENDOR_ALLWINNER` is a boolean vendor gate, defaulting to `y`, depending on `ARCH_SUNXI`.
- `SUN4I_EMAC` is a tristate depending on `ARCH_SUNXI` and `OF`, selecting `CRC32`, `MII`, `PHYLIB`, and `MDIO_SUN4I`.

## Control flow and integration
When `SUN4I_EMAC` is enabled, kbuild includes `sun4i-emac.o` through the directory Makefile. The selected libraries provide PHY/MDIO and multicast hash support for the platform driver.

## State and persistence behavior
No runtime state exists here. The file controls build-time availability.

## Dependencies and integration points
It integrates into the networking Ethernet driver Kconfig tree and restricts visibility to SUNXI/OF platforms.

## Risks and edge cases
The `ARCH_SUNXI` dependency means cross-architecture compile testing needs config overrides or SUNXI builds. Selecting `MDIO_SUN4I` assumes the EMAC driver uses the matching MDIO bus provider in devicetree systems.

## Test signals
Verify config visibility under SUNXI/OF, module and built-in builds for `SUN4I_EMAC`, and automatic selection of PHYLIB/MII/MDIO_SUN4I/CRC32.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/Makefile

## Purpose
The Makefile connects the Allwinner A10 EMAC driver to kbuild.

## Important build rules
- `obj-$(CONFIG_SUN4I_EMAC) += sun4i-emac.o` builds the platform driver when selected.

## Control flow and integration
kbuild includes the single driver object based on `CONFIG_SUN4I_EMAC`. There are no composite objects in this directory.

## State and persistence behavior
No runtime state exists. It only controls build outputs.

## Dependencies and integration points
The rule depends on the Kconfig symbol and the `sun4i-emac.c` source file.

## Risks and edge cases
Renaming the config or source requires updating this rule. Otherwise the file is intentionally low risk.

## Test signals
Build with `SUN4I_EMAC=y`, `m`, and `n` and confirm the expected object/module inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/sun4i-emac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/sun4i-emac.c

## Purpose
`sun4i-emac.c` implements the Allwinner A10 Fast Ethernet MAC platform driver. It maps EMAC registers, claims clock/SRAM resources, attaches to a devicetree PHY, performs FIFO-based TX, RX through programmed I/O or optional DMAengine, handles interrupts, and exposes standard netdev/ethtool operations.

## Important APIs and functions
- Probe/remove/PM: `emac_probe()`, `emac_remove()`, `emac_suspend()`, and `emac_resume()`.
- Netdev lifecycle: `emac_open()`, `emac_stop()`, `emac_shutdown()`, `emac_init_device()`, and `emac_timeout()`.
- PHY integration: `emac_mdio_probe()`, `emac_mdio_remove()`, and `emac_handle_link_change()` use phylib and update MAC speed/duplex registers.
- Datapath: `emac_start_xmit()` writes packets into TX FIFO channel 0/1; `emac_tx_done()` clears FIFO state and wakes the queue; `emac_rx()` validates RX FIFO headers/status and passes SKBs to the stack.
- DMA helpers: `emac_configure_dma()`, `emac_dma_inblk_32bit()`, and `emac_dma_done_callback()` optionally use a DMAengine `rx` channel for large RX copies.
- Filtering/setup: `emac_setup()`, `emac_powerup()`, `emac_set_rx_mode()`, and `emac_set_mac_address()` configure MAC registers, frame length, flow control, RX acceptance, and MAC address.
- IRQ/netpoll: `emac_interrupt()` masks/clears/re-enables interrupts and dispatches RX/TX/abort handling; `emac_poll_controller()` supports netpoll when configured.

## Control flow
Probe allocates a netdev, maps MMIO from OF, maps the IRQ, optionally configures RX DMA, enables the clock, claims SUNXI SRAM, resolves a PHY phandle, reads or randomizes the MAC address, powers/resets hardware, installs netdev ops, and registers the device. Open requests the IRQ, resets/init hardware, connects/starts the PHY, and starts the TX queue. TX selects one of two hardware FIFO channels and stops the queue when both are occupied. RX loops while FIFO byte count is nonzero, checks an undocumented magic header, validates packet status/length, allocates SKBs, optionally starts DMA for large frames, otherwise reads through `readsl()`, and calls `netif_rx()`. Stop tears down PHY, shuts down MAC/interrupts, and frees IRQ.

## State and persistence behavior
Runtime state lives in `struct emac_board_info`: clock, MMIO, lock, netdev, TX FIFO bitmap, RX DMA channel, PHY node/interface, link/speed/duplex, and RX completion flag. The driver does not persist host data; MAC address comes from devicetree or is randomized. Hardware register state is reinitialized across probe/open/resume.

## Dependencies and integration points
The driver depends on OF platform resources, phylib, SUNXI SRAM claiming, clocks, DMAengine, IRQ/netpoll, and the register definitions in `sun4i-emac.h`. Kconfig selects `MDIO_SUN4I`, but this file attaches to an existing PHY node with `of_phy_connect()`.

## Risks and edge cases
The RX path uses a legacy `emacrx_completed_flag` to avoid overlapping RX/DMA processing. DMA RX falls back to programmed I/O if setup or transfer fails. RX length/status handling subtracts CRC (`rxlen - 4`) for SKB payload but stats add full RX length. The interrupt handler masks all interrupts under a spinlock and directly calls RX, so long RX bursts can increase IRQ latency. Suspend/resume reinitializes hardware without explicitly reattaching PHY state. Probe error paths must release SRAM, clock, IRQ mapping, DMA channel, and MMIO in correct order.

## Test signals
Test OF probe with valid/missing PHY and MAC address, clock/SRAM failures, optional DMA channel present/absent, link speed/duplex changes, TX FIFO saturation and wakeup, RX good/error frames, invalid magic FIFO flush path, netpoll, suspend/resume, and DMAengine fallback/error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/sun4i-emac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/sun4i-emac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/sun4i-emac.h

## Purpose
`sun4i-emac.h` defines the Allwinner A10 EMAC register offsets and bitfields used by `sun4i-emac.c`.

## Important APIs, types, and constants
- Register offsets cover controller control, TX mode/flow/control/FIFO/status, RX control/hash/status/FIFO/count, interrupts, MAC control/timing/frame length, MII clock, MAC address, and source-address filters.
- Bitfields define reset/TX/RX enable, DMA enable, RX acceptance/filter modes, interrupt enable/status bits, MAC duplex/CRC/padding/flow control, 100M speed selection, and MII clock divider.
- Helper macros `EMAC_RX_IO_DATA_LEN()` and `EMAC_RX_IO_DATA_STATUS()` extract RX FIFO header fields.
- `EMAC_EEPROM_MAGIC` and `EMAC_UNDOCUMENTED_MAGIC` document magic values used by legacy hardware/FIFO handling.

## Control flow and integration
The header has no executable control flow. The platform driver uses these constants for MMIO reads/writes in setup, TX, RX, IRQ, link updates, and power management.

## State and persistence behavior
All state is hardware register state and volatile FIFO/header data. The header itself stores no runtime state.

## Dependencies and integration points
It is a private companion to `sun4i-emac.c` and has no external dependencies beyond basic C preprocessing.

## Risks and edge cases
Incorrect register offsets or bit definitions affect hardware directly. The undocumented magic value is central to the RX FIFO resynchronization path; changing it would break recovery from FIFO desynchronization. Frame-length and RX status masks must match hardware encoding.

## Test signals
Compile the driver, validate register programming during probe/open/link changes, confirm RX header decoding, exercise interrupt status bits, and test FIFO flush behavior when the magic header is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/allwinner/sun4i-emac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/Kconfig

## Purpose
This Kconfig file defines `ALTERA_TSE`, the Altera Triple-Speed Ethernet MAC driver option.

## Important configuration
- `ALTERA_TSE` is a tristate depending on `HAS_DMA` and `HAS_IOMEM`.
- It selects `PHYLIB`, `PHYLINK`, `PCS_LYNX`, `MDIO_REGMAP`, and `REGMAP_MMIO`, reflecting the MAC/PCS/MDIO stack used by the full driver.

## Control flow and integration
When enabled, the Altera Makefile builds the composite `altera_tse` object from main, ethtool, DMA, and utility sources. The same option covers both SGDMA and mSGDMA variants selected by devicetree match data at probe time.

## State and persistence behavior
No runtime state exists here. It controls driver availability at build time.

## Dependencies and integration points
The option integrates with the Ethernet driver menu and ensures the required phylink/PCS/regmap infrastructure is available.

## Risks and edge cases
Systems without DMA or IOMEM cannot select the driver. Because both DMA backends are compiled into one module, build errors in either backend break the single driver.

## Test signals
Check built-in and module builds, verify selected dependencies appear in generated configs, and confirm the composite object links with both DMA backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/Makefile

## Purpose
The Makefile builds the Altera Triple-Speed Ethernet driver and combines its component objects.

## Important build rules
- `obj-$(CONFIG_ALTERA_TSE) += altera_tse.o` selects the module/built-in target.
- `altera_tse-objs := altera_tse_main.o altera_tse_ethtool.o altera_msgdma.o altera_sgdma.o altera_utils.o` links the main driver, ethtool support, both DMA engines, and common utilities into one object.

## Control flow and integration
kbuild evaluates `CONFIG_ALTERA_TSE` and links all listed objects into `altera_tse`. Runtime DMA backend selection is handled by the full driver, not by separate build targets.

## State and persistence behavior
No runtime state exists. Build artifacts are the only effect.

## Dependencies and integration points
It depends on the Kconfig symbol and all listed source files. The DMA files researched here are integrated through this composite target.

## Risks and edge cases
Any source listed in `altera_tse-objs` must compile for every enabled `ALTERA_TSE` build, even if a platform only uses one DMA backend. Object list drift can break runtime match data or unresolved symbols.

## Test signals
Build `ALTERA_TSE=y` and `m`, confirm `altera_msgdma.o` and `altera_sgdma.o` are included, and verify `ALTERA_TSE=n` omits the composite object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdma.c

## Purpose
`altera_msgdma.c` implements the modular SGDMA backend for the Altera Triple-Speed Ethernet driver. It provides the `struct altera_dmaops` callbacks used by the main TSE driver to reset mSGDMA engines, control interrupts, post TX/RX descriptors, count TX completions, and read RX response status.

## Important APIs and functions
- `msgdma_initialize()`, `msgdma_uninitialize()`, and `msgdma_start_rxdma()` are no-op hooks because mSGDMA descriptor FIFOs do not need the SGDMA-style descriptor memory setup.
- `msgdma_reset()` resets RX and TX mSGDMA CSR blocks, polls the `RESETTING` status bit with `ALTERA_TSE_SW_RESET_WATCHDOG_CNTR`, warns on timeout, and clears status bits.
- `msgdma_enable_rxirq()`, `msgdma_disable_rxirq()`, `msgdma_enable_txirq()`, and `msgdma_disable_txirq()` manipulate the global interrupt bit in RX/TX CSR control registers.
- `msgdma_clear_rxirq()` and `msgdma_clear_txirq()` clear IRQ status bits.
- `msgdma_tx_buffer()` writes an extended descriptor into the TX descriptor port from a `tse_buffer` DMA address and length.
- `msgdma_tx_completions()` estimates completed TX descriptors from `rw_fill_level`, producer/consumer indexes, and busy status.
- `msgdma_add_rx_desc()` posts an RX descriptor to write into a receive buffer and request completion/error/early IRQs.
- `msgdma_rx_status()` reads response FIFO entries and returns `(status << 16) | length`.

## Control flow
The main TSE driver calls `init_dma()` during open, `reset_dma()` while starting/stopping, preposts RX buffers with `add_rx_desc()`, starts NAPI/IRQs, and calls `tx_buffer()` for SKB transmission. TX completion polling uses `tx_completions()` to advance `tx_cons`. RX NAPI calls `get_rx_status()` to learn whether a response is available and how many bytes/status bits were returned.

## State and persistence behavior
This backend stores no private state beyond fields in `struct altera_tse_private`: CSR/descriptor/response MMIO pointers and TX/RX producer/consumer counters owned by the main driver. mSGDMA hardware FIFOs and status registers are volatile.

## Dependencies and integration points
It depends on `altera_tse.h`, `altera_utils.h`, and `altera_msgdmahw.h` for private state, CSR accessors, bit definitions, and descriptor offsets. It is installed in `altera_tse_main.c` match data as the MSGDMA variant.

## Risks and edge cases
TX completion counting is derived from fill-level and busy bits, so off-by-one errors can leak or prematurely free TX buffers. Reset relies on finite polling and only warns on timeout after proceeding to clear status. RX status returns zero when no response FIFO entry exists, making zero-length/error encoding important. Descriptor writes go directly to MMIO ports and must preserve ordering expected by hardware.

## Test signals
Test mSGDMA reset timeout/warning paths, IRQ enable/disable/clear, TX posting and completion accounting under queue pressure, RX descriptor posting and response parsing, error response bits, and DMA mask behavior for 64-bit descriptor address fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdma.h

## Purpose
`altera_msgdma.h` declares the mSGDMA backend callback functions exported to the Altera TSE main driver.

## Important APIs
The declarations cover reset, IRQ enable/disable/clear, TX submission/completion, RX descriptor posting/status, initialization, uninitialization, and RX DMA start: `msgdma_reset()`, `msgdma_tx_buffer()`, `msgdma_tx_completions()`, `msgdma_add_rx_desc()`, `msgdma_rx_status()`, and related helpers.

## Control flow and integration
`altera_tse_main.c` binds these functions into a `struct altera_dmaops` instance for MSGDMA devicetree matches. The header provides prototypes only.

## State and persistence behavior
No state is stored in this header. All functions operate on `struct altera_tse_private` and hardware registers.

## Dependencies and integration points
It requires the forward-visible `struct altera_tse_private` and `struct tse_buffer` definitions from `altera_tse.h` in including translation units.

## Risks and edge cases
Prototype drift between this header, `altera_msgdma.c`, and the `altera_dmaops` function-pointer signature would break builds or runtime backend selection.

## Test signals
Compile the composite Altera TSE driver and verify all MSGDMA callbacks are assigned in match data without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdmahw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdmahw.h

## Purpose
`altera_msgdmahw.h` defines the mSGDMA hardware ABI used by the Altera TSE MSGDMA backend: extended descriptors, CSR registers, response registers, control/status bits, and offset helpers.

## Important APIs, types, and constants
- `struct msgdma_extended_desc` models the descriptor port fields: read/write address low/high, length, burst/sequence, stride, and control.
- Descriptor control macros define SOP/EOP generation, parking, end-on-EOP/length, completion/early/error IRQs, and `GO`.
- `MSGDMA_DESC_CTL_TX_SINGLE` and `MSGDMA_DESC_CTL_RX_SINGLE` are precomposed common controls.
- `struct msgdma_csr` maps status, control, fill-level, response fill-level, and sequence registers.
- CSR status/control masks define busy, FIFO empty/full, stopped/resetting/error/early states, IRQ, reset, stop, stop-on-error/early, global interrupt, and stop-descriptor controls.
- `struct msgdma_response` and response bits expose bytes transferred, status, early termination, and error mask.
- `msgdma_*offs()` macros provide `offsetof()` values for MMIO access helpers.

## Control flow and integration
The header has no executable flow. `altera_msgdma.c` uses it to write descriptors, reset/control engines, inspect fill levels, and parse RX responses.

## State and persistence behavior
All described state is volatile hardware state accessed through MMIO. Descriptors are written to hardware descriptor FIFO/ports rather than persistent memory.

## Dependencies and integration points
It depends on standard bit/offset macros and the utility `GET_BIT_VALUE` macro from the broader driver include context. It is private to the Altera TSE MSGDMA backend.

## Risks and edge cases
Bit definitions and structure layout must match mSGDMA IP. Since offsets derive from C structures, accidental type/field changes alter register programming. Error and early-termination bits must be propagated correctly to the main RX path.

## Test signals
Build with MSGDMA backend, validate descriptor writes on TX/RX, reset and IRQ status behavior, fill-level accounting, response FIFO parsing, and hardware error response propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_msgdmahw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdma.c

## Purpose
`altera_sgdma.c` implements the legacy SGDMA backend for the Altera Triple-Speed Ethernet driver. It maps descriptor memory for DMA, manages simple software TX/RX buffer lists, starts SGDMA read/write transactions, reports completions/status, and exposes the same DMAops contract as the MSGDMA backend.

## Important APIs and functions
- `sgdma_initialize()` sets SGDMA control defaults, initializes TX/RX pending lists, maps RX/TX descriptor memory, clears it with `memset_io()`, and syncs it for hardware.
- `sgdma_uninitialize()` unmaps descriptor memory.
- `sgdma_reset()` clears descriptor memory and toggles RX/TX SGDMA reset controls.
- IRQ hooks are mostly no-ops for enable/disable because SGDMA interrupts stay enabled after initial setup; `sgdma_clear_rxirq()` and `sgdma_clear_txirq()` set the clear-interrupt bit.
- `sgdma_tx_buffer()` waits for TX idle, builds a current/next descriptor pair, starts async write, and queues the buffer for completion.
- `sgdma_tx_completions()` returns one completion when TX is idle, the descriptor is no longer hardware-owned, and a queued TX buffer can be dequeued.
- `sgdma_add_rx_desc()` queues RX buffers; `sgdma_start_rxdma()` starts the first read; `sgdma_rx_status()` reads descriptor status/bytes on EOP, dequeues the RX buffer, clears CSR state, and restarts RX DMA.
- Private helpers handle descriptor setup, physical address calculation, async read/write, queue push/pop/peek, and busy polling.

## Control flow
The main TSE driver allocates descriptor regions, calls `sgdma_initialize()`, refills RX by calling `add_rx_desc()`, then calls `start_rxdma()`. `sgdma_async_read()` peeks the queued RX buffer, programs descriptor 0 with write address and descriptor 1 as terminator, syncs descriptor memory, writes `next_descrip`, and starts the RX controller. On RX EOP, `sgdma_rx_status()` syncs descriptor memory for CPU, extracts status/length, removes the buffer from the pending list, clears controller state, and kicks the next read. TX is single-buffer-at-a-time: `sgdma_tx_buffer()` programs descriptor 0 for the SKB DMA address and starts TX; completion is seen when hardware clears ownership and TX busy is false.

## State and persistence behavior
State is volatile and stored in `struct altera_tse_private`: descriptor virtual/MMIO pointers, descriptor bus addresses, mapped DMA addresses, control words, and `txlisthd`/`rxlisthd`. Hardware descriptor ownership bits and CSR busy/status bits drive progress. No persistent storage is used.

## Dependencies and integration points
It depends on the main TSE private state from `altera_tse.h`, list handling, DMA mapping/sync APIs, register access helpers from `altera_utils.h`, and SGDMA layout constants from `altera_sgdmahw.h`. It is selected by the SGDMA `struct altera_dmaops` in `altera_tse_main.c`.

## Risks and edge cases
This backend supports only one active TX and one active RX descriptor chain at a time despite the main driver ring abstraction. List operations assume the caller holds the appropriate main-driver lock. `sgdma_txbusy()` waits only about 100 microseconds before logging a timeout. Descriptor memory is mapped from an IO memory pointer, so DMA mapping/sync assumptions are sensitive to platform memory attributes. RX status zero after EOP is treated as a serious error and no packet is returned.

## Test signals
Test initialization/uninitialization with DMA API debug, TX busy timeout handling, single-packet TX completion, RX queue empty handling, RX EOP status/length/error propagation, interrupt clear behavior, reset clearing descriptors, and lockdep coverage around list operations in the main driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdma.h

## Purpose
`altera_sgdma.h` declares the SGDMA backend functions used by the Altera TSE main driver.

## Important APIs
The prototypes cover reset, IRQ enable/disable/clear, TX submission/completion, RX descriptor queueing/status, optional status reporting declaration, initialization, uninitialization, and RX DMA start.

## Control flow and integration
`altera_tse_main.c` assigns these functions to a `struct altera_dmaops` instance for SGDMA hardware. The header provides the compile-time contract for `altera_sgdma.c`.

## State and persistence behavior
No state is stored here. Declared functions operate on `struct altera_tse_private`, `struct tse_buffer`, and SGDMA hardware state.

## Dependencies and integration points
It requires compatible definitions from `altera_tse.h` in users. It pairs with `altera_sgdmahw.h` for hardware layout details.

## Risks and edge cases
The header declares `sgdma_status()` but the implementation in this file set does not define it; if referenced elsewhere, that would be a link risk. Otherwise, signature drift would break the DMAops assignments.

## Test signals
Compile the composite Altera TSE driver and confirm SGDMA callbacks link correctly and match the `altera_dmaops` signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdmahw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdmahw.h

## Purpose
`altera_sgdmahw.h` defines the legacy SGDMA hardware descriptor and CSR ABI for the Altera TSE SGDMA backend.

## Important APIs, types, and constants
- `struct sgdma_descrip` is the packed DMA descriptor with read/write addresses, next descriptor, byte counts, burst fields, transfer status, and control ownership/EOP/fixed-address bits.
- Status bits identify generic, length, CRC, truncation, PHY, collision, and EOP states.
- Control bits define EOP, read-fixed, write-fixed, and hardware ownership.
- `struct sgdma_csr` maps status, control, and next-descriptor registers with reserved padding.
- CSR status/control macros define error, EOP, descriptor/chain completion, busy, interrupt enables, start, stop-on-error, max-descriptor interrupt, reset, clear-owned-by-hardware, polling mode, and clear-interrupt.
- `sgdma_csroffs()` and `sgdma_descroffs()` provide offsets for register/descriptor field access helpers.

## Control flow and integration
The header has no executable flow. `altera_sgdma.c` uses these definitions to program descriptor memory, start/clear/reset controllers, test busy/EOP state, and parse RX status.

## State and persistence behavior
The described state lives in DMA-visible descriptor memory and volatile SGDMA MMIO registers. Hardware owns descriptors while `SGDMA_CONTROL_HW_OWNED` is set.

## Dependencies and integration points
It depends on bit and offset macros from kernel headers. It is private to the Altera TSE SGDMA backend but must match the SGDMA IP core configured in hardware.

## Risks and edge cases
The packed descriptor layout is a hardware ABI. Changing field sizes/order or control bits can corrupt DMA. The status/control register comments are the authoritative semantic map for the backend; mistakes cause missed interrupts, stuck busy state, or dropped RX/TX.

## Test signals
Validate descriptor programming with SGDMA hardware or simulation, reset/start/interrupt-clear behavior, RX error bit propagation, EOP handling, and ownership-bit transitions during TX/RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_sgdmahw.h -->
