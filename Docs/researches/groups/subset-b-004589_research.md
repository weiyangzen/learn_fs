# Research: subset-b-004589

This grouped report covers the Netronome/Corigine NFP netdev control ABI, PF/VF bring-up, datapath support, ethtool/debug interfaces, representors, SR-IOV configuration, AF_XDP support, port/devlink integration, shared-buffer registration, and small nfpcore helper headers. Each section is delimited for deterministic splitting into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ctrl.h

## Purpose

`nfp_net_ctrl.h` defines the firmware-facing control BAR ABI for NFP network vNICs. It is the central map of offsets, bit definitions, mailbox commands, metadata formats, RSS layout, ring configuration registers, statistics registers, TLV capability records, and parsed TLV capability state used by the rest of the NFP network driver.

## Important APIs, Types, and Functions

The file exports constants rather than executable code. Important groups include `NFP_NET_CFG_CTRL*` capability/control bits, `NFP_NET_CFG_UPDATE*` reconfiguration flags, `NFP_NET_CFG_STS*` link status and link-rate encodings, RSS controls under `NFP_NET_CFG_RSS_*`, TX/RX ring register address macros, interrupt-cause registers, legacy and TLV statistics offsets, mailbox command IDs, and BPF/IPsec/flow-steering metadata constants. `struct nfp_net_tlv_caps` is the parsed TLV state consumed by runtime code, and `nfp_net_tlv_caps_parse()` is the parser entry point implemented elsewhere.

## Control Flow

There is no local control flow, but the definitions shape driver sequencing. Runtime code writes control bits, ring DMA addresses, ring sizes, MSI-X vectors, mailbox payloads, and RSS tables into the CFG BAR, then signals firmware with the matching `NFP_NET_CFG_UPDATE_*` bits. Consumers also read status/capability words and optional TLVs to choose datapath features, representor capabilities, mailbox location, per-vNIC statistics layout, crypto capabilities, and ME clock frequency for interrupt moderation conversion.

## State and Persistence Behavior

The state described here lives in device BAR memory and firmware-owned control structures, not in this header. Persistent hardware-facing fields include enabled ring masks, MTU, buffer size, MAC address, RSS key/indir table, ring DMA locations, IRQ moderation values, stats counters, mailbox values, and TLV capability data. Because offsets are an ABI, changes are high risk and must remain compatible with firmware.

## Dependencies and Integration Points

The header is included by PF/VF probe, datapath setup, ethtool, representor, SR-IOV, XDP/BPF, flow-steering, crypto, and debug paths. It depends only on Linux integer/bit macros but integrates with firmware symbols, NFP queue-controller BARs, ethtool link-rate reporting, devlink shared-buffer state, and mailbox helpers.

## Risks and Edge Cases

Offset and bit definitions are contract-sensitive. Incorrect sizes or alignment for TLVs, mailbox values, ring blocks, or stats blocks can make the host and firmware disagree. Some features have mutually constrained control bits, such as old/new VLAN offloads, LSO/LSO2, RSS/RSS2, checksum-complete metadata, and representor capabilities. TLV parsing must reject required unknown TLVs while tolerating reserved/padding regions. Code using mailbox length macros must respect `NFP_NET_CFG_MBOX_VAL_MAX_SZ`.

## Test Signals

Useful coverage is primarily integration and ABI validation: PF/VF probe across firmware ABI versions, ethtool stats with legacy and TLV stats, RSS programming, VLAN strip/insert variants, mailbox VF/VLAN/multicast/flow-steer commands, interrupt moderation, BPF/crypto capability parsing, and register dumps verifying offsets against firmware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_debugdump.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_debugdump.c

## Purpose

`nfp_net_debugdump.c` implements TLV-driven ethtool firmware/debug dumps for NFP PF devices. It loads a firmware dump specification from the `_abi_dump_spec` runtime symbol, calculates the dump size for a requested dump level, and populates an ethtool dump buffer with firmware name, hwinfo, selected hwinfo fields, runtime symbols, direct CSR ranges, XPB CSR ranges, ME CSR ranges, and indirect ME CSR contexts.

## Important APIs, Types, and Functions

External entry points are `nfp_net_dump_load_dumpspec()`, `nfp_net_dump_calculate_size()`, and `nfp_net_dump_populate_buffer()`. Key local types are `struct nfp_dump_tl`, `struct nfp_dumpspec_csr`, `struct nfp_dumpspec_rtsym`, `struct nfp_dump_csr`, `struct nfp_dump_rtsym`, `struct nfp_dump_prolog`, `struct nfp_dump_error`, `struct nfp_level_size`, and `struct nfp_dump_state`. Core helpers include `nfp_traverse_tlvs()`, `nfp_add_tlv_size()`, `nfp_dump_for_tlv()`, `nfp_dump_csr_range()`, `nfp_dump_indirect_csr_range()`, `nfp_dump_single_rtsym()`, `nfp_dump_hwinfo()`, and `nfp_dump_hwinfo_field()`.

## Control Flow

Dump spec loading looks up `_abi_dump_spec`, allocates a `struct nfp_dumpspec` with `vmalloc()`, and reads the runtime symbol into memory. Size calculation seeds the total with a prolog TLV, traverses top-level dump-level TLVs, selects the requested level, and recursively adds the aligned output size for each dumpable TLV. Population mirrors that traversal: write a prolog, find matching dump-level TLVs, dispatch each dumpable by type, reserve an aligned output TLV, then fill it from NFP CPP reads, XPB reads, runtime symbol reads, hwinfo strings, or error TLVs.

## State and Persistence Behavior

The file does not persist driver settings, but it reads persistent firmware/runtime state through CPP, XPB, RTSYM, MIP, and hwinfo interfaces. `struct ethtool_dump.len` is updated with the actual dumped size. Error conditions are embedded in output TLVs so a partial dump can still be returned with per-object failure metadata.

## Dependencies and Integration Points

It integrates with ethtool dump ops in `nfp_net_ethtool.c`, PF state in `struct nfp_pf`, runtime symbols from `nfp_rtsym`, hwinfo from `nfpcore/nfp.h`, MIP firmware names, NFP CPP read APIs, XPB reads, and indirect CSR helpers from `nfp_asm.h`. The output format is firmware ABI data and must remain deterministic for support tooling.

## Risks and Edge Cases

The TLV walker validates length and 4-byte alignment, but malformed firmware specs can still cause missing or error TLVs. Buffer accounting in `nfp_add_tlv()` is critical because ethtool provides the destination length. CSR specs are accepted only for 32- or 64-bit register widths. Runtime symbols and hwinfo keys must be NUL-terminated inside the TLV payload. Indirect CSR reads write context selector state before reads, so failures must preserve useful `error_offset` data.

## Test Signals

