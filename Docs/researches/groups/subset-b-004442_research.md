# Research: subset-b-004442

Work item `subset-b-004442` covers a Sun3 i82586 header, IBM Ethernet Kconfig/Kbuild files, and the IBM eHEA driver. Each section preserves the source path and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sun3_82586.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sun3_82586.h

Purpose: Defines the Sun3 on-board I/O variant of the Intel 82586 Ethernet controller interface. It is a hardware contract header rather than executable code: register bits, controller memory structures, command block layouts, receive/transmit descriptor formats, and status/error masks used by the corresponding Sun3 i82586 driver.

Important APIs, types, and constants: The OBIO control bits `IEOB_NORSET`, `IEOB_ONAIR`, `IEOB_ATTEN`, `IEOB_IENAB`, `IEOB_BUSERR`, and `IEOB_INT` describe board-level reset, attention, interrupt, and transceiver state. `IE_OBIO`, `IE_IRQ`, and `SCP_DEFAULT_ADDRESS` anchor the device's memory/interrupt placement. `struct scp_struct`, `struct iscp_struct`, and `struct scb_struct` model the 82586 initialization path from System Configuration Pointer to Intermediate SCP to System Control Block. `struct rfd_struct` and `struct rbd_struct` describe receive frame and receive buffer descriptors. Command blocks include `nop_cmd_struct`, `iasetup_cmd_struct`, `configure_cmd_struct`, `mcsetup_cmd_struct`, `dump_cmd_struct`, `transmit_cmd_struct`, `tdr_cmd_struct`, and `tbd_struct`. `RUC_*`, `CUC_*`, `ACK_*`, `STAT_*`, `CMD_*`, `RFD_*`, `RBD_*`, `TCMD_*`, and `TDR_*` masks are the vocabulary the driver uses to drive the receive unit, command unit, and transmit diagnostics.

Control flow: The expected driver sequence is: place and populate SCP/ISCP/SCB in 82586-visible memory, let the chip clear `iscp_struct.busy`, configure the SCB command words, issue command-unit actions through command blocks, and operate receive through RFD/RBD rings. Transmit flow points a transmit command at a TBD chain, then starts/resumes the command unit. Receive flow watches RFD completion, follows RBD offsets to packet buffers, and acknowledges SCB interrupt causes with `ACK_*`.

State and persistence: All state is volatile hardware-visible memory. The file defines no functions, allocation, locking, or persistent storage. Descriptor `next`, `cmd_link`, `cbl_offset`, `rfa_offset`, and pointer fields encode the in-memory graph shared with the 82586. Error counters in `scb_struct` and descriptor status bits are accumulated by hardware until consumed by the driver.

Dependencies and integration: Depends on `ETH_ALEN` from Ethernet headers and on the Sun3 i82586 driver using the exact packed hardware layout implied by these C structs. It is derived from the generic `ni52.h` i82586 definitions but specialized for Sun3 OBIO rather than VME.

Risks: The hardware layout is extremely sensitive to structure padding, pointer size, endianness, and 16-bit offset semantics. The header uses native C pointers for hardware-visible addresses, so it only remains correct in the intended architecture/driver context. Misprogramming SCB command/ack bytes can wedge the command or receive unit. Descriptor ring termination and suspend bits must be consistent or RX can run out of resources.

