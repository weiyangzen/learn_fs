# Research: subset-b-004573

This grouped report covers LAN966x, LAN969x, and shared Sparx5 Microchip Ethernet switch-driver files. Each source file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_impl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_impl.c

## Purpose
This file adapts LAN966x hardware VCAP blocks to the common Microchip VCAP API. It declares the ES0, IS1, and IS2 instances, allocates `vcap_admin` objects, initializes the hardware address ranges, selects per-port keysets, supplies default match fields for ingress or egress rules, moves entries, reads and writes cached key/action/counter streams, and exposes debugfs state.

## Important APIs, Types, And Functions
Important entry points are `lan966x_vcap_init()` and `lan966x_vcap_deinit()`. The `lan966x_vcap_ops` table supplies `validate_keyset`, `add_default_fields`, `cache_erase`, `cache_write`, `cache_read`, `init`, `update`, `move`, and `port_info` callbacks to `vcap_control`. `lan966x_vcap_inst_cfg[]` maps VCAP types to target instances, lookup counts, chain ranges, capacities, and ingress direction. IS1/IS2 helpers derive lookup numbers from chain IDs and discover valid keysets from `ANA_VCAP_S1_CFG` and `ANA_VCAP_S2_CFG`.

## Control Flow
Initialization allocates one `vcap_control`, then loops over the static instance descriptors. Each admin gets stream caches, lock/list initialization, address boundaries, core mapping, range initialization, and key deselection. After debugfs registration, each live port has IS1, IS2, and ES0 enabled. Rule programming flows through the common VCAP API: validate an API-proposed keyset against the current port parser configuration, inject default port/lookup fields, serialize rule data into admin cache arrays, and trigger VCAP update commands. Entry moves program `VCAP_MV_CFG` and issue `MOVE_UP` or `MOVE_DOWN`.

## State And Persistence
Runtime state lives in `lan966x->vcap_ctrl`, per-admin rule lists, enabled lists, stream caches, and hardware tables. Nothing is persisted to disk. Hardware-visible state includes VCAP entries/actions/counters, parser key-selection registers, ES0 enable bits, and REW statistics mode. ES0 counter handling also reads and writes ESDX packet counters through SYS statistic registers under `lan966x->stats_lock`.

## Dependencies And Integration Points
The file depends on LAN966x register helpers from `lan966x_main.h`, generated field metadata from `lan966x_vcap_ag_api.h`, and generic APIs from `vcap_api*`. It integrates with tc/flower users through the VCAP core, with per-port netdev state through `netdev_priv()`, and with debugfs through `vcap_debugfs()` and `vcap_port_debugfs()`.

## Risks And Edge Cases
`readx_poll_timeout()` return values are ignored in the VCAP update wait helper, so hardware command timeouts are not propagated to callers. Mask encoding writes inverted masks to hardware, so changes must preserve the key/mask convention. Default ingress port masks use `~BIT(port->chip_port)` and rely on the VCAP API field width. ES0 ESDX counters are limited to 8-bit IDs and share SYS statistic view state, making the stats lock important. Initialization error paths can leak earlier admins if a later allocation fails before `lan966x->vcap_ctrl` is published.

## Test Signals
Useful signals include successful probe with VCAP debugfs populated, tc filters installing on IS1/IS2/ES0 chains, keyset rejection for unsupported parser states, correct per-port default matches, counter reads after hit traffic, move/delete behavior under rule reordering, and driver unload without leaked VCAP rules or caches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_impl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vlan.c

## Purpose
This file owns LAN966x VLAN membership and per-port VLAN classification/rewriter programming. It keeps software masks for hardware VLAN table membership, tracks CPU VLAN intent, updates PVID/native VLAN state, applies ingress/egress tag behavior, and coordinates FDB/MDB entries when the CPU port joins or leaves VLANs.

## Important APIs, Types, And Functions
Public driver functions include `lan966x_vlan_init()`, `lan966x_vlan_port_add_vlan()`, `lan966x_vlan_port_del_vlan()`, `lan966x_vlan_cpu_add_vlan()`, `lan966x_vlan_cpu_del_vlan()`, `lan966x_vlan_port_apply()`, `lan966x_vlan_port_set_vid()`, `lan966x_vlan_port_set_vlan_aware()`, `lan966x_vlan_port_rew_host()`, and `lan966x_vlan_cpu_member_cpu_vlan_mask()`. Internal helpers manipulate `lan966x->vlan_mask[vid]`, `lan966x->cpu_vlan_mask`, and the `ANA_VLANACCESS` table command interface.

## Control Flow
`lan966x_vlan_init()` initializes the VLAN table, clears all normal VLANs, programs HOST and UNAWARE PVID membership for all physical ports plus CPU, configures the CPU port as VLAN-aware, and clears per-port REW VLAN settings. Adding a front-port VLAN may first add the CPU port and write FDB/MDB entries if bridge CPU intent already exists; then it updates PVID/native fields, hardware membership, and port registers. Deleting a VLAN removes port classification state and hardware membership, then removes CPU hardware membership and FDB/MDB entries when no front ports remain. CPU VLAN add/delete keeps an intent bitmap separate from active hardware membership.