Tests should cover dump levels with valid CSR, indirect CSR, XPB, RTSYM, hwinfo, firmware-name, unknown, malformed-length, and missing-symbol TLVs. Fault injection around `nfp_cpp_read()`, `nfp_xpb_readl()`, `nfp_rtsym_read()`, and undersized ethtool buffers should verify error TLV creation and size consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_debugdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_debugfs.c

## Purpose

`nfp_net_debugfs.c` creates the NFP netdev debugfs hierarchy and exposes live RX, TX, and XDP ring descriptor state for each vNIC. It is a diagnostic-only interface used to inspect host pointers, queue-controller pointers, descriptor contents, DMA addresses, fragments, and optional TX write-back state.

## Important APIs, Types, and Functions

Public helpers are `nfp_net_debugfs_vnic_add()`, `nfp_net_debugfs_device_add()`, `nfp_net_debugfs_dir_clean()`, `nfp_net_debugfs_create()`, and `nfp_net_debugfs_destroy()`. Show handlers are `nfp_rx_q_show()`, `nfp_tx_q_show()`, `nfp_xdp_q_show()`, and shared `__nfp_tx_q_show()`. `DEFINE_SHOW_ATTRIBUTE()` binds the handlers to debugfs file operations. The module-global `nfp_dir` is the root `nfp_net` dentry.

## Control Flow

Module/device setup creates `nfp_net/<pci-name>/vnicN/queue/{rx,tx,xdp}/` files. RX reads take `rtnl_lock()`, verify that the vector/ring exists and that the vNIC is running, read queue-controller freelist pointers, print ring metadata, then iterate descriptors and mark host/freelist pointer positions. TX/XDP reads similarly choose the normal or XDP ring, read device read/write pointers, print optional write-back, then delegate descriptor formatting to the active datapath ops via `nfp_net_debugfs_print_tx_descs()`.

## State and Persistence Behavior

The file owns debugfs dentries stored in `nn->debugfs_dir` and the global root pointer. It does not mutate datapath state except for transient register reads. It serializes inspection with RTNL to avoid racing netdev/ring teardown and checks `nfp_net_running()` before dereferencing active ring content.

## Dependencies and Integration Points

It depends on Linux debugfs, seq_file, RTNL, queue-controller pointer helpers, `struct nfp_net_r_vector`, `struct nfp_net_rx_ring`, `struct nfp_net_tx_ring`, AF_XDP ring storage, and datapath-specific descriptor printers from `struct nfp_dp_ops`.

## Risks and Edge Cases

Debugfs readers inspect live DMA rings, so pointer validity and RTNL coverage are important. XSK and normal RX rings use different software buffer arrays. Ring modulo annotations assume descriptor counts are nonzero and stable while running. Debugfs creation ignores failures, consistent with debugfs conventions, so diagnostics may be absent without affecting probe.

## Test Signals

Validation should mount debugfs, probe PF and VF vNICs, read RX/TX/XDP queue files while interfaces are down, up, under traffic, and after AF_XDP pool setup. Teardown tests should repeatedly add/remove devices while reading debugfs to catch stale pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_dp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_dp.c

## Purpose

`nfp_net_dp.c` provides datapath-neutral allocation, initialization, reset, hardware configuration, and small transmit helpers for NFP netdev rings. It sits below netdev lifecycle code and above the NFD3/NFDK datapath-specific implementations selected through `struct nfp_dp_ops`.

## Important APIs, Types, and Functions

Exported functions include `nfp_net_rx_alloc_one()`, `nfp_net_rx_ring_reset()`, `nfp_net_tx_rings_prepare()`, `nfp_net_tx_rings_free()`, `nfp_net_rx_rings_prepare()`, `nfp_net_rx_rings_free()`, `nfp_net_rx_ring_hw_cfg_write()`, `nfp_net_tx_ring_hw_cfg_write()`, `nfp_net_vec_clear_ring_data()`, `nfp_net_tx()`, `__nfp_ctrl_tx()`, `nfp_ctrl_tx()`, and `nfp_net_vlan_strip()`. Important local helpers allocate/free RX software buffers, initialize TX/RX ring queue-controller pointers, allocate coherent descriptor memory, register XDP RXQ memory models, and allocate optional TX ring write-back memory.

## Control Flow

Ring preparation allocates arrays of `struct nfp_net_tx_ring` or `struct nfp_net_rx_ring`, initializes each ring's index, vector pointer, queue-controller index, queue-controller BAR pointer, and stats sync, then allocates descriptor resources and per-buffer software state. TX resource allocation is delegated to datapath ops; RX descriptor rings are allocated here and then filled with either page fragments/pages or left for XSK pools. Hardware configuration writes ring DMA addresses, ring size encodings, MSI-X vector entries, and TX write-back DMA addresses to the CFG BAR.

## State and Persistence Behavior

Persistent runtime state includes `dp->tx_rings`, `dp->rx_rings`, optional `dp->txrwb`, ring DMA addresses, descriptor memory, software buffer arrays, XDP RXQ registrations, host read/write pointers, queue-controller BAR pointers, and CFG BAR ring configuration. `nfp_net_rx_ring_reset()` reestablishes the driver's expected freelist geometry after device disable by moving the empty entry to the end and zeroing descriptors.

## Dependencies and Integration Points

The file depends on `nfp_net.h` core structures, `nfp_net_dp.h` inline DMA helpers and ops wrappers, `nfp_net_xsk.h` XSK checks, Linux DMA mapping/coherent allocation, page-frag allocation, XDP RXQ registration, VLAN accel APIs, queue-controller pointer helpers, and NFP CFG BAR macros.

## Risks and Edge Cases

Error unwind paths must free partially allocated TX rings, RX descriptors, XDP RXQ registrations, coherent write-back memory, and software buffers in the right order. XDP mode changes allocation from page fragments to full pages and changes DMA direction/length assumptions through `dp`. XSK rings skip normal RX buffer allocation and use different buffer arrays. `nfp_net_vlan_strip()` must reconcile old descriptor VLAN flags with chained metadata and reject unknown TPIDs.

## Test Signals

Test ring preparation/failure injection for descriptor allocation, TX op allocation, buffer allocation, DMA map failure, XDP enabled, AF_XDP enabled, and TXRWB enabled. Runtime tests should reconfigure ring counts/sizes, open/close netdevs, run VLAN strip traffic, verify CFG BAR ring fields, and use KASAN/KMEMLEAK for ring lifecycle leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_dp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_dp.h

## Purpose

`nfp_net_dp.h` is the shared datapath interface for NFP netdev implementations. It defines DMA helper inlines, ring-space helpers, interrupt unmasking, the `struct nfp_dp_ops` abstraction, wrappers around datapath-specific operations, and exported common datapath entry points.

## Important APIs, Types, and Functions