Test signals: Build coverage for the Sun3 i82586 driver, boot/probe on Sun3 hardware or emulator, successful SCP/ISCP initialization, transmit command completion, receive ring wrap, multicast setup, TDR command reporting, SCB error counter reads, and interrupt acknowledge behavior for `STAT_CX`, `STAT_FR`, `STAT_CNA`, and `STAT_RNR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sun3_82586.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/Kconfig

Purpose: Defines the IBM Ethernet vendor menu and top-level selectable IBM network drivers for the kernel networking Kconfig tree.

Important configuration entries: `NET_VENDOR_IBM` is a vendor gate that defaults to `y` and depends on `PPC_PSERIES`, `PPC_DCR`, or `(IBMEBUS && SPARSEMEM)`. `IBMVETH` enables IBM LAN Virtual Ethernet on pSeries. `IBMVETH_KUNIT_TEST` enables KUnit tests for the IBMVETH driver, requiring built-in KUnit and built-in IBMVETH. `source "drivers/net/ethernet/ibm/emac/Kconfig"` includes embedded PowerPC EMAC options. `EHEA` enables the IBM pSeries eHEA adapter driver and depends on `IBMEBUS && SPARSEMEM`. `IBMVNIC` enables IBM Virtual NIC support on pSeries.

Control flow: The file is declarative. The kernel Kconfig frontend evaluates the vendor gate first; when `NET_VENDOR_IBM` is enabled, it exposes IBMVETH, EMAC, EHEA, and IBMVNIC prompts. Selected symbols are consumed by the directory Makefile and subdirectory Makefiles to include the corresponding objects.

State and persistence: Configuration state persists in `.config`, not in this file. The file itself carries dependency topology and help text only. The notable runtime implication is that `CONFIG_EHEA` cannot be selected outside an IBM eBus sparse-memory environment.

Dependencies and integration: Integrates with the global network-device Kconfig hierarchy and the adjacent `drivers/net/ethernet/ibm/Makefile`. The EMAC subtree contributes its own `IBM_EMAC` and feature symbols. IBMVETH and IBMVNIC rely on pSeries platform support; EHEA relies on IBM eBus and sparse memory infrastructure.

Risks: Broad vendor gate defaults can expose prompts in more configurations than strictly needed, but leaf dependencies constrain buildability. `IBMVETH_KUNIT_TEST` requires both KUnit and IBMVETH built in, so module-only IBMVETH configurations will not run that test. EHEA's dependency on sparse memory is essential because its memory-region busmap logic assumes sparsemem sections.

Test signals: Kconfig resolution for pSeries, PPC DCR embedded, IBMEBUS/SPARSEMEM, and unrelated architectures; compile tests for `CONFIG_EHEA=m/y`, `CONFIG_IBM_EMAC=m/y`, `CONFIG_IBMVETH_KUNIT_TEST=y`, and vendor gate disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/Makefile

Purpose: Maps IBM Ethernet Kconfig symbols to object files and subdirectories.

Important build entries: `obj-$(CONFIG_IBMVETH) += ibmveth.o`, `obj-$(CONFIG_IBMVNIC) += ibmvnic.o`, `obj-$(CONFIG_IBM_EMAC) += emac/`, and `obj-$(CONFIG_EHEA) += ehea/` are the only build rules. They delegate EMAC and eHEA compilation to their subdirectory Makefiles.

Control flow: During kbuild traversal, enabled tristate symbols append either built-in or module targets. If `CONFIG_EHEA=m`, the `ehea/` subdirectory produces the `ehea.ko` module through its own Makefile. If disabled, the directory is skipped.

State and persistence: No runtime state. The persistent effect is kernel build output composition based on `.config`.

Dependencies and integration: Coupled to `drivers/net/ethernet/ibm/Kconfig` symbol names and to existing subdirectories/files. It integrates IBM Ethernet drivers into the larger `drivers/net/ethernet/Makefile` traversal.

Risks: Misspelled symbols or directory names would silently drop drivers from builds. The file contains no ordering constraints beyond kbuild line order; inter-driver dependencies must be encoded in Kconfig.

Test signals: `make drivers/net/ethernet/ibm/` under configurations enabling each symbol; module and built-in builds; `make M=drivers/net/ethernet/ibm/ehea` for EHEA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/Makefile

Purpose: Defines the composite object list for the IBM eHEA Ethernet driver.

Important build entries: `ehea-y = ehea_main.o ehea_phyp.o ehea_qmr.o ehea_ethtool.o` combines the netdev/core, hypervisor-call wrapper, queue/memory-region, and ethtool units into one driver. `obj-$(CONFIG_EHEA) += ehea.o` exposes that composite as built-in or module depending on `CONFIG_EHEA`.

Control flow: kbuild compiles the four source files and links them into `ehea.o`. The module entry/exit symbols live in `ehea_main.o`; the remaining units provide referenced helpers and exported internal interfaces.

State and persistence: No runtime state. Build state follows `.config` and kbuild outputs.

Dependencies and integration: Depends on `CONFIG_EHEA` from the parent Kconfig and on all four source files sharing internal headers `ehea.h`, `ehea_qmr.h`, `ehea_hw.h`, and `ehea_phyp.h`.

Risks: Removing any object from `ehea-y` would break link-time references: `ehea_main.o` needs PHYP wrappers, QMR queue/MR helpers, and ethtool setup; `ehea_qmr.o` needs PHYP calls. The Makefile has no conditional feature splits, so all code must compile on every EHEA-supported configuration.

Test signals: `CONFIG_EHEA=y` vmlinux link, `CONFIG_EHEA=m` module link, modpost symbol checks, and targeted `make M=drivers/net/ethernet/ibm/ehea`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea.h

Purpose: Central private header for the IBM eHEA driver. It defines driver identity, queue sizing, adapter/port/resource structures, bitfield helpers, memory-region busmap structures, multicast bookkeeping, kdump handle tracking, state flags, and cross-file prototypes.

Important APIs, types, and constants: `DRV_NAME`, `DRV_VERSION`, `EHEA_CAPABILITIES`, queue-size constants, packet-size constants, speed constants, BCMC registration flags, memory-region constants, and `EHEA_WATCH_DOG_TIMEOUT` configure driver behavior. `EHEA_BMASK_*` helpers pack and unpack IBM-style bitfields. `struct hw_queue` abstracts page-backed hardware queues. `struct ehea_qp_init_attr`, `ehea_eq_attr`, and `ehea_cq_attr` are PHYP allocation contracts. `struct ehea_adapter` owns the logical adapter, notification EQ, kernel MR, port array, capabilities, and adapter list node. `struct ehea_port` is the netdev-private port state. `struct ehea_port_res` represents one default queue pair and its NAPI, QP/CQ/EQ handles, shared MRs, skb rings, counters, and TX availability state.

Control flow: The header is included by all eHEA units. `ehea_main.c` allocates and mutates adapters, ports, and port resources; `ehea_qmr.c` fills queue/MR internals; `ehea_phyp.c` uses init attributes to marshal hcalls; `ehea_ethtool.c` reads port fields and calls exported sensing/speed helpers.

State and persistence: All state is volatile kernel/firmware state. Persistent-like runtime records include `ehea_fw_handle_array` and `ehea_bcmc_reg_array` used for crash cleanup and re-registration bookkeeping, but they are in-memory only. Port state tracks carrier, speed, MAC, multicast list, queue statistics, reset counts, flags, and work items.

Dependencies and integration: Depends on Linux module, ethtool, vmalloc, VLAN, platform-device, ibmebus, and I/O headers. It is tied to Power/IBM eBus firmware interfaces and to the netdevice stack through `struct net_device`, NAPI, skb arrays, workqueues, wait queues, and link state.

Risks: Queue constants and encoded SG sizes must agree with PHYP allocation and WQE layout. `EHEA_BMASK_IBM` is used everywhere for register/hcall packing; incorrect positions break firmware interaction. `EHEA_MAX_PORT_RES` and `EHEA_MAX_PORTS` bound arrays that are indexed by firmware queue tokens and probed ports. Shared state such as `swqe_avail`, reset flags, and multicast arrays has concurrency exposure across IRQ, NAPI, workqueue, notifier, and sysfs paths.

Test signals: Compile all eHEA units, inspect structure size/layout assumptions on supported Power configs, open/close ports with multiple default QPs, ethtool stats and speed operations, memory hotplug re-registration, crash-shutdown cleanup, multicast/allmulti/promisc changes, and reset work scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_ethtool.c

Purpose: Provides ethtool operations for eHEA netdevices: link settings, driver info, message level, driver-private statistics, and autonegotiation restart.

Important APIs and functions: `ehea_get_link_ksettings()` refreshes port attributes through `ehea_sense_port_attr()`, converts eHEA speed/duplex state to ethtool `SPEED_*` and `DUPLEX_*`, and populates supported/advertising link modes. `ehea_set_link_ksettings()` maps requested ethtool speed/duplex/autoneg settings to PHYP speed constants and calls `ehea_set_portspeed()`. `ehea_nway_reset()` requests autonegotiation. `ehea_get_drvinfo()`, `ehea_get_msglevel()`, and `ehea_set_msglevel()` expose metadata and debug mask state. `ehea_get_strings()`, `ehea_get_sset_count()`, and `ehea_get_ethtool_stats()` expose 24 statistics including reset count, checksum errors, receive errors, queue stops, and per-port-resource free SWQEs. `ehea_set_ethtool_ops()` installs the static ops table.

Control flow: `ehea_setup_single_port()` calls `ehea_set_ethtool_ops()` before registering the netdev. Userspace ethtool calls enter this file, then delegate hardware-sensitive operations to `ehea_main.c` helpers that perform PHYP queries/modifications. Statistics are aggregated over `EHEA_MAX_PORT_RES`, not only active queues, with inactive queue counters reading as zero.

State and persistence: Reads and writes runtime `struct ehea_port` fields: `port_speed`, `full_duplex`, `autoneg`, `msg_enable`, `sig_comp_iv`, `resets`, and each `port_res[].p_stats`/`swqe_avail`. No persistent storage. `set_msglevel` persists only for the lifetime of the netdev.

Dependencies and integration: Depends on `ehea.h`, `ehea_phyp.h`, ethtool link-mode conversion helpers, and netdevice carrier state. It integrates tightly with PHYP-backed port sensing and speed modification.

Risks: `ehea_get_link_ksettings()` reports different supported modes based on the current sensed speed; unusual hardware may have capabilities broader than the current link. `ehea_set_link_ksettings()` rejects half-duplex 1G/10G but relies on PHYP for authority checks. Stats read concurrent counters without locking, so values are approximate.

Test signals: `ethtool <dev>`, `ethtool -s` for autoneg/10/100/1000/10000 combinations, permission-denied speed changes from hypervisor, `ethtool -S` after RX/TX/checksum errors, and msglevel get/set round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_hw.h

Purpose: Defines eHEA hardware register-map layouts for queue pairs, memory regions, queue-pair event data, completion queues, and event queues, plus low-level MMIO access helpers and queue/CQ doorbell helpers.

Important APIs and types: `struct ehea_qptemm`, `ehea_mrmwmm`, `ehea_qpedmm`, `ehea_cqtemm`, and `ehea_eqtemm` describe firmware-provided resource pages. Offset macros such as `QPTEMM_OFFSET()`, `MRMWMM_OFFSET()`, `QPEDMM_OFFSET()`, `CQTEMM_OFFSET()`, and `EQTEMM_OFFSET()` produce byte offsets for MMIO access. `epa_load()`, `epa_store()`, and `epa_store_acc()` wrap raw 64-bit MMIO reads/writes. `ehea_update_sqa()`, `ehea_update_rq1a()`, `ehea_update_rq2a()`, `ehea_update_rq3a()`, `ehea_update_feca()`, `ehea_reset_cq_n1()`, and `ehea_reset_cq_ep()` ring hardware queues or reset completion notification state.

Control flow: QMR allocation maps EPAs through PHYP. Runtime TX posts an SWQE then calls `ehea_update_sqa()`. RX refill paths post RWQEs and call the RQ adder helpers. NAPI completion calls CQ reset helpers to re-enable completion events. Completion processing calls `ehea_update_feca()` after consuming CQEs.

State and persistence: The structs represent hardware/firmware state in MMIO pages, not regular kernel-owned persistent state. The helper writes update producer/consumer accounting and event state inside eHEA resources. `epa_store()` does a readback to synchronize writes to eHEA; `epa_store_acc()` skips that synchronization for accumulator-style writes.

Dependencies and integration: Depends on `struct h_epa`, `struct ehea_qp`, and `struct ehea_cq` from `ehea.h`, and on raw Power I/O helpers. It is included by both PHYP and QMR code and is central to queue doorbell interaction.

Risks: Register layouts are fixed hardware ABI. Wrong offsets or bit masks can write the wrong MMIO location. The RQ helper names and masks must match hardware queue fields; subtle mismatches would show as lost RX refills. MMIO ordering is critical: `epa_store_acc()` assumes accumulator writes do not need readback, while `ehea_post_swqe()` separately issues `iosync()`.

Test signals: TX completion under load, RX refill on RQ1/RQ2/RQ3, NAPI completion rearming interrupts, CQ event pending behavior, and debug instrumentation confirming expected MMIO offsets against firmware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_main.c

Purpose: Main eHEA netdevice/platform driver. It owns module parameters, IBM eBus probing/removal, logical-port setup, netdev operations, TX/RX data paths, NAPI, IRQ handling, multicast/VLAN/filter management, PHYP port configuration, queue-pair activation/reset, memory hotplug re-registration, crash/reboot cleanup, sysfs port add/remove, and module init/exit.

Important APIs and functions: Module parameters tune queue sizes, debug mask, carrier propagation, and multi-queue use. `ehea_probe_adapter()` registers memory hooks, reads the adapter handle, queries adapter attributes, creates the notification EQ, sets up sysfs and ports, requests the NEQ IRQ, and schedules initial event handling. `ehea_setup_single_port()` allocates a multi-queue netdev, senses port attributes, registers a child Open Firmware device, sets features and ethtool ops, and registers the netdev. Netdev ops include `ehea_open()`, `ehea_stop()`, `ehea_start_xmit()`, `ehea_get_stats64()`, `ehea_set_mac_addr()`, `ehea_set_multicast_list()`, VLAN add/kill, and TX timeout. `ehea_up()` creates QPs/CQs/EQs/MRs, configures the port, registers IRQs, activates QPs, fills receive queues, and registers broadcast filters. `ehea_down()` reverses that state. `ehea_poll()` processes send completions and RX completions.

Control flow: Probe builds adapter and port shells but queue resources are created on open. Open calls `ehea_up()`, enables NAPI, and starts TX queues. RX interrupt schedules NAPI; NAPI drains send CQEs, drains RQ1-backed receive completions, refills RQ1/RQ2/RQ3, rearms CQ events, and returns budget. TX selects a port resource by skb queue mapping, reserves an SWQE, chooses immediate-only SWQE3 for small packets or descriptor SWQE2 for larger/fragments/TSO, maps addresses through `ehea_map_vaddr()`, posts the SWQE, and stops the queue on low credits. Link and malfunction events arrive on the notification EQ and are parsed by `ehea_neq_tasklet()`. Reset work serializes with `port_lock`, tears down and rebuilds the port, restores multicast filters, reenables NAPI, and wakes queues. Memory hotplug uses `ehea_mem_notifier()` to stop transfer, update the busmap, re-register adapter MRs, regenerate shared MRs, update queued receive addresses, check send queues, and resume.

State and persistence: Global runtime state includes `adapter_list`, `ehea_driver_flags`, `dlpar_mem_lock`, `ehea_fw_handles`, and `ehea_bcmc_regs`. Per-adapter state stores PHYP handle, ports, NEQ, kernel MR, protection domain, and active port count. Per-port state stores netdev, multicast list, QP EQ, reset/stats work, locks, speed/link/MAC, queue count, flags, and wait queues. Per-port-resource state stores queues, CQs, shared MRs, skb arrays, counters, SWQE credits, and NAPI. No disk persistence; sysfs `probe_port` and `remove_port` mutate runtime port presence.

Dependencies and integration: Depends on IBM eBus/Open Firmware, Power hypervisor calls through `ehea_phyp.c`, queue/MR helpers from `ehea_qmr.c`, ethtool setup, Linux netdevice/NAPI/VLAN/checksum/TSO APIs, memory/reboot/crash notifiers, and kernel workqueues/tasklets/IRQs.

Risks: This file has the highest concurrency and recovery risk. TX/RX share queue state across xmit, IRQ, NAPI, reset work, close, and memory hotplug. Memory hotplug re-registration is invasive and must stop transfers before invalidating MRs. `ehea_start_xmit()` assumes `ehea_map_vaddr()` succeeds for send buffers; invalid mappings would program bad descriptors. Filter registration and crash cleanup depend on `ehea_bcmc_regs` staying current. Queue counts from firmware must not exceed fixed arrays. Error paths during bring-up must free partial QP/CQ/EQ/MR/skb state in the right order.

Test signals: Adapter probe/remove, logical port sysfs add/remove, open/close cycles, multi-queue TX/RX traffic, small immediate TX, fragmented/TSO TX, VLAN insert/extract/filter, multicast/allmulti/promisc changes, ethtool speed changes, link up/down NEQ events, QP affiliated errors, TX timeout reset, memory online/offline, kexec crash handler cleanup, reboot notifier, and failure injection for IRQ/resource/MR allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_phyp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_phyp.c

Purpose: Implements the eHEA driver's Power hypervisor-call wrapper layer. It packs driver data structures into H_CALL register arguments, retries long-busy calls, logs failures, decodes outputs, maps resource EPAs, and exposes typed helpers for QP/CQ/EQ/MR/port/event operations.

Important APIs and functions: `ehea_plpar_hcall_norets()` and `ehea_plpar_hcall9()` wrap `plpar_hcall_norets()` and `plpar_hcall9()`, retrying up to five times on `H_IS_LONG_BUSY()` and sleeping for the hypervisor-provided delay. Allocation helpers include `ehea_h_alloc_resource_qp()`, `ehea_h_alloc_resource_cq()`, `ehea_h_alloc_resource_eq()`, and `ehea_h_alloc_resource_mr()`. Other helpers query/modify QPs and ports, register queue/MR pages, register shared MRs, disable QPs, free resources, register/deregister broadcast/multicast filters, reset notification events, query adapter attributes, and fetch error data.

Control flow: QMR code calls allocation helpers, then registers pages. Main driver calls port/query/modify helpers during probe, open, link settings, filters, VLANs, QP activation, and reset. All helpers translate C fields into bit-packed H_CALL parameters using `EHEA_BMASK_SET()` and decode outputs back into init attributes, handles, lkeys, page counts, interrupt service tokens, or PHYP status.

State and persistence: The file itself stores no long-lived state. It mutates caller-owned structures such as `ehea_qp_init_attr`, `ehea_cq_attr`, `ehea_eq_attr`, and `ehea_mr`, and maps EPAs into `struct h_epas`. Firmware resources persist in the hypervisor until freed by matching calls.

Dependencies and integration: Depends on `asm/hvcall.h`, `plpar_hcall*`, PHYP H_CALL numbers, `ehea_phyp.h` control block definitions, `ehea_hw.h` EPA mapping helpers, and `ehea.h` attributes. It is the only eHEA layer that should know exact register argument packing for PHYP calls.

Risks: Argument packing errors can allocate unusable resources or modify the wrong port/QP state. Long-busy retry is bounded; persistent busy returns `H_BUSY` to callers. Some `H_AUTHORITY` errors for port speed/jumbo/promisc-like operations are intentionally not logged as generic failures. `hcp_epas_ctor()` mapping relies on returned physical addresses and page alignment behavior.

Test signals: Resource allocation/free for EQ/CQ/QP/MR, page registration completion status (`H_PAGE_REGISTERED` then `H_SUCCESS`), QP state transitions, port query/modify authority failures, BCMC register/deregister, long-busy retry behavior, and H_CALL failure logging with useful arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_phyp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_phyp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_phyp.h

Purpose: Declares the eHEA PHYP ABI used by the driver: notification event masks, H_CALL control block layouts, selection masks, speed/receive-control constants, resource-operation prototypes, and EPA constructor/destructor helpers.

Important APIs and types: `hcp_epas_ctor()` maps hypervisor-provided resource pages into kernel virtual address space; `hcp_epas_dtor()` unmaps them. Control blocks `hcp_modify_qp_cb0`, `hcp_modify_qp_cb1`, `hcp_query_ehea`, and `hcp_ehea_port_cb0` through `cb7` model PHYP query/modify payloads. Masks such as `H_QPCB0_*`, `H_PORT_CB0_*`, `H_PORT_CB4_*`, `H_REGBCMC_*`, `NEQE_*`, and `NELR_*` define exact bitfields. Prototypes expose every wrapper implemented in `ehea_phyp.c`.

Control flow: `ehea_main.c` allocates a zeroed page for the relevant control block, fills selected fields, and calls query/modify wrappers with a category and selection mask. `ehea_phyp.c` packs the category, port number, resource handles, and physical control-block address into H_CALL registers. Notification event bits are parsed by `ehea_parse_eqe()` and reset through `ehea_h_reset_events()`.

State and persistence: The header defines data exchanged with firmware; it does not own state. `hcp_query_ehea` returns adapter capability state. Port control blocks reflect or request firmware state for MAC, receive control, VLAN filters, counters, jumbo/speed, promiscuous default queue, and default unicast queue.

Dependencies and integration: Depends on Linux delay, Power hypervisor call definitions, and eHEA core/hardware headers. It is the shared contract between the PHYP wrapper implementation and the main/QMR driver code.

Risks: Control block field ordering and selection masks are firmware ABI. Incorrect category/mask pairing can modify unrelated settings. `hcp_epas_ctor()` does pointer arithmetic on an `__iomem` mapping and assumes PAGE_SIZE/PAGE_MASK handling is correct for the platform. Speed constants must stay aligned with ethtool conversion and port sensing.

Test signals: Port attribute sensing, speed modification, VLAN filter changes, jumbo enable/query, promiscuous default-QPN changes, adapter capability query, NEQ event parsing, QP modify/query state transitions, and sparsemem builds validating control-block sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_phyp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_qmr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_qmr.c

Purpose: Implements eHEA queue and memory-region management. It allocates page-backed hardware queues, registers queue pages with PHYP, creates/destroys EQ/CQ/QP resources, builds the global eHEA busmap over system RAM, registers adapter memory regions, derives shared memory regions for port resources, maps kernel virtual addresses into eHEA bus addresses, and fetches/prints hardware error data.

Important APIs and functions: `ehea_create_eq()`, `ehea_create_cq()`, and `ehea_create_qp()` allocate firmware resources, allocate software queue pages, register pages, reset queue iterators, and return typed resources. Matching destroy functions free PHYP resources and queue pages, using force-free after `H_R_STATE` with error data. `ehea_create_busmap()`, `ehea_add_sect_bmap()`, `ehea_rem_sect_bmap()`, and `ehea_destroy_busmap()` manage the global busmap. `ehea_reg_kernel_mr()` allocates and registers the adapter-wide MR over mapped RAM sections. `ehea_gen_smr()` registers shared MRs for send/receive queues. `ehea_map_vaddr()` converts a kernel virtual address to the bus address used in WQEs. `ehea_error_data()` retrieves and dumps PHYP error state.

Control flow: On first adapter probe, main registers memory hooks and calls `ehea_create_busmap()`. When a port opens, adapter MR registration happens before per-port resources; each port resource creates EQ/CQs/QP, then shared MRs. RX/TX WQE construction calls `ehea_map_vaddr()` for skb data and fragments. Memory hotplug updates the busmap under `ehea_busmap_mutex`, then `ehea_main.c` re-registers MRs and updates queued WQEs. Destroy paths unmap EPAs, free resources, and release queue pages.

State and persistence: Global `ehea_bmap` is a three-level sparse map of valid memory sections to contiguous eHEA bus addresses starting at `EHEA_BUSMAP_START`; `ehea_mr_len` tracks MR length. Queue state lives in `struct hw_queue` page arrays and offsets. Firmware resource handles and lkeys are stored in caller-owned `ehea_eq`, `ehea_cq`, `ehea_qp`, and `ehea_mr`.

Dependencies and integration: Depends on Linux memory walking/hotplug primitives, page allocation, slab allocation, PHYP wrappers, eHEA hardware queue helpers, sparsemem `SECTION_SIZE_BITS`, and hugepage detection. It is the memory translation layer for the main TX/RX path.

Risks: Busmap correctness is critical; invalid mappings lead to bad DMA-like addresses in WQEs. Huge pages are deliberately skipped in busmap creation for 16GB chunks, so memory layout assumptions matter. `hw_queue_ctor()` divides kernel pages into eHEA queue pages and must free only base allocations. Page registration must observe `H_PAGE_REGISTERED` intermediate status and `H_SUCCESS` on completion. Memory hotplug races are mitigated by external locking but remain a high-risk integration point.

Test signals: EQ/CQ/QP create/destroy under normal and forced-free paths, queue wrap/toggle behavior, page registration failure injection, adapter MR registration over fragmented memory, memory online/offline section add/remove, hugepage exclusion, `ehea_map_vaddr()` returning valid addresses for skb data/frags, and error-data dumps after QP/CQ/EQ faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_qmr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_qmr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_qmr.h

Purpose: Defines eHEA queue/memory-region constants, WQE/CQE/EQE formats, work-request ID encoding, error masks, queue iterator helpers, and QMR public prototypes.

Important APIs and types: Page and section constants include `EHEA_PAGESIZE`, `EHEA_SECTSIZE`, `EHEA_PAGES_PER_SECTION`, `EHEA_HUGEPAGE_SIZE`, and a compile-time assertion that kernel section size is large enough. `struct ehea_vsgentry`, `ehea_swqe`, `ehea_rwqe`, `ehea_cqe`, and `ehea_eqe` describe send, receive, completion, and event entries. `EHEA_WR_ID_*` encodes completion type, index, count, and refill credits. TX flags include checksum, TSO, VLAN insert, immediate data, descriptors, and purge. Inline queue helpers calculate current entries, increment with toggle-state wrap, validate CQ/EQ entries, fetch SWQEs/RWQEs, post SWQEs, and poll RQ1/CQs.

Control flow: `ehea_main.c` uses `ehea_get_swqe()` and `ehea_post_swqe()` in TX, `ehea_get_next_rwqe()` in RX refill, `ehea_poll_rq1()`/`ehea_inc_rq1()` in RX completion, and `ehea_poll_cq()`/`ehea_inc_cq()` in send completion. `ehea_qmr.c` implements the resource and MR prototypes declared here.

State and persistence: Queue state is held in `struct hw_queue` from `ehea.h`; inline helpers mutate `current_q_offset` and `toggle_state`. WQE `wr_id` carries software state through hardware completions, tying CQEs back to skb arrays and refill credit accounting. No persistent storage.

Dependencies and integration: Depends on Linux prefetch helpers, `ehea.h`, and `ehea_hw.h`. It bridges hardware entry formats to the netdev data path in `ehea_main.c`.

Risks: Queue toggle validation is central to detecting valid CQEs/EQEs; off-by-one or wrong entry size causes missed or repeated completions. `ehea_get_swqe()` computes indices from queue offset and SG encoding, so it must match `sq_skba` sizing. WR_ID field packing must remain consistent across TX post, RX refill, and completion processing. Error masks decide whether RX/TX errors trigger port resets.

Test signals: Queue wrap at ring boundaries, valid-bit toggle transitions, SWQE2/SWQE3 completion handling, RX RQ2/RQ3 skb-index recovery, refill credit accounting, fatal CQE reset paths, and compile-time section-size assertion on target configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/ehea_qmr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/Kconfig

Purpose: Defines Kconfig options for the IBM EMAC Ethernet family used on 4xx embedded PowerPC chips and Axon southbridge systems.

Important configuration entries: `IBM_EMAC` is the main tristate, depends on `PPC_DCR`, and selects `CRC32` and `PHYLIB`. Tunables `IBM_EMAC_RXB`, `IBM_EMAC_TXB`, `IBM_EMAC_POLL_WEIGHT`, and `IBM_EMAC_RX_COPY_THRESHOLD` configure receive buffers, transmit buffers, NAPI/MAL polling weight, and RX copy threshold. `IBM_EMAC_DEBUG` enables debugging. Hidden platform-selected booleans include `IBM_EMAC_ZMII`, `IBM_EMAC_RGMII`, `IBM_EMAC_TAH`, `IBM_EMAC_EMAC4`, `IBM_EMAC_NO_FLOW_CTRL`, `IBM_EMAC_MAL_CLR_ICINTSTAT`, and `IBM_EMAC_MAL_COMMON_ERR`.

Control flow: This file is sourced from the IBM vendor Kconfig. User-visible options configure the EMAC driver; hidden booleans are selected by SoC/platform code to include connector/accelerator variants and hardware quirks. The EMAC Makefile consumes those symbols to include optional objects.

State and persistence: Values persist in `.config`. Numeric tunables shape compile-time constants or runtime defaults in the EMAC driver; this file itself has no runtime state.

Dependencies and integration: Depends on PowerPC DCR support and integrates with PHYLIB, CRC32, and the IBM EMAC Makefile. Hidden symbols map directly to optional object files such as `zmii.o`, `rgmii.o`, and `tah.o`.

Risks: Buffer/tuning options accept arbitrary integer values in Kconfig; downstream code must validate or tolerate unusual values. Hidden platform selects must match actual hardware topology or required bridge objects will be omitted. The comment notes these options should be selected by processor/platform definitions, so manual edits can create unsupported builds.

Test signals: `CONFIG_IBM_EMAC=m/y` builds, platform configs selecting ZMII/RGMII/TAH/EMAC4, unusual buffer counts and poll weight builds, debug builds, and PHYLIB dependency resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/Makefile

Purpose: Builds the IBM PowerPC 4xx on-chip EMAC driver and optional hardware-support objects.

Important build entries: `obj-$(CONFIG_IBM_EMAC) += ibm_emac.o` defines the composite driver. `ibm_emac-y := mal.o core.o phy.o` always includes MAL, core, and PHY support. Conditional additions include `zmii.o`, `rgmii.o`, and `tah.o` when `CONFIG_IBM_EMAC_ZMII`, `CONFIG_IBM_EMAC_RGMII`, or `CONFIG_IBM_EMAC_TAH` are selected.

Control flow: kbuild enters this Makefile when the parent directory includes `emac/`. The composite object includes optional bridge/accelerator files based on hidden Kconfig symbols selected by platform code.

State and persistence: No runtime state. Build artifacts persist only in the kernel build directory.

Dependencies and integration: Coupled to `ibm/emac/Kconfig` and to source files in the EMAC subdirectory. The base object set implies the EMAC driver always needs MAL DMA management, the core netdev implementation, and PHY handling.

Risks: Optional hardware files must be included when hardware requires them; otherwise the driver can compile but lack required register support. Conversely, unnecessary optional objects may introduce references unavailable on a given platform if Kconfig selects are wrong.

Test signals: Build `CONFIG_IBM_EMAC` with no optional bridges, with each optional bridge alone, and with combined ZMII/RGMII/TAH selections; module and built-in links; platform defconfig coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/Makefile -->