## State And Persistence
All state is runtime memory plus hardware registers. `vlan_mask` is the source for VLAN table writes; `cpu_vlan_mask` records bridge CPU VLAN membership even when no front port currently uses that VID; each `lan966x_port` stores `pvid`, `vid`, and `vlan_aware`. Hardware state is in ANA VLAN table, ANA ingress VLAN/drop configuration, DEV MAC tag awareness, REW tag configuration, REW port VLAN defaults, and FDB/MDB tables updated by other files.

## Dependencies And Integration Points
The file is integrated with bridge VLAN callbacks, switchdev FDB/MDB helpers, LAN966x register accessors, and netdev port state. It depends on constants such as `HOST_PVID`, `UNAWARE_PVID`, `CPU_PORT`, `VLAN_N_VID`, and table polling timeouts from surrounding headers.

## Risks And Edge Cases
Only one untagged/native VLAN is allowed per port; attempts to add a second return `-EBUSY`. VLAN table update failures are logged but not propagated from `lan966x_vlan_set_mask()`, so callers may believe a software update succeeded when hardware rejected or timed out. CPU hardware membership is intentionally suppressed when no front ports are in the VLAN, which is important for broadcast storm avoidance but can surprise tests that inspect raw membership. `GENMASK(lan966x->num_phys_ports - 1, 0)` assumes at least one physical port.

## Test Signals
Test bridge VLAN add/delete, PVID transitions, untagged VLAN conflicts, host-mode tag insertion, VLAN-aware ports without PVID dropping untagged frames, CPU VLAN membership before and after first front-port join, FDB/MDB replay/erase, and table command timeout logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_xdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_xdp.c

## Purpose
This file provides LAN966x XDP setup, XDP transmit, receive-side program execution, and XDP RX queue registration. XDP is only supported when the driver uses FDMA, because the implementation depends on page-backed receive buffers and FDMA transmit helpers.

## Important APIs, Types, And Functions
`lan966x_xdp()` dispatches `XDP_SETUP_PROG` to `lan966x_xdp_setup()`. `lan966x_xdp_xmit()` implements netdev XDP frame transmit. `lan966x_xdp_run()` executes the installed BPF program on an RX page and returns FDMA disposition codes. `lan966x_xdp_present()`, `lan966x_xdp_port_init()`, and `lan966x_xdp_port_deinit()` manage global presence detection and `xdp_rxq_info` lifetime.

## Control Flow
Program setup rejects XDP when `lan966x->fdma` is absent. It atomically swaps the port program with `xchg()`, detects whether the switch moved between no-XDP and any-XDP states, and reloads the FDMA page pool only for those global transitions. On reload failure, it restores the old program. RX builds an `xdp_buff` starting after the IFH and headroom, runs the BPF program, and maps `XDP_PASS`, `XDP_TX`, `XDP_REDIRECT`, invalid actions, `XDP_ABORTED`, and `XDP_DROP` into FDMA actions.

## State And Persistence
The only persistent-in-memory XDP state is `port->xdp_prog` and `port->xdp_rxq`. The FDMA page pool may be rebuilt when XDP presence changes globally. BPF program references are owned through `bpf_prog_put()` after replacement. No disk persistence exists.

## Dependencies And Integration Points
The file depends on Linux BPF/XDP APIs, `lan966x_fdma_reload_page_pool()`, `lan966x_fdma_xmit_xdpf()`, page allocation geometry from `lan966x->rx.page_order`, and IFH layout constants. It integrates with netdev BPF ops and the FDMA RX path that calls `lan966x_xdp_run()`.

## Risks And Edge Cases
`lan966x_xdp_run()` assumes a non-NULL `port->xdp_prog`; callers must check XDP presence before invoking it. `XDP_TX` passes a page and length to a helper whose `xdp_xmit` path also accepts `xdp_frame` objects, so helper semantics must remain clear. The setup path swaps programs before FDMA reload and restores on error, but concurrent RX must be synchronized by the surrounding driver. XDP redirect errors drop the frame.

## Test Signals
Check extack rejection without FDMA, attaching/detaching XDP on one and multiple ports, page-pool reload on first attach and last detach, XDP_PASS delivery, XDP_DROP counters or traffic disappearance, XDP_TX loopback/transmit, XDP_REDIRECT to another device or cpumap, invalid action tracing, and RX queue registration cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/Kconfig

## Purpose
This Kconfig file defines build-time configuration for the Microchip Sparx5 switch driver, optional DCB support, and LAN969x family support layered on top of Sparx5.

## Important APIs, Types, And Functions
The symbols are `SPARX5_SWITCH`, `SPARX5_DCB`, and `LAN969X_SWITCH`. `SPARX5_SWITCH` is a tristate with dependencies on switchdev, MMIO, OF, supported architectures or compile testing, optional PTP clock support, and bridge availability. It selects `PHYLINK`, `PHY_SPARX5_SERDES`, `RESET_CONTROLLER`, `VCAP`, and `FDMA`. `SPARX5_DCB` is a bool default-y option gated by `SPARX5_SWITCH && DCB`. `LAN969X_SWITCH` is a bool depending on `SPARX5_SWITCH` and selects `PAGE_POOL`.