Important inlines are `nfp_net_dma_map_rx()`, `nfp_net_dma_sync_dev_rx()`, `nfp_net_dma_unmap_rx()`, `nfp_net_dma_sync_cpu_rx()`, `nfp_net_tx_full()`, `nfp_net_tx_xmit_more_flush()`, `nfp_net_read_tx_cmpl()`, `nfp_net_free_frag()`, and `nfp_net_irq_unmask()`. `enum nfp_nfd_version` identifies NFD3 versus NFDK. `struct nfp_dp_ops` provides poll, xsk_poll, ctrl_poll, normal xmit, control TX, freelist fill, TX ring allocation/reset/free, TX buffer allocation/free, and descriptor debug printing hooks. Extern ops are `nfp_nfd3_ops` and `nfp_nfdk_ops`.

## Control Flow

Most runtime control flow is indirect. Core code calls wrapper functions in this header, which dispatch through `dp->ops` to the selected datapath implementation. Common code uses the DMA helpers when allocating/freeing RX buffers and uses queue-controller helpers for TX completion and write-pointer updates. Interrupt handlers clear CFG BAR ICR entries through `nfp_net_irq_unmask()` when firmware auto-masking is not used.

## State and Persistence Behavior

The header itself owns no storage, but its helpers mutate DMA mappings, queue-controller write pointers, TX pending-add counters, and CFG BAR interrupt-cause bytes. The ops table establishes persistent behavior selection for the life of a datapath instance and constrains capabilities through `cap_mask`, `dma_mask`, and minimum descriptors per packet.

## Dependencies and Integration Points

It includes `nfp_net.h` and relies on Linux DMA APIs, NFP queue-controller helpers, `struct napi_struct`, tasklets, seq_file, netdev TX APIs, and descriptor/ring structures declared in the main NFP headers. It is consumed by datapath C files, debugfs, XSK support, and netdev TX dispatch.

## Risks and Edge Cases

DMA helper lengths subtract `NFP_NET_RX_BUF_NON_DATA` and add/subtract headroom, so buffer sizing must remain consistent with allocation and firmware RX offset. `nfp_net_tx_full()` uses host pointer copies and may be conservative until completions are refreshed. `nfp_net_tx_xmit_more_flush()` relies on a write memory barrier before queue-controller pointer update. Ops table omissions or mismatched capability masks can break NFD3/NFDK feature gating.

## Test Signals

Compile both NFD3 and NFDK paths, exercise TX batching with `xmit_more`, RX DMA sync/unmap under XDP and non-XDP, interrupt auto-mask/unmask modes, debugfs descriptor printing, control TX, and datapath selection for PF and VF devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ethtool.c

## Purpose

`nfp_net_ethtool.c` implements ethtool operations for NFP data vNICs and NFP ports/representors. It reports driver and firmware identity, link settings, ring/channel configuration, self-tests, software/hardware/MAC/application stats, RSS and flow-steering controls, CFG BAR register dumps, firmware diagnostic dumps, module EEPROM reads, interrupt coalescing, FEC, pause, LED identification, and persistent port MAC access.

## Important APIs, Types, and Functions

The main exported objects are `nfp_net_ethtool_ops`, `nfp_port_ethtool_ops`, and `nfp_net_set_ethtool_ops()`. Key helpers include `nfp_net_get_drvinfo()`, `nfp_net_nway_reset()`, `nfp_net_get_link_ksettings()`, `nfp_net_set_link_ksettings()`, ring/channel setters, self-test functions (`nfp_test_link()`, `nfp_test_nsp()`, `nfp_test_fw()`, `nfp_test_reg()`), stats string/value helpers for software, legacy hardware, TLV hardware, MAC, and app stats, RSS helpers, flow-steering add/delete/get functions, dump helpers, module EEPROM helpers, coalesce setters, FEC/pause setters, `nfp_net_get_eeprom()`, and `nfp_net_set_eeprom()`.

## Control Flow

Read operations translate current driver state and firmware tables into ethtool data structures. Link settings prefer NSP ETH-table data and fall back to the CFG BAR link-rate field for plain vNICs. Set operations validate support and bounds, write through NSP or CFG BAR/mailbox helpers, and then trigger refresh or reconfiguration. Ring size/channel changes clone the datapath, alter counts, and call `nfp_net_ring_reconfig()`. RSS changes update local key/table/config and signal `NFP_NET_CFG_UPDATE_RSS`. Flow-steering converts ethtool flow specs to `struct nfp_fs_entry`, checks duplicates and masks, updates firmware through `nfp_net_fs_add_hw()`/`nfp_net_fs_del_hw()`, and keeps `nn->fs.list` sorted by location.

## State and Persistence Behavior

State read or changed here includes `nn->rss_key`, `nn->rss_itbl`, `nn->rss_cfg`, `nn->fs.list`, `nn->fs.count`, `nn->dp` ring sizes/counts, coalesce fields, `pf->dump_flag`, `pf->dump_len`, persistent hwinfo MAC strings, NSP port configuration, FEC/pause settings, LED mode, and stats counters. Many changes are persistent in firmware/NSP configuration rather than only Linux memory.

## Dependencies and Integration Points

The file bridges Linux ethtool to NFP core services: NSP open/config/read-module/hwinfo APIs, CPP/resource reads, app stats hooks, port helpers, shared control BAR offsets, flow-steering hardware helpers, debugdump routines, and NFP ETH-table media/FEC/speed metadata. Representors reuse `nfp_port_ethtool_ops` with switch-perspective stats.

## Risks and Edge Cases

Large scope makes consistency between string counts and data counts important. Link-mode arrays must match `NFP_MEDIA_LINK_MODES_NUMBER` and media bitmaps. Changing link settings is refused while netdev is running to avoid port-disable states. Flow steering supports only selected masks and only RSS context 0. The `nfp_net_fs_add()` insertion path uses sorted list traversal and replacement semantics that must remain valid for empty/end insertion. Coalesce conversion depends on TLV ME frequency; zero or stale frequency would break usec-to-tick validation.

## Test Signals

Run `ethtool -i`, `-S`, `-k`, `-l/-L`, `-g/-G`, `-c/-C`, `-x/-X`, `-n/-N`, `-d`, `--get-dump/--set-dump`, module EEPROM reads, FEC/pause/LED operations, and link-mode changes on physical ports and representors. Include TLV stats firmware, legacy stats firmware, unsupported NSP feature versions, flow-steering duplicate/mask errors, and ring/channel reconfiguration under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_main.c

## Purpose

`nfp_net_main.c` is the PF-side NFP netdev entry point. It maps firmware runtime symbols, allocates and initializes PF data vNICs and optional control vNICs, starts the selected NFP application, registers devlink resources and debugfs, allocates IRQs, tracks physical port table changes, and cleans everything up on PCI remove.

## Important APIs, Types, and Functions

Important exported functions are `nfp_net_get_mac_addr()`, `nfp_net_lr2speed()`, `nfp_net_speed2lr()`, `nfp_net_refresh_port_table_sync()`, `nfp_net_refresh_port_table()`, `nfp_net_refresh_eth_port()`, `nfp_net_pci_probe()`, and `nfp_net_pci_remove()`. Local helpers allocate/free/init/clean vNICs, distribute IRQs, map/unmap BAR-like CPP areas, start/stop app control vNICs, update ETH-table port state, and schedule asynchronous port refresh work.