## Control Flow
There is no runtime control flow. The kernel configuration controls whether the shared Sparx5 object is built, whether `sparx5_dcb.o` is included, and whether LAN969x-specific files and page-pool based FDMA support are compiled into the Sparx5 module.

## State And Persistence
State is the kernel `.config` selection. It persists only through normal kernel configuration and build artifacts.

## Dependencies And Integration Points
This file connects the driver to net/switchdev, phylink, serdes PHY support, reset controller support, VCAP core, FDMA core, DCBNL, page_pool, OF platform probing, and architecture guards for Sparx5 and LAN969x SoCs.

## Risks And Edge Cases
`LAN969X_SWITCH` is a bool under a tristate parent, so LAN969x support is compiled into the Sparx5 module rather than as a separate module. Missing `PAGE_POOL` selection would break LAN969x FDMA compilation. Bridge dependency allows `BRIDGE=n`, so code must tolerate no bridge module. Compile-test coverage can expose architecture-specific assumptions around MMIO and DMA.

## Test Signals
Build configurations should include `SPARX5_SWITCH=m/y`, with and without `SPARX5_DCB`, with `LAN969X_SWITCH=y`, `COMPILE_TEST=y`, and bridge disabled. Expected output is one Sparx5 module containing optional LAN969x objects when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/Makefile

## Purpose
This Makefile assembles the `sparx5-switch.o` composite object and conditionally adds DCB, debugfs, and LAN969x source files based on Kconfig symbols.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SPARX5_SWITCH) += sparx5-switch.o` declares the module object. `sparx5-switch-y` lists the common Sparx5 implementation: main probing, packet path, netdev, phylink, port, MAC table, VLAN, switchdev, calendar, ethtool, FDMA, PTP, PGID, tc, QoS, VCAP, pools, scheduling, policing, PSFP, mirror, and registers. Conditional fragments add `sparx5_dcb.o`, `sparx5_vcap_debugfs.o`, and LAN969x files. Include paths add Microchip VCAP and FDMA headers.

## Control Flow
There is no runtime flow. Build-time object composition determines which functions and descriptor tables are available to the final driver binary.

## State And Persistence
The file contributes to build system state only. It does not define runtime or persistent state.

## Dependencies And Integration Points
It integrates the Sparx5 directory with Kbuild and with shared include directories under `drivers/net/ethernet/microchip/vcap` and `drivers/net/ethernet/microchip/fdma`. The LAN969x conditional block brings in family descriptors, generated registers, generated VCAP metadata, RGMII support, calendar support, and page-pool FDMA.

## Risks And Edge Cases
The LAN969x code is compiled into the same `sparx5-switch.o`, so missing prototypes or object ordering issues appear as link errors in the shared module. Generated API/register files must stay synchronized with headers used by common code. If `CONFIG_DEBUG_FS` is off, VCAP debugfs-specific symbols must not be referenced unconditionally elsewhere.

## Test Signals
Use kernel build targets for `CONFIG_SPARX5_SWITCH`, `CONFIG_SPARX5_DCB`, `CONFIG_DEBUG_FS`, and `CONFIG_LAN969X_SWITCH` combinations. Link success and absence of undefined VCAP/FDMA/generated-register symbols are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x.c

## Purpose
This file defines LAN969x family match data for the common Sparx5 driver. It provides IO target mapping, register table binding, hardware constants, port-speed classification and device-index mapping, scheduler/leak group data, QSGMII mux programming, a LAN969x-specific PTP two-step IRQ handler, and operation hooks used by common Sparx5 code.

## Important APIs, Types, And Functions
The exported object is `lan969x_desc`. Internals include `lan969x_main_iomap[]`, `lan969x_consts`, `lan969x_regs`, `lan969x_ops`, `lan969x_get_dev_mode_bit()`, `lan969x_port_dev_mapping()`, `lan969x_port_mux_set()`, `lan969x_ptp_irq_handler()`, `lan969x_get_sdlb_group()`, and `lan969x_get_hsch_max_group_rate()`.

## Control Flow
Platform matching selects `lan969x_desc`; common Sparx5 probe then uses its target map to bind MMIO ranges, its constants to size driver structures, its register arrays for offset calculation, and its ops for runtime family differences. Port helpers classify fixed LAN969x port numbers into 2.5G, 5G, 10G, or RGMII groups. QSGMII mode sets a per-quad mux bit. The PTP handler drains timestamp FIFO entries, pairs a TX timestamp and ID timestamp, finds the matching queued skb by `ts_id`, computes the hardware timestamp, completes `skb_tstamp_tx()`, and frees the skb.

## State And Persistence
Static descriptor data is read-only. Runtime state touched by this file includes `sparx5->ports[]`, per-port `tx_skbs`, `sparx5->ptp_skbs`, and hardware PTP FIFO/control registers. No persistent storage is modified.

## Dependencies And Integration Points
It depends on generated LAN969x register arrays, generated VCAP metadata, LAN969x calendar/RGMII/FDMA helpers, common Sparx5 PTP helpers, and common `sparx5_match_data` probing. The target IO map must align with the SoC memory map used by device tree resources.

## Risks And Edge Cases
Port-number maps are hard-coded and must match silicon. The PTP handler assumes a valid `sparx5->ports[txport]`; bad FIFO data could dereference a missing port. Timestamp queue matching is O(queue length) and protected by the per-port skb queue lock. `WARN_ON(!skb_match)` indicates lost timestamp correlation. QSGMII mux changes are skipped when the requested port mode already equals the current mode.

## Test Signals
Probe a LAN969x device tree, verify all targets map, bring up ports from each speed class, exercise QSGMII and RGMII modes, run PTP two-step transmit timestamping under load, check scheduler group rates, and confirm common Sparx5 paths call LAN969x FDMA/calendar/RGMII hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x.h

## Purpose
This header declares the LAN969x family interface used by the shared Sparx5 driver and LAN969x implementation files. It exposes descriptor data, generated register/VCAP tables, family-specific ops, and inline port classification helpers.

## Important APIs, Types, And Functions
Exports include `lan969x_desc`, `lan969x_vcap_stats`, `lan969x_vcaps`, `lan969x_vcap_inst_cfg`, generated register arrays, `lan969x_dsm_calendar_calc()`, `lan969x_port_config_rgmii()`, and LAN969x FDMA functions. Inline helpers classify port numbers as 2.5G, 5G, 10G, 25G, or RGMII.

## Control Flow
The header has no runtime control flow by itself. It lets `lan969x.c` populate `sparx5_ops` and lets common Sparx5 code call LAN969x-specific implementations through those hooks.

## State And Persistence
There is no storage here. The inline classification functions encode static hardware topology in code.

## Dependencies And Integration Points
It includes common Sparx5 main, register, and VCAP implementation headers. It is the local contract between generated LAN969x tables, family glue, RGMII, calendar, FDMA, and common driver code.

## Risks And Edge Cases
Hard-coded port classification is an ABI with the hardware. `lan969x_port_is_25g()` always returns false, so common code must not infer 25G support for this family. Header include paths reach through `../sparx5/`, so directory moves can break includes.

## Test Signals
Build with `CONFIG_LAN969X_SWITCH`, verify all externs resolve, and test port mode decisions for every physical port number, especially RGMII ports 28 and 29 and 10G ports 24-27.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_calendar.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_calendar.c

## Purpose
This file calculates DSM taxi calendars for LAN969x. It maps each taxi to LAN969x port positions, groups active devices by required speed, verifies taxi bandwidth, chooses a calendar length and slot spacing, and fills `sparx5_calendar_data->schedule`.

## Important APIs, Types, And Functions
The exported function is `lan969x_dsm_calendar_calc()`. Internal helpers are `lan969x_dsm_cal_idx_get()`, `lan969x_dsm_cal_get_dev()`, and `lan969x_dsm_cal_get_speed()`. `struct lan969x_dsm_cal_dev_speed` accumulates devices, required slot count, and slot gap per speed class.

## Control Flow
The function computes taxi bandwidth from core clock period, copies the static LAN969x taxi-port map, translates active port bandwidths through common Sparx5 calendar helpers, and sums required bandwidth. Empty taxis get an empty schedule. Non-empty taxis search for the smallest calendar length that can fit all slots at the computed bandwidth per slot. It clears the 64-slot schedule, then places each speed class by repeatedly finding the next empty slot and advancing by the class gap.

## State And Persistence
Only caller-provided `sparx5_calendar_data` is mutated. Hardware is not programmed here; common `sparx5_calendar.c` validates and writes the schedule later. No persistent state exists.

## Dependencies And Integration Points
The file depends on `sparx5_clk_period()`, `sparx5_get_port_cal_speed()`, `sparx5_cal_speed_to_value()`, `SPX5_DSM_CAL_LEN`, and the common calendar update path through `sparx5_ops.dsm_calendar_calc`.

## Risks And Edge Cases
Taxi port entries use sentinel value `99`; callers must keep `n_ports_all` below that sentinel meaning. The slot-placement algorithm can return `-ENOENT` if the gap pattern cannot find an empty slot. It checks required bandwidth against taxi bandwidth but relies on the later common checker for spacing quality. Calendar length greater than `SPX5_DSM_CAL_LEN` is rejected.

## Test Signals
Test empty taxis, single-speed taxis, mixed 10G/5G/2.5G/1G taxis, overcommitted bandwidth, all supported core clocks, and final hardware update through common DSM calendar init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_calendar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_fdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_fdma.c

## Purpose
This file implements the LAN969x FDMA datapath using coherent descriptor memory plus page_pool-backed RX pages. It supplies family-specific init/deinit, NAPI polling, RX frame construction, TX descriptor management, and DMA-mapped transmit.

## Important APIs, Types, And Functions
Exports are `lan969x_fdma_init()`, `lan969x_fdma_deinit()`, `lan969x_fdma_napi_poll()`, and `lan969x_fdma_xmit()`. Important helpers include `lan969x_fdma_rx_dataptr_cb()`, `lan969x_fdma_tx_dataptr_cb()`, `lan969x_fdma_get_next_dcb()`, `lan969x_fdma_tx_clear_buf()`, `lan969x_fdma_rx_get_frame()`, `lan969x_fdma_rx_alloc()`, and `lan969x_fdma_tx_alloc()`.

## Control Flow
Initialization configures RX/TX FDMA structures, switches the common hardware into FDMA injection mode, sets a 64-bit DMA mask, allocates RX page_pool and coherent FDMA descriptors, allocates TX buffers and descriptors, and resets FDMA. RX dataptr callbacks allocate pages from the page pool and publish DMA addresses. NAPI first reclaims completed TX descriptors, then consumes RX frames while descriptors report data, builds recyclable skbs from pages, parses IFH, trims FCS if requested, stamps PTP, updates stats, and passes packets to GRO. Consumed descriptor chains are reloaded before interrupts are re-enabled. TX finds an unused descriptor, expands head/tailroom if needed, pushes IFH, appends FCS space, maps the skb, records completion state, adds a DCB, and reloads FDMA.

## State And Persistence
State lives in `sparx5->rx.fdma`, `sparx5->tx.fdma`, `sparx5->rx.page_pool`, `sparx5->rx.page[dcb][db]`, `sparx5->tx.dbs`, descriptor rings, skb ownership, DMA mappings, and per-netdev stats. No disk persistence exists.

## Dependencies And Integration Points
It depends on common FDMA helpers, page_pool APIs, Sparx5 IFH parsing, PTP RX timestamping, common FDMA reload/stop/injection functions, netdev stats, NAPI, GRO, and DMA mapping APIs. It is selected through LAN969x ops in `lan969x.c`.

## Risks And Edge Cases
`lan969x_fdma_rx_alloc()` leaks the page pool if coherent descriptor allocation fails. `lan969x_fdma_xmit()` returns after DMA mapping failure without undoing IFH/FCS skb mutation. TX descriptor reclamation skips PTP skbs because timestamp completion owns them, so timestamp loss can keep descriptors used. `lan969x_fdma_free_pages()` assumes every page pointer was allocated. RX warns and recycles on invalid source port.

## Test Signals
Exercise sustained RX/TX, GRO delivery, FCS feature toggling, bridge offload marks, PTP RX and TX timestamp ownership, descriptor exhaustion returning `-EBUSY`, DMA mapping failures, init error unwinding, and deinit after active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_fdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_regs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_regs.c

## Purpose
This autogenerated file provides LAN969x register metadata arrays consumed by the common Sparx5 register access layer. It maps target sizes, register addresses/counts, group addresses/counts/sizes, and field positions/sizes for LAN969x silicon.

## Important APIs, Types, And Functions
The exported arrays are `lan969x_tsize`, `lan969x_raddr`, `lan969x_rcnt`, `lan969x_gaddr`, `lan969x_gcnt`, `lan969x_gsize`, `lan969x_fpos`, and `lan969x_fsize`. They are collected into `struct sparx5_regs lan969x_regs` in `lan969x.c`.

## Control Flow
There is no algorithmic runtime control flow. Common register macros index these arrays to calculate register addresses, group strides, replicated counts, and field encoding details. The tables determine whether generated register accessors reach the intended LAN969x hardware offsets.

## State And Persistence
All state is static read-only data. Hardware state is affected only indirectly when other code uses these tables for MMIO reads and writes.

## Dependencies And Integration Points
The file depends on enum indexes from Sparx5 register headers and must stay synchronized with the generated accessor macros. It is generated by cml-utils and tied to the commit ID recorded in the header.

## Risks And Edge Cases
Any wrong table entry can redirect MMIO to the wrong register or encode fields incorrectly. Because sparse designated initializers leave unspecified entries as zero, missing generated indexes may silently become address zero. Regeneration must be coordinated with header enum changes and common driver assumptions.

## Test Signals
Build-time array index coverage, probe register mapping, known register readback values, FDMA/PTP/QSYS/DSM/ANA/REW operations on real LAN969x hardware, and comparison with vendor register documentation are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_rgmii.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_rgmii.c

## Purpose
This file configures LAN969x RGMII MAC-side behavior for ports 28 and 29. It programs TX clock frequency, MAC speed, IFG, VLAN tag awareness, optional internal RX/TX delay lines, GPIO muxing, and MAC enablement.

## Important APIs, Types, And Functions
The exported function is `lan969x_port_config_rgmii()`. Internal helpers map speed to clock selectors and device speed selectors, validate delay properties in picoseconds, program `HSIO_WRAP_RGMII_CFG`, `DEVRGMII_*`, `HSIO_WRAP_DLL_CFG`, and `HSIO_WRAP_XMII_CFG`.

## Control Flow
Configuration first reads `rx-internal-delay-ps` and `tx-internal-delay-ps` from the port device node and maps allowed values to hardware selectors. It enables DLLs, enabling the delayed clock only when delay is nonzero. Then it releases RGMII clock resets and selects TX clock rate from link speed, enables GPIO RGMII muxing, enables RX/TX MAC, configures IFG, selects device speed, and programs VLAN tag parsing based on the port VLAN type and maximum tag count.

## State And Persistence
Runtime state is hardware register configuration derived from `struct sparx5_port`, `struct sparx5_port_config`, and device-tree delay properties. Settings persist in hardware until reconfigured or reset.

## Dependencies And Integration Points
The file integrates with phylink-driven port configuration through `sparx5_ops.port_config_rgmii`, with OF properties on each port node, and with Sparx5 VLAN state (`vlan_type`, `custom_etype`, `max_vlan_tags`).

## Risks And Edge Cases
Only exact delay values 0, 1000, 1700, 2000, 2500, 3000, and 3300 ps are accepted. `RGMII_PORT_IDX()` assumes only ports 28 and 29 call this path. `HSIO_WRAP_XMII_CFG(!idx)` is a compact mapping that should be checked against hardware docs. The comments distinguish MAC-side delay properties from PHY-mode delay semantics, so duplicate PHY and MAC delays are a board-design risk.

## Test Signals
Bring up 10/100/1000 Mbps RGMII links on ports 28/29, test each supported internal delay value, verify VLAN tagged and untagged traffic, confirm GPIO mux selection, and inspect invalid delay extents returning `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_rgmii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_vcap_ag_api.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_vcap_ag_api.c