## Control Flow

PF probe requires a runtime symbol table, reads max data vNIC count, maps data vNIC control memory, optional MAC stats, VF config tables, and queue-controller memory, validates firmware ABI/class, determines queue stride, allocates/initializes the app, registers shared buffers and devlink params, creates debugfs, allocates vNIC objects from consecutive CSR slices, allocates/distributes IRQ vectors, starts the app/control vNIC/SR-IOV state, initializes data vNICs, then registers devlink. Remove reverses the sequence: unregister devlink, clean/free data vNICs, stop app/control vNIC, remove debugfs/devlink params, unregister shared buffers, free IRQs/app, unmap memory, and cancel refresh work.

## State and Persistence Behavior

The file mutates `struct nfp_pf` fields for mapped areas, vNIC lists, vNIC count, app pointer, control vNIC, IRQ entries, debugfs dentry, shared port refresh work, MAC stats memory, VF config memory, and port lists. It updates `struct nfp_net` BAR pointers, IDs, app/port pointers, queue stride, and data-vNIC lifecycle. It writes CFG BAR link-rate mirror values based on NSP ETH-table speed.

## Dependencies and Integration Points

It integrates with nfpcore CPP/runtime symbols, NFP NSP ETH tables, NFFW/MIP data, `nfp_app` lifecycle, devlink, shared-buffer registration, NFP port helpers, SR-IOV app hooks, core `nfp_net_init()`/`nfp_net_clean()`, MSI-X allocation helpers, and debugfs.

## Risks and Edge Cases

Probe has many partial-failure labels; cleanup ordering must avoid leaked CPP areas, devlink locks, debugfs dentries, vNICs, IRQs, and app resources. ETH-table refresh can mark ports invalid and unregister vNICs, so callers must hold the devlink lock and use RTNL around port state. Firmware ABI version checks gate queue stride and VF isolation. Empty vNIC lists are treated as remove races in refresh.

## Test Signals

PF probe/remove tests should cover missing symbol table, unsupported firmware ABI, missing optional MAC/VF symbols, control-vNIC app requirement, multiple data vNICs, IRQ scarcity, invalid ETH-table overrides, port refresh work, SR-IOV enabled at start, and repeated bind/unbind with lockdep/KMEMLEAK enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_repr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_repr.c

## Purpose

`nfp_net_repr.c` implements NFP representor netdevices for physical ports, PF ports, and VF ports. Representors expose switch-facing ports to Linux, forward transmitted skbs to a lower PF netdev using metadata destination port IDs, provide hardware and CPU-hit statistics, inherit supported offloads from lower-device representor capability TLVs, and manage representor allocation/cleanup sets.

## Important APIs, Types, and Functions

Public functions include `nfp_repr_get_locked()`, `nfp_repr_inc_rx_stats()`, `nfp_repr_transfer_features()`, `nfp_repr_init()`, `nfp_repr_free()`, `nfp_repr_alloc_mqs()`, `nfp_repr_clean_and_free()`, `nfp_reprs_clean_and_free()`, `nfp_reprs_clean_and_free_by_type()`, `nfp_reprs_alloc()`, and `nfp_reprs_resync_phys_ports()`. `nfp_repr_netdev_ops` binds open, stop, xmit, MTU, stats, offload-stats, phys-port naming, TC, VF controls, feature fixing, MAC setting, and parent-ID ops.

## Control Flow

Initialization assigns lockdep classes, stores port/app pointers, allocates a `metadata_dst` with `METADATA_HW_PORT_MUX`, records the firmware control-message port ID and lower PF netdev, configures feature flags from `nn->tlv_caps.repr_cap`, calls app-specific init, and registers the netdev. TX drops any previous dst, attaches the representor metadata dst, rewrites `skb->dev` to the lower device, queues via `dev_queue_xmit()`, and records per-CPU TX stats or drops. Open/stop configure the physical port and call app-specific representor hooks.

## State and Persistence Behavior

Persistent state lives in `struct nfp_repr`: netdev pointer, metadata dst, associated `struct nfp_port`, app pointer, per-CPU stats, and app-private data. `struct nfp_reprs` stores RCU-protected representor netdev arrays. Cleanup unregisters the netdev, calls app cleanup/preclean hooks, releases metadata dst, frees ports, synchronizes RCU when removing app references, and frees per-CPU stats/netdev memory.

## Dependencies and Integration Points

Representors depend on Linux netdev metadata dst support, RCU, per-CPU u64 stats, lower PF netdev capabilities, `nfp_app` representor hooks, NFP port helpers, SR-IOV ndo wrappers, MAC stats offsets, vNIC stats offsets from `nfp_net_ctrl.h`, and ethtool port ops.

## Risks and Edge Cases

Feature transfer must intersect with lower-device features while preserving software and HW TC flags. Statistics are switch-perspective for vNIC ports, so RX/TX counters are intentionally flipped. `nfp_reprs_resync_phys_ports()` removes invalid physical-port representors in place and must synchronize RCU before freeing. TX always returns `NETDEV_TX_OK`; errors are reflected in representor stats, not netdev queue backpressure.

## Test Signals

Exercise physical/PF/VF representor creation, packet TX/RX CPU-hit stats, hardware stats on MAC and vNIC ports, MTU propagation, feature changes on lower devices, TC offload enable/disable, VF ndo passthrough, port invalidation during ETH-table refresh, and teardown under concurrent RCU readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_repr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_repr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_repr.h

## Purpose

`nfp_net_repr.h` declares the representor data structures and APIs used by NFP applications and port-management code. It defines representor containers, per-CPU stats, representor private data, representor type IDs, and helpers to identify and allocate NFP representor netdevs.

## Important APIs, Types, and Functions

Important types are `struct nfp_reprs`, `struct nfp_repr_pcpu_stats`, `struct nfp_repr`, and `enum nfp_repr_type`. Important helpers are `nfp_netdev_is_nfp_repr()`, `nfp_repr_get_port_id()`, and `nfp_repr_alloc()`. Declared functions cover locked lookup, RX stats increment, feature transfer, initialization/free, multi-queue allocation, clean-and-free, cleanup by type, representor set allocation, and physical-port resync.

## Control Flow

The header supports representor lifecycle flows: allocate a netdev with `nfp_repr_alloc_mqs()`, initialize it against an app, control-message port ID, NFP port, and lower PF netdev via `nfp_repr_init()`, use `nfp_repr_netdev_ops` for runtime callbacks, then clean/free individual representors or entire RCU-protected sets during app shutdown or port invalidation.

## State and Persistence Behavior

The structures persist mapping between Linux representor netdevs, firmware port IDs, app state, port state, and per-CPU packet counters. `reprs[]` is RCU-protected because datapath/control paths may look up representors while app code replaces or removes sets.