## Purpose
This autogenerated file describes LAN969x VCAP key fields, action fields, field sets, typegroups, human-readable names, and per-VCAP metadata for the common VCAP API.

## Important APIs, Types, And Functions
The exported objects are `lan969x_vcaps[]` and `lan969x_vcap_stats`. Static data covers keyfield arrays for IS0, IS2, ES0, and ES2, actionfield arrays for those VCAPs, `vcap_set` descriptors, field-set maps, map sizes, typegroup arrays, and name tables for keysets, actionsets, keys, and actions.

## Control Flow
There is no procedural control flow. The VCAP core indexes this metadata to validate whether a requested key/action field exists in a selected field set, to serialize rule streams at the right bit offsets and widths, to add typegroup bits, and to expose readable names through debug/stat APIs.

## State And Persistence
All data is static read-only metadata. Runtime VCAP rule state is held by common VCAP admin structures and hardware tables, not by this file.

## Dependencies And Integration Points
The file includes Linux type/kernel helpers and `lan969x.h`. It must match VCAP enums from the shared Microchip VCAP API and the LAN969x hardware extraction/action layout. `lan969x.c` publishes this metadata through `sparx5_consts`, while `lan969x_vcap_impl.c` defines instance placement.

## Risks And Edge Cases
Because the file is generated, hand edits risk divergence from hardware definitions. Field offsets and widths are hardware ABI; a wrong value can corrupt rules or make tc filters match unexpected traffic. Large sparse arrays depend on enum stability. Metadata size mismatches between maps and set arrays can break VCAP validation.

## Test Signals
Build with VCAP enabled, inspect VCAP debugfs names, install tc flower rules covering IS0/IS2/ES0/ES2 paths, verify key/action serialization on hardware, and compare generated metadata version and commit with the register model used for the target kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_vcap_ag_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_vcap_impl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_vcap_impl.c

## Purpose
This file declares the LAN969x VCAP instance layout for the shared Sparx5 VCAP implementation. It maps logical VCAP types and chain ranges to physical blocks, map IDs, lookup counts, and ingress/egress direction.

## Important APIs, Types, And Functions
The exported object is `lan969x_vcap_inst_cfg[]`, an array of `struct sparx5_vcap_inst`. It defines three IS0 CLM instances, two IS2 instances, one ES0 instance, and one ES2 instance.

## Control Flow
There is no executable control flow beyond static initialization. Common Sparx5 VCAP initialization iterates this array to create `vcap_admin` blocks, determine chain ownership, program block numbers, and expose the correct VCAPs for tc rule insertion.

## State And Persistence
The array is static read-only configuration. It influences runtime VCAP admin state and hardware initialization but does not mutate state itself.

## Dependencies And Integration Points
It depends on common Sparx5 VCAP chain constants, lookup constants, `struct sparx5_vcap_inst`, and generated LAN969x VCAP metadata. The file is compiled only when LAN969x support is selected.

## Risks And Edge Cases
Chain boundaries must be contiguous and non-overlapping; otherwise tc chain routing can install rules in the wrong physical VCAP. IS0/IS2 `lookups_per_instance` uses integer division assumptions. ES0 and ES2 use count-based layouts rather than block numbers, so common code must handle both patterns. Incorrect `ingress` flags would route rule validation and default fields incorrectly.

## Test Signals
Test tc filters on every advertised chain range, verify debugfs VCAP instances, confirm IS0 CLM0/1/2 and IS2-0/1 rule placement, and validate ES0/ES2 egress rules after LAN969x probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_vcap_impl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_calendar.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_calendar.c