## Dependencies and Integration Points

The header depends on `net/dst_metadata.h`, net_device APIs, u64 stats sync, NFP app/port forward declarations, and the implementation in `nfp_net_repr.c`. It is used by application modules, SR-IOV representor management, port refresh, and packet receive paths that need to account CPU hits.

## Risks and Edge Cases

`nfp_repr_get_port_id()` assumes the netdev is an initialized NFP representor with a metadata dst. Callers must use the locked/RCU lookup contracts for `struct nfp_reprs`. Per-CPU stat comments include a typo around `tx_bytes`, but fields are clear. Representor type bounds depend on `NFP_REPR_TYPE_MAX`.

## Test Signals

Compile all representor consumers, validate type-based cleanup, RCU lookup under concurrent removal, port-ID extraction, and stats accounting. Static analysis should check callers do not pass plain NFP netdevs to representor-only helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_repr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_sriov.c

## Purpose

`nfp_net_sriov.c` implements PF-side netdev operations for configuring NFP SR-IOV VFs. It writes per-VF settings into the firmware VF config table, signals firmware through a mailbox/update path, and returns VF configuration to Linux.

## Important APIs, Types, and Functions

Public functions are `nfp_app_set_vf_mac()`, `nfp_app_set_vf_vlan()`, `nfp_app_set_vf_rate()`, `nfp_app_set_vf_spoofchk()`, `nfp_app_set_vf_trust()`, `nfp_app_set_vf_link_state()`, and `nfp_app_get_vf_config()`. Local helpers are `nfp_net_sriov_check()` for capability/table/VF validation and `nfp_net_sriov_update()` for mailbox update signaling.

## Control Flow

Each setter obtains the app from the netdev, validates that `vfcfg_tbl2` exists, checks the relevant firmware capability bit, validates VF index and user input, writes the appropriate fields in the VF's fixed-size config entry, writes mailbox VF number and update bits, then signals firmware with `nfp_net_reconfig(nn, NFP_NET_CFG_UPDATE_VF)` using the first PF vNIC. Firmware's return word is read and converted to a negative errno. Getter reads MAC, control flags, VLAN, optional VLAN protocol, and optional rates back into `struct ifla_vf_info`.

## State and Persistence Behavior

The file mutates the firmware-mapped `vfcfg_tbl2` area: mailbox capability/return/update/VF selector fields and per-VF MAC, control, VLAN, and rate entries. Changes are persistent from the PF driver's perspective but some, such as MAC changes, may require VF driver reload as noted by the log message.

## Dependencies and Integration Points

It depends on NFP app/PF state, VF config layout macros from `nfp_net_sriov.h`, CFG update bits from `nfp_net_ctrl.h`, Linux `ifla_vf_info`, VLAN protocol helpers, `FIELD_PREP/FIELD_GET`, and `nfp_net_reconfig()` firmware synchronization.

## Risks and Edge Cases

Capability checks must precede table writes for unsupported firmware. The VLAN path tolerates firmware without VLAN protocol support only for default 802.1Q; non-default TPIDs require the extra capability. Rate values are limited below `NFP_NET_VF_RATE_MAX`, and zero max maps to the firmware maximum sentinel. The update path assumes at least one vNIC exists on `pf->vnics`. Firmware return codes are positive errno values and are negated.

## Test Signals

Validate all VF ndo operations with supported and unsupported capabilities, invalid VF indexes, multicast MAC rejection, VLAN/QoS bounds, non-802.1Q VLAN protocol support, rate sentinel behavior, firmware refusal return codes, and `ip link show` VF config round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_sriov.h

## Purpose

`nfp_net_sriov.h` defines the NFP VF configuration mailbox and per-VF entry layout used by PF-side SR-IOV configuration code. It also declares the VF netdev operation helpers exported by `nfp_net_sriov.c`.

## Important APIs, Types, and Functions

The header defines mailbox size constants, capability bits (`MAC`, `VLAN`, `SPOOF`, `LINK_STATE`, `TRUST`, `VLAN_PROTO`, `RATE`), update bits, mailbox return/update/VF selector offsets, per-VF entry offsets for MAC/control/VLAN/rate, bit masks for trust/spoof/link-state/VLAN protocol/QoS/VID/rate, link-state encodings, and `NFP_NET_VF_RATE_MAX`. Declared functions mirror Linux VF ndo operations.

## Control Flow

There is no executable control flow. Setters use the layout to write a VF entry, fill mailbox update fields, and trigger firmware reconfiguration. Getter uses the same layout to decode `struct ifla_vf_info`.

## State and Persistence Behavior

The described state is a firmware-visible memory table. The first 16 bytes are the mailbox and the following fixed-width entries are indexed by VF number. The control byte combines link-state, spoof-check, and trust state; VLAN and rate fields pack multiple logical values.

## Dependencies and Integration Points

It integrates with PF runtime symbol mapping in `nfp_net_main.c`, Linux VF netdev operations in representor/netdev ops, and firmware handling of `NFP_NET_CFG_UPDATE_VF`.

## Risks and Edge Cases

Field packing must match firmware endian and bit placement. The comment notes MAC layout is chosen so firmware can read the address in one 6-byte read, which is easy to break by changing offsets. New capabilities need both mailbox cap and update bits to avoid host/firmware disagreement.

## Test Signals

Compile with SR-IOV paths, inspect generated offsets with firmware documentation, and run VF configuration tests for every declared capability, including old firmware that lacks VLAN protocol or rate capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_xsk.c

## Purpose

`nfp_net_xsk.c` implements AF_XDP zero-copy pool support for compatible NFP datapaths. It manages XSK RX buffer ownership, fills RX freelists from an XSK pool, maps/unmaps pools for DMA, installs/removes pools through ring reconfiguration, drops XSK RX buffers, and wakes NAPI for XSK TX progress.

## Important APIs, Types, and Functions

Public functions are `nfp_net_xsk_rx_unstash()`, `nfp_net_xsk_rx_free()`, `nfp_net_xsk_rx_bufs_free()`, `nfp_net_xsk_rx_ring_fill_freelist()`, `nfp_net_xsk_rx_drop()`, `nfp_net_xsk_setup_pool()`, and `nfp_net_xsk_wakeup()`. Local helpers are `nfp_net_xsk_rx_bufs_stash()`, `nfp_net_xsk_pool_map()`, and `nfp_net_xsk_pool_unmap()`.

## Control Flow

Freelist fill loops while RX space is available, allocates `xdp_buff`s from the queue's pool, stashes buffer/DMA state, writes 48-bit DMA addresses into RX descriptors, advances host write pointer, then uses a write memory barrier before incrementing the queue-controller freelist write pointer. Pool setup rejects NFDK and older firmware lacking dynamic RX offset or chained metadata, DMA-maps the new pool, clones datapath state, swaps `dp->xsk_pools[queue_id]`, and calls `nfp_net_ring_reconfig()`. Wakeup schedules the queue's NAPI instance.

## State and Persistence Behavior

State includes per-RX descriptor `xsk_rxbufs`, XSK pool DMA mappings, `r_vec->xsk_pool`, datapath cloned pool pointers, ring write pointers, RX descriptor reserved/metadata fields, and drop counters under `rx_sync`. Uninstall unmaps the previous pool after successful reconfiguration.

## Dependencies and Integration Points

It depends on AF_XDP driver APIs, XDP buffer pools, NFP RX descriptor helpers, NFP ring reconfiguration, datapath version/capability state, NAPI scheduling, traceable XDP infrastructure, and DMA mapping APIs.

## Risks and Edge Cases

The feature is deliberately disabled for NFDK and old firmware so datapath code can assume dynamic metadata support. Reconfiguration failure must unmap any newly mapped pool and leave old pool state intact. The queue ID is trusted in wakeup because AF_XDP setup validates it, but out-of-band callers would need bounds checks. DMA address width uses 48-bit descriptor encoding for NFP3800 while still accepting 40-bit addresses.

## Test Signals

Run AF_XDP zero-copy bind/unbind, pool replacement, RX fill, RX drop, wakeup, interface up/down, and ring reconfig tests. Include rejection tests for NFDK, non-dynamic RX offset, missing chained metadata, DMA map failure, and allocation failure from `xsk_buff_alloc()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_xsk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_xsk.h

## Purpose

`nfp_net_xsk.h` declares AF_XDP support functions and small ring-space helpers for NFP netdevs. It provides the shared interface between core datapath allocation, NFD datapaths, and the XSK implementation.

## Important APIs, Types, and Functions

It defines `NFP_NET_XSK_TX_BATCH`, `nfp_net_has_xsk_pool_slow()`, `nfp_net_rx_space()`, `nfp_net_tx_space()`, and prototypes for XSK RX buffer unstash/free/drop, pool setup, RX buffer array free, RX freelist fill, and wakeup. The helpers depend on `struct nfp_net_dp`, `struct nfp_net_rx_ring`, `struct nfp_net_tx_ring`, `struct nfp_net_xsk_rx_buf`, and `struct nfp_net_r_vector`.

## Control Flow

Callers use `nfp_net_has_xsk_pool_slow()` to select XSK versus normal RX allocation and free paths. Datapath refill logic uses `nfp_net_rx_space()` and TX logic uses `nfp_net_tx_space()` to preserve one empty ring slot. Netdev XDP setup calls `nfp_net_xsk_setup_pool()`, and AF_XDP wakeups call `nfp_net_xsk_wakeup()`.

## State and Persistence Behavior

The header owns no storage but encodes ring occupancy calculations using host read/write pointers and datapath XDP/pool pointers. The batch constant affects XSK TX scheduling granularity in implementation code.

## Dependencies and Integration Points

It includes `net/xdp_sock_drv.h` and is consumed by `nfp_net_dp.c`, `nfp_net_xsk.c`, and datapath implementations. It integrates with Linux AF_XDP pool setup and NFP ring structs from `nfp_net.h`.

## Risks and Edge Cases

Ring-space helpers assume monotonic ring pointers and one reserved slot. `nfp_net_has_xsk_pool_slow()` requires both an XDP program and a pool; changing XSK support must preserve that invariant. Queue IDs must be validated before indexing `xsk_pools`.

## Test Signals

Compile with and without AF_XDP support, run XSK bind/unbind per queue, verify ring-space calculations near wraparound, and exercise normal RX fallback when XDP program or pool is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_xsk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_netvf_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_netvf_main.c

## Purpose

`nfp_netvf_main.c` is the PCI VF driver entry point for NFP netdevs. It probes VF PCI devices, maps the VF control and queue-controller BARs, validates firmware ABI, allocates a single `struct nfp_net`, assigns interrupts, initializes the netdev, and cleans all VF resources on remove or shutdown.

## Important APIs, Types, and Functions

Key types and objects are `struct nfp_net_vf`, the `nfp_netvf_pci_device_ids` table, and `struct pci_driver nfp_netvf_pci_driver`. Main functions are `nfp_netvf_get_mac_addr()`, `nfp_netvf_pci_probe()`, and `nfp_netvf_pci_remove()`.

## Control Flow

Probe allocates VF private state, enables PCI memory, requests regions, sets bus mastering and DMA mask, maps the control BAR to `NFP_NET_CFG_BAR_SZ`, reads and validates firmware version/class, chooses queue stride and BAR layout based on firmware ABI, reads max ring counts, validates BAR resource sizes, computes queue offsets, allocates `struct nfp_net`, maps TX/RX queue memory either as one overlapping BAR mapping or separate mappings, reads/sets MAC address, allocates MSI-X vectors, initializes the NFP netdev, creates debugfs, and returns success. Remove tears down debugfs, cleans netdev, disables IRQs, unmaps queue/control BARs, frees netdev/private state, releases regions, and disables PCI.

## State and Persistence Behavior

State is per-VF and includes the `nfp_net` pointer, MSI-X entries, optional shared queue BAR mapping, debugfs directory, control BAR mapping, TX/RX queue BAR pointers, stride, `dp.is_vf`, and netdev MAC/permanent address. Hardware-visible changes are limited to normal `nfp_net_init()` and runtime operations after probe.

## Dependencies and Integration Points

It depends on Linux PCI, DMA mask setup, NFP device-info table, CFG BAR ABI, queue-controller offsets, core `nfp_net_alloc()`/`nfp_net_init()`/`nfp_net_clean()`, IRQ allocation helpers, and debugfs helpers. Unlike PF probe, it does not use CPP runtime symbols or `nfp_app`.

## Risks and Edge Cases

Firmware ABI determines whether TX/RX queues are in separate or shared BARs and whether VF isolation is available. BAR size sanity checks adjust ring counts but use divisor logic tied to queue stride. Partial probe failure paths must unmap the correct combination of overlapping/separate queue mappings. Invalid firmware-provided MACs are replaced with random MACs.

## Test Signals

Bind VFs for NFP3800/NFP6000 and Netronome/Corigine IDs, test old and current firmware ABI paths, BAR-size truncation, MSI-X shortage, invalid MAC fallback, repeated probe/remove/shutdown, and basic traffic with debugfs queue inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_netvf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_port.c

## Purpose

`nfp_port.c` implements common NFP port helpers shared by PF data netdevs and representors. It maps netdevs to `struct nfp_port`, provides parent ID and physical port names, delegates TC setup to the active app, protects feature changes while TC offloads are active, retrieves/refreshes ETH-table port data, configures physical port up/down state, initializes physical-port metadata, and allocates/frees port objects.

## Important APIs, Types, and Functions

Public functions are `nfp_port_from_netdev()`, `nfp_port_get_port_parent_id()`, `nfp_port_setup_tc()`, `nfp_port_set_features()`, `__nfp_port_get_eth_port()`, `nfp_port_get_eth_port()`, `nfp_port_get_phys_port_name()`, `nfp_port_configure()`, `nfp_port_init_phy_port()`, `nfp_port_alloc()`, and `nfp_port_free()`.

## Control Flow

`nfp_port_from_netdev()` distinguishes core NFP netdevs from representors and returns their stored port pointer. `nfp_port_get_eth_port()` checks if a physical port has a changed flag and refreshes from the NSP ETH table before returning it. Port naming switches on type to emit `pN`, `pNsM`, `pfN`, `pfNsM`, or `pfNvfM`. Physical port configure ignores non-physical or forced ports and otherwise calls `nfp_eth_set_configured()`. Physical-port init validates the ETH table entry, handles override-changed invalidation, stores ETH IDs and MAC stats pointers, and updates `netdev->dev_port`.

## State and Persistence Behavior

`nfp_port_alloc()` adds port objects to the PF port list, and `nfp_port_free()` removes/frees them. Port fields persist netdev/type/app relationships, ETH-table pointers, port IDs, MAC stats pointers, vNIC IDs, split IDs, and TC offload count. `nfp_port_configure()` changes firmware/NSP configured state for physical interfaces.

## Dependencies and Integration Points

The file depends on NFP netdev/representor type checks, `nfp_app_setup_tc()`, CPP serial lookup, NSP ETH helpers, port structures in `nfp_port.h`, and RTNL/lockdep expectations from callers. It feeds netdev ops and ethtool ops.

## Risks and Edge Cases

Unknown netdev types trigger `WARN(1)`. `nfp_port_set_features()` refuses disabling HW TC while offloads are active, so offload counting must be accurate. `__nfp_port_get_eth_port()` intentionally returns NULL for non-physical ports. Refresh failures set `NFP_PORT_CHANGED` and callers must handle NULL ETH data. Forced ports bypass configured-state changes.

## Test Signals

Test phys-port names for split/non-split physical, PF, split-PF, and VF ports; parent ID reporting; TC setup delegation; HW TC disable with active offloads; ETH-table refresh on changed flags; forced and non-physical configure no-ops; and allocation/free list integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_port.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_port.h

## Purpose

`nfp_port.h` defines the common NFP port abstraction and MAC statistics offsets. It is the interface used by netdevs, representors, ethtool, devlink, app code, and PF port-refresh code to represent physical NIC ports, logical PF ports, and logical VF ports.

## Important APIs, Types, and Functions

Important definitions are `enum nfp_port_type`, `enum nfp_port_flags`, speed bitmap indexes, and `struct nfp_port`. The structure stores netdev/app links, devlink port, link callback, TC offload count, physical ETH-table data, MAC stats base, supported speeds, PF/VF IDs, split-port metadata, vNIC control memory, and list membership. The header declares port netdev ops helpers, ETH-table accessors, physical-port init, refresh functions, devlink port register/unregister, and `nfp_port_ethtool_ops`.

## Control Flow

The header supports lifecycle flows where app/PF code allocates a port, fills physical or vNIC-specific union fields, registers a devlink port, associates it with a netdev/representor, and later refreshes or frees it. The inline `nfp_port_is_vnic()` quickly distinguishes PF/VF logical ports from physical ports for stats and ethtool handling.

## State and Persistence Behavior

Port objects persist the driver's view of hardware topology and offload state. `NFP_PORT_CHANGED` tracks stale physical-port data between ETH-table refreshes. MAC stats offsets define persistent firmware accumulator locations used by representor and ethtool stats.

## Dependencies and Integration Points

It depends on Linux devlink, netdev physical item IDs, NFP app/PF forward declarations, NSP ETH-table types, and ethtool. MAC stats offsets must match firmware `_mac_stats` layout and are consumed in `nfp_net_ethtool.c` and `nfp_net_repr.c`.

## Risks and Edge Cases

The union requires callers to branch on `port->type` before accessing fields. Physical ports may transition to `NFP_PORT_INVALID` after firmware configuration changes. MAC stat offsets are ABI-like and any mismatch skews stats. `tc_offload_cnt` is documented as boolean-like, so consumers should not depend on exact count semantics unless app code defines them.

## Test Signals

Compile all port consumers, validate devlink port registration for each type, exercise ETH-table invalidation, compare MAC stats offsets against firmware dumps, and check feature/offload behavior for physical and vNIC ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_shared_buf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_shared_buf.c

## Purpose

`nfp_shared_buf.c` registers firmware-described NFP shared buffers with devlink and implements devlink shared-buffer pool get/set callbacks via the NFP mailbox. It exposes buffer pool size, type, threshold type, and cell size to Linux devlink users.

## Important APIs, Types, and Functions

Public functions are `nfp_shared_buf_pool_get()`, `nfp_shared_buf_pool_set()`, `nfp_shared_buf_register()`, and `nfp_shared_buf_unregister()`. Local helper `nfp_shared_buf_pool_unit()` finds a shared buffer's pool size unit in `pf->shared_bufs`.

## Control Flow

Registration first requires PF mailbox support, reads the shared-buffer count runtime symbol, maps the shared-buffer descriptor table, allocates `pf->shared_bufs`, copies each descriptor from IO memory, and calls `devlink_sb_register()` for each shared buffer. Pool get validates unit size, sends `NFP_MBOX_POOL_GET`, checks reply length, and scales firmware size units to bytes. Pool set validates unit size and byte alignment, converts bytes to firmware units, and sends `NFP_MBOX_POOL_SET`. Unregister iterates registered shared buffers and frees the descriptor array.

## State and Persistence Behavior

Persistent driver state is `pf->shared_bufs` and `pf->num_shared_bufs`. Runtime firmware state includes pool sizes and threshold types changed through mailbox commands. Devlink registration state is tied to the PF devlink instance.

## Dependencies and Integration Points

It depends on devlink shared-buffer APIs, NFP runtime symbols `NFP_SHARED_BUF_COUNT_SYM_NAME` and `NFP_SHARED_BUF_TABLE_SYM_NAME`, mailbox commands, ABI structures from `nfp_abi.h`, CPP area mapping, and PF app/main lifecycle that calls register/unregister during PF probe/remove.

## Risks and Edge Cases

No mailbox means no shared-buffer registration, which is a supported no-op. Descriptor entries may grow in future firmware, so the code computes table entry stride from mapped area size and copies only known fields. Partial devlink registration failure must unregister previous buffers. Pool set rejects sizes not divisible by the unit size.

## Test Signals

Probe with no mailbox, no shared-buffer symbol, multiple shared buffers, larger descriptor strides, mailbox short replies, invalid unit size, pool get/set through `devlink sb`, and unregister after partial registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_shared_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/crc32.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/crc32.h

## Purpose

`nfpcore/crc32.h` provides small inline helpers for POSIX CRC32 calculation used by NFP core code, especially resource keys whose comments elsewhere describe CRC32-POSIX over identification strings.

## Important APIs, Types, and Functions

It declares `crc32_posix_end()` and `crc32_posix()`. `crc32_posix_end()` appends the little-byte sequence of the total length to an in-progress big-endian CRC32 state and returns the complemented final value. `crc32_posix()` performs `crc32_be(0, buff, len)` and finalizes it with the buffer length.

## Control Flow

The helpers are straight-line inlines. Finalization loops while `total_len` is nonzero, extracts the low byte, updates the big-endian CRC, shifts the length, and returns bitwise-not of the final CRC.

## State and Persistence Behavior

There is no persistent state. Results are deterministic for a given buffer and length and are suitable for matching firmware/resource table keys.

## Dependencies and Integration Points

The header depends on Linux `crc32_be()` from `<linux/crc32.h>`. It integrates with nfpcore resource lookup/key generation code.

## Risks and Edge Cases

Length finalization is part of POSIX CRC32 semantics; callers that use plain CRC32 will not match NFP resource keys. Empty buffers skip the length loop and return complement of the initial CRC state. The function consumes `size_t`, so results are platform-width aware for very large lengths.

## Test Signals

Compare known POSIX CRC32 vectors, empty input, short identification strings, and resource key values against firmware/resource table expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp.h

## Purpose

`nfpcore/nfp.h` is a compact public interface for NFP device access and query services. It declares hwinfo accessors, low-level NSP configuration/state helpers, NSP read/write commands, resource-table functions, and standard NFP resource names.

## Important APIs, Types, and Functions

Important declarations include `nfp_hwinfo_read()`, `nfp_hwinfo_lookup()`, packed hwinfo accessors, `nfp_nsp_cpp()`, NSP config modified/state helpers, `nfp_nsp_read_eth_table()`, `nfp_nsp_write_eth_table()`, `nfp_nsp_read_identify()`, `nfp_nsp_read_sensors()`, `nfp_resource_table_init()`, `nfp_resource_acquire()`, `nfp_resource_release()`, `nfp_resource_wait()`, and resource property accessors. Resource names include PCI vNIC resources, hwinfo, NSP, NSP diagnostics, NFFW, and MAC statistics.

## Control Flow

The header has no implementation. Consumers acquire CPP resources by name, query resource CPP ID/address/size, release resources, read hwinfo, and use NSP state helpers around management-processor operations. Resource names are fixed strings whose keys are CRC32-POSIX in the resource implementation.

## State and Persistence Behavior

The described state lives in NFP resource tables, hwinfo databases, and NSP firmware state. NSP config helpers expose mutable in-memory state for config entry iteration and modified tracking. Resource acquisition/release controls access to firmware-advertised address ranges.

## Dependencies and Integration Points

It includes `nfp_cpp.h` and is included by netdev PF probe, debugdump, ethtool NSP diagnostics, resource users, and hwinfo/NSP/resource implementation files. It bridges driver code to NFP service-processor and resource abstractions.

## Risks and Edge Cases

Resource names and CRC32 keying are ABI-sensitive. Callers must release acquired resources and handle optional resources returning `-ENOENT`. NSP config state functions expose raw pointers and indexes, so sequencing must be disciplined by the NSP implementation.

## Test Signals

Compile all nfpcore users, test resource acquire/wait/release for present and absent resources, hwinfo lookup and packed string retrieval, NSP ETH-table read/write, identify/sensor reads, and leak detection for unreleased resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000/nfp6000.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000/nfp6000.h

## Purpose

`nfpcore/nfp6000/nfp6000.h` defines NFP6000 CPP target IDs, memory-unit addressing constants, push/pull width helpers, locality-bit helpers, and declarations for CPP target/address translation routines.

## Important APIs, Types, and Functions

It defines target constants such as `NFP_CPP_TARGET_NBI`, `QDR`, `MU`, `PCIE`, `ARM`, `CRYPTO`, `ISLAND_XPB/CAP/CT_XPB`, and `CLS`, plus `NFP_ISL_EMEM0`, MU direct-access masks, `PUSHPULL()`, `PUSH_WIDTH()`, `PULL_WIDTH()`, `pushpull_width()`, `nfp_cppat_mu_locality_lsb()`, `nfp_target_pushpull()`, and `nfp_target_cpp()`.

## Control Flow

`pushpull_width()` masks a 4-bit encoded width and returns `-EINVAL` for zero or `2 << pp` for valid encodings. `nfp_cppat_mu_locality_lsb()` accepts modes 0 through 3 and returns bit 38 for 40-bit addresses or bit 30 for non-40-bit addresses, otherwise `-EINVAL`. The declared target helpers are implemented elsewhere to translate CPP IDs and island addresses.

## State and Persistence Behavior

The header has no runtime state. Constants encode hardware target IDs and address interpretation used by CPP read/write paths.

## Dependencies and Integration Points

It depends on Linux errno/types and is included by NFP CPP target translation code and debugdump paths that need target IDs. It integrates with NFP6000 hardware addressing rules and CPP island translation tables.

## Risks and Edge Cases

Invalid push/pull width encodings return negative errno and must be checked by callers. Target ID aliases share value 14 for XPB/CAP/CT_XPB and must be interpreted by context. Address locality bit selection depends on address width and MU mode.

## Test Signals

Unit-style tests should cover all push/pull encodings, invalid zero/default modes, MU locality for 32/40-bit paths, and CPP target translation for each declared target and island address form.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000/nfp6000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000/nfp_xpb.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000/nfp_xpb.h

## Purpose

`nfpcore/nfp6000/nfp_xpb.h` defines address-construction macros for NFP6000 XPB island and device addressing. It is a small hardware-addressing header used by low-level XPB/CPP access code.

## Important APIs, Types, and Functions

Macros are `NFP_XPB_OVERLAY(island)`, `NFP_XPB_ISLAND(island)`, `NFP_XPB_ISLAND_of(offset)`, and `NFP_XPB_DEVICE(island, slave, device)`. They pack or extract island, slave, and device fields according to NFP6000 XPB addressing rules.

## Control Flow

There is no executable control flow. Callers use the macros to compute XPB offsets for an island base or a specific island/slave/device tuple, or to recover an island number from an XPB offset.

## State and Persistence Behavior

The header has no state. The generated numeric addresses are hardware-facing constants used for register access.

## Dependencies and Integration Points

It is used by NFP6000 CPP/XPB code and diagnostic dump paths that read XPB CSR ranges. The comments tie it directly to NFP6000 databook addressing sections.

## Risks and Edge Cases

Input fields are masked, so out-of-range island/slave/device values silently wrap into encoded bit widths. Callers must validate higher-level hardware IDs if wrapping would be unsafe.

## Test Signals

Check macro outputs for known island/device examples from the NFP6000 databook and verify `NFP_XPB_ISLAND_of()` reverses the island overlay bits for constructed offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000/nfp_xpb.h -->