## Purpose
This file configures Sparx5-family traffic calendars. It programs the QSYS auto calendar from port bandwidths and computes, validates, and writes DSM taxi calendars used by the disassembler. The DSM calculation can be family-specific through `sparx5_ops.dsm_calendar_calc`.

## Important APIs, Types, And Functions
Exports include `sparx5_calendar_init()`, `sparx5_cal_speed_to_value()`, `sparx5_get_port_cal_speed()`, and the default `sparx5_dsm_calendar_calc()`. Important internals are `sparx5_config_auto_calendar()`, `sparx5_config_dsm_calendar()`, `sparx5_dsm_calendar_check()`, and `sparx5_dsm_calendar_update()`.

## Control Flow
`sparx5_calendar_init()` first configures QSYS auto calendar. It translates each front/internal port bandwidth into compact calendar codes, checks target SKU bandwidth and core-clock bandwidth, halts the calendar on Sparx5, writes `QSYS_CAL_AUTO`, grants idle use to virtual devices, enables auto mode, and checks hardware error state. DSM configuration allocates a scratch `sparx5_calendar_data`, calls the family calendar calculator for each taxi, validates spacing, programs DSM calendar entries, and switches banks on non-Sparx5 families.

## State And Persistence
State is hardware calendar registers plus temporary calculation buffers. It derives from current port configuration, target chip ID, core clock, and constants in `sparx5->data`. There is no disk persistence.

## Dependencies And Integration Points
The file depends on Sparx5 register accessors, port configuration state, family constants, internal-port mapping, and LAN969x or Sparx5 DSM calculator ops. It is called during driver/port initialization when port bandwidths are known.

## Risks And Edge Cases
Bandwidth guards reject configurations exceeding target or core capacity. The default DSM calculator has several integer scaling and spacing assumptions, including overhead loss compensation and special handling for slow core clocks. The calendar checker iterates modulo slot counts and must avoid zero-slot cases. `sparx5_dsm_calendar_update()` expects readback length to equal `cal_len - 1`.

## Test Signals
Test all core clocks, each supported target SKU, port bandwidth mixes, overcommit rejection, empty taxis, LAN969x calculator dispatch, DSM readback length, QSYS auto error bits, and traffic forwarding after link speed changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_calendar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_dcb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_dcb.c

## Purpose
This file implements Sparx5 DCBNL support for application priority mappings, apptrust policy, and priority rewrite tables. It translates kernel DCB app and rewrite state into hardware QoS configuration for each port.

## Important APIs, Types, And Functions
The exported objects/functions are `sparx5_dcbnl_ops` and `sparx5_dcb_init()`. Important helpers include `sparx5_dcb_app_validate()`, `sparx5_dcb_apptrust_validate()`, `sparx5_dcb_app_update()`, `sparx5_dcb_ieee_setapp()`, `sparx5_dcb_ieee_delapp()`, `sparx5_dcb_setapptrust()`, `sparx5_dcb_getapptrust()`, `sparx5_dcb_setrewr()`, and `sparx5_dcb_delrewr()`.

## Control Flow
Initialization attaches DCBNL ops to each netdev, defaults trust order to DSCP plus PCP, and enables DSCP rewrite mode. DCB app set/delete validates selector/protocol/priority, updates kernel DCB state, replicates DSCP mappings globally across all ports, and then rebuilds port QoS. `sparx5_dcb_app_update()` reads default priority, DSCP maps, PCP maps, PCP rewrite maps, and DSCP rewrite maps, enables only trusted classification sources, enables rewrite only when mappings exist, and calls `sparx5_port_qos_set()`.

## State And Persistence
Per-port apptrust state is held in the static `sparx5_port_apptrust[SPX5_PORTS]` pointer table. Mapping and rewrite state is held by the kernel DCB app database and mirrored into hardware QoS registers through `sparx5_port_qos_set()`. No disk persistence exists.

## Dependencies And Integration Points
The file depends on DCBNL, DCB app/rewrite helper APIs, Sparx5 QoS structures and setters, port netdevs, and constants for DSCP/PCP table sizes and priorities.

## Risks And Edge Cases
DSCP mappings are global in hardware but exposed through per-netdev DCB operations, so set/delete replicates across all ports and can fail midway. Apptrust validation is order-sensitive and only supports empty, DSCP, PCP, or DSCP then PCP. Default priority uses the highest set bit from the DCB mask. Static apptrust storage assumes port numbers are below `SPX5_PORTS`.

## Test Signals
Use `dcb app` and apptrust commands for DSCP, PCP, and default priority; test invalid selectors/ranges; verify global DSCP replication across ports; confirm PCP/DSCP rewrite only when trusted and mapped; and check hardware QoS classification with marked traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_dcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_ethtool.c

## Purpose
This file provides Sparx5 ethtool operations and the driver statistics subsystem. It periodically extends hardware 32-bit counters into 64-bit software counters, exposes standard IEEE/RMON stats, exposes custom stats strings/data, delegates link and pause settings to phylink, and reports PTP timestamping capabilities.

## Important APIs, Types, And Functions
Exports are `sparx5_ethtool_ops`, `sparx5_stats_init()`, `sparx5_stats_deinit()`, and `sparx5_get_stats64()`. Important internals include `sparx5_update_counter()`, device/ASM counter readers, XQS queue-stat readers, ANA_AC policer-stat readers, ethtool standard stat callbacks, `sparx5_update_stats()`, and delayed work `sparx5_check_stats_work()`.

## Control Flow
Stats initialization allocates `sparx5->stats`, configures policer and queue counters, creates a single-thread workqueue, and schedules periodic polling. The worker updates every live port. Counter readers choose DEV register blocks for Base-R modes and ASM registers otherwise, then combine normal and PMAC counters. EtHTool callbacks refresh relevant counters before filling standard structures or custom arrays. Link ksettings and pause parameters are delegated to phylink. Timestamp info reports hardware capabilities when a PHC is registered, with a Sparx5-specific fallback when PTP is disabled.

## State And Persistence
The driver keeps `sparx5->stats` as a flat `n_ports_all * num_stats` u64 array. `queue_stats_lock` serializes XQS statistic view selection. Delayed work and workqueue pointers live in `sparx5`. Hardware counters are read and extended but not persisted to disk.

## Dependencies And Integration Points
The file integrates with ethtool, rtnl link stats, phylink, PTP clock registration, Sparx5/ASM/DEV/XQS/ANA register blocks, port mode helpers, and netdev ops that call `sparx5_get_stats64()`.

## Risks And Edge Cases
`sparx5_update_counter()` assumes hardware counters are read often enough to detect one wrap between polls. `sparx5_get_stats64()` does not refresh counters itself, so it can lag the delayed worker. XQS statistic view is shared hardware state, hence the mutex. Stats deinit assumes init completed far enough to create the workqueue. Port mode changes must keep Base-R versus ASM counter selection correct.

## Test Signals
Run `ethtool -S`, standard ethtool stats, `ip -s link`, pause and link-setting operations, PTP timestamp capability queries, long traffic runs to test wrap extension, queue drops, policer drops, and unload while stats work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_fdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_fdma.c

## Purpose
This file implements the common Sparx5 FDMA extraction and injection path for non-LAN969x operation. It allocates descriptor/buffer memory, configures FDMA hardware channels, handles FDMA interrupts, performs NAPI RX processing, injects TX frames with IFH, and starts/stops FDMA.

## Important APIs, Types, And Functions
Exports include `sparx5_fdma_init()`, `sparx5_fdma_deinit()`, `sparx5_fdma_start()`, `sparx5_fdma_stop()`, `sparx5_fdma_handler()`, `sparx5_fdma_reload()`, `sparx5_fdma_injection_mode()`, `sparx5_fdma_napi_callback()`, and `sparx5_fdma_xmit()`. Internal helpers provide dataptr callbacks, channel activation/deactivation, RX frame processing, and RX/TX allocation.

## Control Flow
Initialization resets FDMA, configures CPU ACP caching, programs QS extraction/injection mode and CPU port behavior, initializes RX/TX FDMA structures, and allocates physical FDMA memory. Start adds and enables NAPI using the family `fdma_poll` op, activates RX/TX channels, and enables interrupts. The IRQ handler masks DB interrupts, clears interrupt status, schedules NAPI, and logs/clears FDMA errors. NAPI consumes completed RX descriptors, parses IFH, maps source port to netdev, trims FCS, timestamps PTP, updates stats, sends skbs up the stack, replenishes descriptors, reloads FDMA, and re-enables interrupts. TX copies IFH and skb data into the next descriptor buffer and reloads FDMA.

## State And Persistence
State lives in `sparx5->rx.fdma`, `sparx5->tx.fdma`, RX skb arrays, descriptor indices, physical/coherent FDMA buffers, NAPI state, netdev stats, and FDMA/QS/ASM/QFWD/DSM/HSCH hardware registers. Nothing persists beyond runtime hardware state.

## Dependencies And Integration Points
The file depends on common FDMA helpers, Sparx5 register accessors, IFH parsing, PTP RX timestamping, netdev/NAPI/IRQ APIs, DMA/physical allocation helpers, CPU internal port mapping, and family ops for NAPI poll selection.

## Risks And Edge Cases
RX dataptr uses `virt_to_phys()` on skb data, which relies on platform DMA assumptions compared with DMA mapping APIs. `sparx5_fdma_init()` does not free RX allocation if TX allocation fails. `sparx5_fdma_xmit()` advances the DCB before checking descriptor done and can return `-EINVAL` under descriptor pressure. RX inactive-port data flushes the extraction queue and returns false, potentially ending the poll early. The stop wait condition checks buffer-empty semantics and should be validated against hardware docs.

## Test Signals
Test FDMA start/stop during interface open/close, RX and TX traffic, inactive source-port handling, bridge offload marks, PTP RX timestamps, FDMA error interrupts, descriptor pressure, unload cleanup, and fallback to LAN969x-specific FDMA ops when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_fdma.c -->
