# Research: subset-b-004509

This grouped report covers Marvell Octeon EP VF queue/register files and OcteonTX2/CN20K RVU Admin Function files. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_regs_cn9k.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_regs_cn9k.h

Purpose: Defines CN93/CN9K VF PCI config, input queue, output queue, and PF/VF mailbox register offsets for the Octeon EP VF Ethernet driver. It is a pure hardware contract header: no code, persistence, or allocation, but every macro feeds MMIO register setup in chip-specific VF setup code and queue paths.

Important APIs/types/functions: The exported surface is macro-only. `CN93_VF_RING_OFFSET` spaces per-ring register windows by bit 17. `CN93_VF_SDP_R_IN_*()` macros compute input-ring control, enable, descriptor base, ring size, doorbell, counters, interrupt levels, packet and byte counter addresses. `CN93_VF_SDP_R_OUT_*()` mirrors that for output rings. `CN93_VF_R_IN_CTL_*` and `CN93_VF_R_OUT_CTL_*` define control bits for idle, 64-byte instruction mode, read size, endian/swap behavior, interrupt mode, and error/status fields. Mailbox macros expose PF-to-VF data, PF-to-VF interrupt, VF-to-PF data, and interrupt enable/status bits.

Control flow and integration: Higher-level CN9K device code includes this header when populating `hw_ops` register callbacks. Setup code writes descriptor DMA bases and sizes, enables queues, rings doorbells, and polls counts through these offsets. Mailbox code uses the mailbox register triplet to exchange PF/VF control messages.

State and persistence: The header models volatile hardware state only. Counter, doorbell, enable, control, and mailbox fields persist in device registers until reset or rewritten; the driver must treat them as MMIO state rather than cached software state.

Dependencies: Requires kernel bit helpers such as `BIT_ULL` from included transitive headers. It depends on CN93/CN9K register layout remaining stable and aligned with firmware/hardware documentation.

Risks: An incorrect base, ring stride, or bit mask breaks DMA queue setup and can produce silent traffic loss or device wedging. This file lacks compile-time validation against a register specification, so cross-chip copy/paste drift is the main risk.

Test signals: Build coverage should verify macro visibility through CN9K code. Runtime signals are successful probe, queue enable, Tx/Rx traffic, mailbox exchange, interrupt delivery, and monotonically increasing packet/byte counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_regs_cn9k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_regs_cnxk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_regs_cnxk.h

Purpose: Defines CNXK VF register offsets and bit masks for the Octeon EP VF Ethernet driver. It is the CNXK counterpart to the CN93 header and supplies register address macros for input/output rings, queue watermarks, error type reporting, counters, and PF/VF mailbox communication.

Important APIs/types/functions: The file exports macros only. `CNXK_VF_RING_OFFSET` is the per-ring stride. `CNXK_VF_SDP_R_IN_*()` and `CNXK_VF_SDP_R_OUT_*()` produce MMIO offsets for ring control, enable, base, size, doorbell, count, interrupt level, packet counter, byte counter, output watermark, and `CNXK_VF_SDP_R_ERR_TYPE()`. Control masks define rings-per-VF fields, 64-byte instruction mode, read size, idle bits, swap/relax-order bits, and output interrupt mode. Mailbox macros define PF-to-VF data/interrupt and VF-to-PF data registers plus enable/status bits.

Control flow and integration: CNXK-specific VF setup code uses these macros behind `hw_ops` to initialize IQ/OQ registers, post credits and doorbells, poll hardware progress, and service mailbox interrupts. Compared with CN93, CNXK adds an error-type register and shifts the output enable address after the output watermark register, so callers must choose the correct chip header.

State and persistence: All represented state is volatile MMIO hardware state. Software queue structures cache pointers to these registers, but the authoritative state is in hardware until device reset or explicit writes.

Dependencies: Requires Linux bit macros and inclusion from the Octeon EP VF driver family. It depends on CNXK silicon/firmware register ABI compatibility.

Risks: Register layout differences from CN93 are subtle. Accidentally using CN93 offsets on CNXK, especially for output enable/watermark, can misconfigure receive rings. Error-type exposure is useful but only if consumers correctly read and decode it.

Test signals: Chip-specific probe must map correct offsets, queues must transition to enabled state, Rx credits and Tx doorbells must move traffic, mailbox interrupts must arrive, and CNXK error registers should remain clear under normal traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_regs_cnxk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_rx.c

Purpose: Implements Octeon EP VF receive queue lifecycle and NAPI receive processing. It allocates output queue descriptor rings and page-backed receive buffers, publishes credits to hardware, converts completed descriptors into SKBs, handles multi-buffer packets, applies checksum status from firmware metadata, and refills descriptors.

Important APIs/types/functions: Public entry points are `octep_vf_setup_oqs()`, `octep_vf_oq_dbell_init()`, `octep_vf_free_oqs()`, and `octep_vf_oq_process_rx()`. Internal helpers include `octep_vf_oq_fill_ring_buffers()`, `octep_vf_oq_refill()`, `octep_vf_setup_oq()`, `octep_vf_oq_free_ring_buffers()`, `octep_vf_free_oq()`, `octep_vf_oq_check_hw_for_pkts()`, `octep_vf_oq_next_idx()`, and `__octep_vf_oq_process_rx()`.

Control flow: Setup loops over active I/O rings, allocates `struct octep_vf_oq`, coherent descriptor memory, `buff_info`, and one page per descriptor, then calls `hw_ops.setup_oq_regs()`. Runtime processing reads `pkts_sent_reg`, updates pending packet count, processes up to the NAPI budget, unmaps consumed pages, reads the big-endian length header, optionally consumes the 8-byte extended offload header, builds an SKB from the page, attaches fragments for packets larger than a single buffer, sets protocol/checksum state, and calls `napi_gro_receive()`. Refill allocates pages for used descriptors and writes descriptor credits after an `smp_wmb()`.

State and persistence: Queue state lives in `oct->oq[]`, `oct->num_oqs`, descriptor DMA memory, `buff_info`, ring indices, `pkts_pending`, `last_pkt_count`, `refill_count`, and per-OQ stats. Hardware state is accessed through cached MMIO register pointers. Pages transfer ownership from driver to device and then back to SKB/network stack.

Dependencies and integration: Uses PCI DMA APIs, page allocation, NAPI/GRO, `net_device` features, firmware capability `oct->fw_info.rx_ol_flags`, config macros from `octep_vf_config.h`, and hardware callbacks from `oct->hw_ops`. It is called from the main driver’s open/close and poll paths.

Risks: Packet length and fragment handling are trust boundaries from hardware; bad lengths could overrun assumptions if firmware misbehaves. The skb-allocation failure path for multi-buffer packets must unmap all fragments correctly. Counter wrap handling assumes the hardware counter can be cleared safely near `0xF0000000`. Refill failures reduce credits and can stall Rx if allocation pressure persists.

Test signals: Probe/open should allocate all OQs, `octep_vf_oq_dbell_init()` should credit all descriptors, NAPI should receive single-buffer and jumbo/multi-fragment frames, checksum-offload traffic should set `CHECKSUM_UNNECESSARY` only when verified, allocation-failure injection should increment `alloc_failures`, and close/remove should leave no DMA mappings or pages leaked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_rx.h

Purpose: Declares the receive-side data formats and state containers for the Octeon EP VF driver. It documents the hardware output queue descriptor format, hardware response headers, receive offload bits, per-buffer bookkeeping, per-queue stats, interface stats, and the software output queue object.

Important APIs/types/functions: `struct octep_vf_oq_desc_hw` is the 16-byte hardware descriptor containing a DMA buffer pointer and currently unused info pointer. `struct octep_vf_oq_resp_hw` is the big-endian 8-byte length header written at the start of each received buffer. `struct octep_vf_oq_resp_hw_ext` carries optional firmware checksum/offload flags. `struct octep_vf_rx_buffer` tracks the backing page and decoded length. `struct octep_vf_oq_stats`, `struct octep_vf_iface_rx_stats`, and `struct octep_vf_oq` hold stats and queue state. Macros define descriptor/response sizes and checksum/offload flag tests.

Control flow and integration: `octep_vf_rx.c` uses these structures to allocate coherent descriptor rings, DMA-map pages into descriptors, parse hardware response headers, manage host read/refill indices, and update stats. The main driver and ethtool paths consume stats structures. Firmware capability bits decide whether the extended response header is present.

State and persistence: `struct octep_vf_oq` is the persistent runtime object for an Rx queue while the network device is open. It links software indices, stats, descriptor memory, DMA addresses, register pointers, NAPI context, and queue configuration. The hardware descriptor and response structs define shared-memory state exchanged through DMA.

Dependencies: Requires Linux DMA, page, NAPI, and networking types supplied by surrounding includes. The `static_assert()` checks bind C layout to the hardware ABI.

Risks: Bitfield and structure layout must match hardware and compiler expectations; the static size checks help but cannot validate endian interpretation or bit ordering. `max_single_buffer_size` depends on response header sizes matching firmware. Misinterpreted checksum flags could mark corrupt packets as valid.

Test signals: Compile-time structure size assertions, Rx with and without firmware offload header support, checksum-offload validation, jumbo frame fragmentation, and ethtool/stat reads are the strongest coverage points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_tx.c

Purpose: Implements Octeon EP VF transmit input queue resource setup, teardown, pending cleanup, and completion processing. It does not build/send Tx descriptors itself in this file; it manages queue memory and reclaims SKBs once hardware consumes posted instructions.

Important APIs/types/functions: Public functions are `octep_vf_iq_process_completions()`, `octep_vf_clean_iqs()`, `octep_vf_setup_iqs()`, and `octep_vf_free_iqs()`. Internal helpers are `octep_vf_iq_reset_indices()`, `octep_vf_iq_free_pending()`, `octep_vf_setup_iq()`, and `octep_vf_free_iq()`.

Control flow: Setup allocates `struct octep_vf_iq`, coherent descriptor ring memory, coherent scatter/gather list memory, and per-descriptor `buff_info`; each Tx buffer receives its slice of the SGLIST area. It initializes indices and asks `hw_ops.setup_iq_regs()` to bind hardware registers. Completion processing refreshes the hardware read index via `hw_ops.update_iq_read_idx()`, walks `flush_index` to that read index within budget, unmaps either a single DMA buffer or all gather segments, frees each SKB, updates stats, and wakes the netdev subqueue through `netif_subqueue_completed_wake()`. Shutdown cleanup unmaps and frees all entries still pending between `flush_index` and `host_write_index`.

State and persistence: Queue state persists in `oct->iq[]`, `oct->num_iqs`, coherent ring and sglist DMA memory, per-entry `octep_vf_tx_buffer`, ring indices, fill counters, completion counters, and stats. Hardware progress is represented by the input queue read index and completion count registers accessed through hardware callbacks.

Dependencies and integration: Uses PCI DMA APIs, Linux SKB fragment metadata, netdev queue helpers, Octeon configuration macros, and chip-specific `hw_ops`. It integrates with the main transmit path, which must populate `buff_info`, descriptor ring entries, and doorbells consistently with the cleanup/completion format.

Risks: Scatter/gather unmap length indexing differs between completion and pending-cleanup paths (`len[3 - (i & 3)]` versus `len[i & 3]`), so descriptor packing must be validated carefully. Freeing queues assumes entries have valid SKB pointers between `flush_index` and `host_write_index`. Resource setup errors must unwind coherent memory in the right order. Queue wake thresholds must align with `IQ_INSTR_SPACE()`.

Test signals: Open/close cycles should allocate/free all IQs without DMA leaks, Tx traffic should complete and wake stopped queues, SG and non-SG packets must unmap correctly, forced shutdown with pending packets should free all SKBs, and stats should reflect posted/completed bytes and gather entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_tx.h

Purpose: Defines transmit-side hardware descriptor formats, software queue state, buffer bookkeeping, offload metadata, status codes, and stats for the Octeon EP VF driver.

Important APIs/types/functions: `struct octep_vf_tx_sglist_desc` is a 40-byte hardware SGLIST entry with four lengths and four DMA pointers. `OCTEP_VF_SGLIST_ENTRIES_PER_PKT` and `OCTEP_VF_SGLIST_SIZE_PER_PKT` size per-packet gather storage for `MAX_SKB_FRAGS`. `struct octep_vf_tx_buffer` tracks the SKB, direct DMA address, SGLIST pointer/DMA address, and gather flag. `struct octep_vf_iq` is the persistent input queue object. `struct octep_vf_instr_hdr`, `struct tx_mdata`, and `struct octep_vf_tx_desc_hw` define the 64-byte hardware instruction including data pointer, instruction header, optional offload metadata, and extension headers. Offload macros classify checksum, VLAN insert, and TSO flags.

Control flow and integration: The main Tx path fills `octep_vf_tx_desc_hw` and `tx_mdata`, rings the IQ doorbell, and stores DMA/SKB metadata in `octep_vf_tx_buffer`; `octep_vf_tx.c` later uses the same structures for completion cleanup. Device setup stores MMIO doorbell/count/interrupt register pointers in `struct octep_vf_iq`.

State and persistence: `struct octep_vf_iq` persists per Tx queue while the device is open. Coherent descriptor and SGLIST memory is shared with hardware. Offload metadata is transient per descriptor but ABI-sensitive because firmware interprets the fields.

Dependencies: Depends on Linux networking constants (`MAX_SKB_FRAGS`, SKB types, `netdev_queue`), DMA address types, and hardware ABI bitfield layout. Static size assertions validate the three most critical wire-format structs.

Risks: Hardware bitfield layout and SGLIST length ordering must match firmware. TSO/checksum offload flags must be kept in sync with the advertised netdev features and firmware capability. Ring index fields are 16-bit while queue counts are 32-bit, so configuration must keep descriptor counts within valid hardware/software bounds.

Test signals: Compile-time static assertions, Tx checksum/TSO/VLAN traffic, maximum-fragment SKBs, queue stop/wake behavior, and DMA debug runs for direct and gather packets are relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/Kconfig

Purpose: Defines kernel configuration symbols for the Marvell OcteonTX2 RVU networking driver family. It controls whether mailbox support, Admin Function, PF, VF, NDC dynamic caching disable, and RVU e-switch support are built.

Important APIs/types/functions: Kconfig symbols are `OCTEONTX2_MBOX`, `OCTEONTX2_AF`, `NDC_DIS_DYNAMIC_CACHING`, `OCTEONTX2_PF`, `OCTEONTX2_VF`, and `RVU_ESWITCH`. `OCTEONTX2_AF` selects mailbox and devlink support and depends on PCI, optional PTP clock support, and ARM64 or 64-bit compile testing. `OCTEONTX2_PF` selects mailbox, devlink, page pool, DIMLIB, and optionally AES crypto for MACsec. `OCTEONTX2_VF` depends on PF support. `RVU_ESWITCH` depends on PF support and defaults to module.

Control flow and integration: These symbols drive Makefile object inclusion and driver availability. Enabling AF builds the resource manager that other RVU functions rely on. Enabling PF builds the host NIC PF; VF support is gated behind PF because the VF driver shares PF-side infrastructure. The dynamic caching option changes AF behavior by disabling caching and locking down context entries.

State and persistence: Kconfig choices persist in the kernel build configuration and shape compiled modules. There is no runtime state here.

Dependencies: Integrates with Linux Kconfig, PCI, devlink, PTP, page pool, DIMLIB, MACsec, and architecture/compile-test constraints.

Risks: Dependency mistakes can produce unresolved symbols or unavailable drivers for supported systems. `RVU_ESWITCH` defaulting to `m` can surprise minimal builds. `NDC_DIS_DYNAMIC_CACHING` has performance and behavior implications because it alters hardware context caching policy.

Test signals: Matrix builds for AF/PF/VF/e-switch combinations, ARM64 and COMPILE_TEST builds, MACsec enabled/disabled builds, and module dependency checks should verify this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/Makefile

Purpose: Top-level build glue for Marvell OcteonTX2 networking drivers. It maps Kconfig symbols to subdirectories.

Important APIs/types/functions: `obj-$(CONFIG_OCTEONTX2_MBOX) += af/`, `obj-$(CONFIG_OCTEONTX2_AF) += af/`, and `obj-$(CONFIG_OCTEONTX2_PF) += nic/` are the functional entries. Both mailbox-only and AF builds descend into `af/`, while PF builds descend into `nic/`.

Control flow and integration: Kbuild evaluates the selected symbols and recursively builds the AF or NIC subdirectories. The duplicated `af/` dependency is intentional because mailbox objects live under the AF directory and may be needed independently of full AF support.

State and persistence: No runtime state. Build configuration determines which object directories become built-in or modules.

Dependencies: Depends on the Kconfig symbols from the sibling `Kconfig` and on subdirectory Makefiles under `af/` and `nic/`.

Risks: Because `af/` is included for two symbols, the lower-level Makefile must keep object lists separated by config to avoid duplicate or missing objects. Adding future subdirectories without matching Kconfig dependencies can break modular builds.

Test signals: `make M=...` or full kernel builds with mailbox-only, AF, and PF combinations should verify correct object inclusion and no duplicate symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/Makefile

Purpose: Defines the object composition for the OcteonTX2 RVU Admin Function and mailbox modules.

Important APIs/types/functions: `ccflags-y += -I$(src)` exposes local AF headers. `obj-$(CONFIG_OCTEONTX2_MBOX) += rvu_mbox.o` and `obj-$(CONFIG_OCTEONTX2_AF) += rvu_af.o` create separate composite objects. `rvu_mbox-y` includes `mbox.o` and `rvu_trace.o`. `rvu_af-y` includes core CGX/RVU/NPA/NIX/NPC/debugfs/PTP/CPT/devlink/switch/SDP/MCS/representor objects plus CN20K objects: `cn20k/mbox_init.o`, `cn20k/nix.o`, `cn20k/debugfs.o`, `cn20k/npa.o`, and `cn20k/npc.o`.

Control flow and integration: Kbuild links the listed objects into module or built-in units according to Kconfig. The Makefile is where CN20K support is integrated into the AF driver, so CN20K helpers are unavailable unless `OCTEONTX2_AF` is built.

State and persistence: Build-only file; no runtime state. It persists the compile/link contract for the AF subsystem.

Dependencies: Depends on all listed C files and their headers. The local include flag allows subfiles to include AF headers without long relative paths.

Risks: Object ordering can matter for init/linkage and exported symbols. Adding CN20K handlers here without corresponding mailbox dispatch declarations elsewhere would compile but not be reachable. Missing `rvu_trace.o` from mailbox builds would break trace references.

Test signals: AF and mailbox module builds, modpost symbol checks, and link tests with CN20K code enabled are direct validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx.c

Purpose: Implements the CGX/RPM MAC driver used by the RVU Admin Function to manage physical MAC/LMAC ports. It provides PCI probe/remove, LMAC discovery, register access, DMAC filter programming, flow control/PFC/PTP/loopback/statistics controls, firmware command transport, link event handling, and MAC operation registration.

Important APIs/types/functions: Exported service functions include `cgx_get_cgxcnt_max()`, `cgx_get_lmac_cnt()`, `cgx_get_pdata()`, `cgx_get_cgxid()`, `cgx_lmac_read/write()`, `cgx_set_pkind()`, `cgx_lmac_addr_*()`, `cgx_lmac_promisc_config()`, `cgx_get_rx_stats()`, `cgx_get_tx_stats()`, `cgx_stats_reset()`, `cgx_get_fec_stats()`, `cgx_lmac_rx_tx_enable()`, `cgx_lmac_tx_enable()`, `verify_lmac_fc_cfg()`, `cgx_lmac_pfc_config()`, `cgx_lmac_ptp_config()`, `cgx_fwi_cmd_send()`, `cgx_fwi_cmd_generic()`, `cgx_lmac_evh_register()`, `cgx_lmac_evh_unregister()`, `cgx_get_fwdata_base()`, `cgx_set_link_mode()`, `cgx_set_fec()`, `cgx_get_phy_fec_stats()`, `cgx_lmac_linkup_start()`, `cgx_lmac_reset()`, and query helpers for LMAC IDs/bitmaps/features/FIFO. Static helpers implement device-type selection, LMAC validation, firmware event parsing, link-mode mapping, probe, cleanup, and `mac_ops`.

Control flow: `cgx_probe()` allocates `struct cgx`, selects CGX versus RPM ops, enables PCI, maps BAR0 registers, filters unmapped CGX blocks, allocates MSI-X vectors and a link command workqueue, links the device into `cgx_list`, populates feature flags, and initializes LMACs. `cgx_lmac_init()` allocates each LMAC, reserves DMAC index 0, allocates flow-control bitmaps, registers firmware interrupts, configures pause defaults, reads LMAC type, clears stale filters, resets the default DMAC entry, starts X2P reset, and verifies firmware major version. Firmware commands are serialized by `lmac->cmd_lock`, written to scratch command registers, completed by the IRQ handler through a waitqueue, and interpreted from event scratch registers. Link changes update cached `lmac->link_info` and notify a registered callback under a spinlock.

State and persistence: Global `cgx_list` tracks probed MAC blocks. `struct cgx` holds PCI, MMIO, `mac_ops`, feature flags, FIFO length, LMAC count, bitmap, ID map, lock, and workqueue. `struct lmac` state includes command waitqueue/lock, event callback, link info, DMAC bitmap, flow-control PF/VF bitmaps, type, and interrupt name. Hardware state persists in CGX/RPM CSRs and firmware scratch registers.

Dependencies and integration: Depends on PCI, ACPI/OF, netdevice/ethtool/PHY helpers, `rvu.h`, `lmac_common.h`, `rpm.h`, firmware ABI in `cgx_fw_if.h`, and RVU bitmap helpers. RVU AF code uses this file through `cgx.h` and `mac_ops` to bind NIX channels, link state, packet filters, and port controls.

Risks: Lock ordering around firmware commands and event callbacks is critical because link events can race with command responses and unregister. DMAC filter indexing relies on enabled-LMAC sequence IDs and per-LMAC bitmap allocation. Link-mode mapping has many ethtool cases and a default invalid mode. Probe error paths must free IRQs, workqueues, list entries, and bitmaps exactly once. Hardware variants selected by `is_dev_rpm()` and `is_dev_rpm2()` have different offsets and capabilities.

Test signals: PCI probe/remove on CGX and RPM devices, firmware version mismatch handling, link up/down callbacks, ethtool link-mode changes, MAC address add/update/delete/promisc transitions, pause/PFC arbitration across PF/VFs, PTP enable/disable, loopback, stats/FEC reads, and fault injection for command timeout or IRQ registration failures are key validation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx.h

Purpose: Public interface and register definition header for the OcteonTX2 CGX/RPM MAC driver. It exposes register offsets, bit masks, LMAC mode enums, event callback types, and the API surface consumed by RVU Admin Function and NIC code.

Important APIs/types/functions: The file defines PCI/device constants, CGX CMR/SPU/GMP/SMU register offsets, DMAC CAM masks, pause/PFC/PTP bits, firmware scratch register aliases, command timeout, and LMAC mode enum values. Types include `struct cgx_link_event` and `struct cgx_event_cb`. Function declarations cover CGX discovery, LMAC count/IDs, register access, pkind setup, event callback registration, MAC address filters, promisc, flow control/PFC, loopback, link info/linkup, firmware data base discovery, PTP, FEC, link mode setting, feature queries, reset, and FIFO length.

Control flow and integration: `cgx.c`, `rvu_cgx.c`, and related AF code include this header to call into the MAC service layer. The `extern struct pci_driver cgx_driver` allows driver registration from AF module initialization. Register macros are used directly by CGX and RPM operations.

State and persistence: No storage is allocated here. It defines how state is addressed in hardware registers and how callbacks deliver state changes through `struct cgx_link_event`.

Dependencies: Includes `mbox.h`, `cgx_fw_if.h`, and `rpm.h`, so it binds the MAC API to mailbox-visible link structures, firmware command ABI, and RPM variant operations.

Risks: This is a high-fanout ABI inside the driver. Renaming or changing prototypes affects AF, PF, and possibly representor/e-switch code. Register macros using `mac_ops->csr_offset` depend on a local variable named `mac_ops` in calling functions, which is concise but fragile if copied without that variable.

Test signals: Build coverage across AF users, successful CGX/RPM probe, RVU-to-CGX link management, filter programming, and PFC/PTP/FEC operations validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx_fw_if.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx_fw_if.h

Purpose: Defines the firmware command/event ABI used for communication between non-secure software and CGX firmware/ATF through scratch registers. It enumerates firmware versions, command IDs, event IDs, status/error encodings, link speeds, physical modes, and bitfield layouts for command and response registers.

Important APIs/types/functions: Key enums are `cgx_error_type`, `cgx_link_speed`, `CGX_MODE_`, `cgx_cmd_id`, `cgx_evt_id`, `cgx_evt_type`, `cgx_stat`, and `cgx_cmd_own`. `FIELD_SET()` wraps bitfield update logic. Response masks define ACK, event type, status, ID, error type, firmware version, MAC address, MKEX profile, firmware data base, and link status fields. `struct cgx_lnk_sts` documents the packed link-status response. Command masks define ownership, command ID, enable flag, MTU, link change, FEC, mode-change speed/duplex/autoneg/base index/flags, and link bring-up timeout.

Control flow and integration: `cgx.c` builds command words with `FIELD_SET(CMDREG_ID, ...)`, writes them to `CGX_COMMAND_REG`, and decodes responses/events with `FIELD_GET()` using masks from this header. Link-mode setting, FEC setting, firmware data base queries, link bring-up/down, and asynchronous link events all depend on these definitions.

State and persistence: The header represents transient command/response state in scratch CSRs. Ownership bits coordinate whether firmware or non-secure software owns a command or advertised-link-mode shared field.

Dependencies: Requires Linux bit and bitfield helpers. It must remain synchronized with firmware and ATF implementations, not just kernel code.

Risks: ABI drift is the central risk. A changed command ID, bitfield width, or firmware major version can break link management. The mode enum includes sparse values and grouped mode ranges; callers must correctly set `CMDMODECHANGE_MODE_BASEIDX` for values above the first range. Incorrect ownership handling can lead to `CGX_ERR_PREV_ACK_NOT_CLEAR` or busy responses.

Test signals: Firmware version checks, every CGX command path, link change event decoding, FEC and advertised mode changes, and negative tests for invalid/unsupported modes validate this ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cgx_fw_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/api.h

Purpose: Declares the CN20K-specific extension API for RVU Admin Function mailbox setup, mailbox memory management, and AF/PF/VF interrupt control.

Important APIs/types/functions: `struct ng_rvu` holds CN20K next-generation RVU extension state: `rvu_mbox_ops`, PF mailbox `qmem`, and VF mailbox `qmem`. Function prototypes include `cn20k_rvu_mbox_init()`, `cn20k_rvu_get_mbox_regions()`, `cn20k_free_mbox_memory()`, `cn20k_register_afpf_mbox_intr()`, `cn20k_register_afvf_mbox_intr()`, `cn20k_rvu_enable_mbox_intr()`, `cn20k_rvu_unregister_interrupts()`, `cn20k_mbox_setup()`, `cn20k_rvu_enable_afvf_intr()`, and `cn20k_rvu_disable_afvf_intr()`.

Control flow and integration: Core RVU AF code calls these declarations when running on CN20K hardware. The implementation in `mbox_init.c` allocates shared mailbox memory, installs mailbox operation handlers, registers interrupts, and enables/disables interrupt masks.

State and persistence: `struct ng_rvu` persists as part of `struct rvu` during AF lifetime. Its qmem pointers own DMA/IOVA-backed mailbox regions until freed.

Dependencies: Includes `../rvu.h` and relies on `struct rvu`, `struct qmem`, `struct mbox_ops`, `struct otx2_mbox`, and PCI device types.

Risks: The header is a cross-module contract; mismatched definitions between core RVU and CN20K implementation cause build or runtime mailbox failures. Memory ownership is implicit: callers must ensure `cn20k_free_mbox_memory()` runs after successful allocation.

Test signals: CN20K AF probe, mailbox init for AFPF and AFVF, interrupt registration, PF/VF message exchange, and teardown memory cleanup validate the API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/debugfs.c

Purpose: Adds CN20K-specific debugfs views for NPC MCAM allocator state and pretty-printers for CN20K NIX/NPA hardware context structures. It is observability code used by the RVU AF debugfs infrastructure.

Important APIs/types/functions: Debugfs show functions are `npc_mcam_layout_show()`, `npc_mcam_default_show()`, `npc_vidx2idx_map_show()`, `npc_idx2vidx_map_show()`, and `npc_defrag_show()`, each wrapped with `DEFINE_SHOW_ATTRIBUTE`. Public lifecycle functions are `npc_cn20k_debugfs_init()` and `npc_cn20k_debugfs_deinit()`. Public context printers are `print_nix_cn20k_sq_ctx()`, `print_nix_cn20k_cq_ctx()`, `print_npa_cn20k_aura_ctx()`, and `print_npa_cn20k_pool_ctx()`.

Control flow: Init creates debugfs files under `rvu->rvu_dbg.npc`: `mcam_layout`, `mcam_default`, `vidx2idx`, `idx2vidx`, and `defrag`. The layout view walks NPC subbanks under each subbank lock and prints occupied MCAM entries, PF ownership, and virtual index mappings for x4 or x2 key modes. Default view walks PF mappings and asks `npc_cn20k_dft_rules_idx_get()` for broadcast, multicast, promisc, and unicast default rule indices. The xarray views dump virtual-to-real and real-to-virtual MCAM mappings. Defrag view prints pending/recorded MCAM defragmentation moves under `npc_priv->lock`. Context printers emit individual bitfields from CN20K SQ/CQ/aura/pool admin-queue responses to a `seq_file`.

State and persistence: Debugfs files are transient kernel objects. The displayed state is live NPC private state: subbank bitmaps, xarrays, defrag list, and NIX/NPA context responses. No state is modified except debugfs registration/removal.

Dependencies and integration: Depends on Linux debugfs/seq_file, xarray, NPC CN20K private structures in `cn20k/npc.h`, and context struct layouts from `struct.h`. AF debugfs setup calls `npc_cn20k_debugfs_init()`, and generic debugfs code can call the context printers for CN20K AQ responses.

Risks: Debugfs readers race with allocator changes unless all relevant locks are held; subbank and defrag paths lock, but xarray dumps rely on xarray iteration semantics. Printing raw context fields can go stale if CN20K struct layouts change. `npc_cn20k_debugfs_deinit()` removes the whole NPC debugfs subtree, which must be coordinated with non-CN20K files under the same directory.

Test signals: Mount debugfs and read all created files under active MCAM allocations, virtual allocations, and defrag activity. CN20K AQ context debug output should match hardware dumps and not sleep or crash under concurrent rule changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/debugfs.h

Purpose: Declares CN20K debugfs initialization/teardown functions and context pretty-printers for NIX and NPA admin-queue response structures.

Important APIs/types/functions: The header exposes `npc_cn20k_debugfs_init()`, `npc_cn20k_debugfs_deinit()`, `print_nix_cn20k_sq_ctx()`, `print_nix_cn20k_cq_ctx()`, `print_npa_cn20k_aura_ctx()`, and `print_npa_cn20k_pool_ctx()`. It includes `struct.h` and `../mbox.h` for CN20K context response types.

Control flow and integration: AF debugfs setup includes this header to install CN20K NPC files. Generic NIX/NPA debugfs context dumping code includes it to call the CN20K-specific formatters when the hardware generation requires CN20K layouts.

State and persistence: Header only; no runtime state. It defines access to debugfs file registration and live context rendering functions.

Dependencies: Depends on debugfs, fs, module, PCI headers, CN20K `struct.h`, and mailbox definitions. The include guard is named `DEBUFS_H`, which appears to be a typo but still prevents repeated inclusion.

Risks: Prototype changes must stay synchronized with `debugfs.c` and generic AF debugfs callers. Because printers take CN20K-specific structures, accidentally calling them with older-generation response layouts would produce invalid output.

Test signals: Build coverage with CN20K debugfs enabled and runtime reads of CN20K debugfs context dumps validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/mbox_init.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/mbox_init.c

Purpose: Implements CN20K-specific RVU mailbox memory allocation, mailbox region mapping, mailbox interrupt handlers/registration, interrupt enable/disable, and additional CINT/QINT context setup for non-OTX2/non-CN20K paths.

Important APIs/types/functions: Public functions include `cn20k_register_afvf_mbox_intr()`, `cn20k_rvu_enable_mbox_intr()`, `cn20k_rvu_unregister_interrupts()`, `cn20k_register_afpf_mbox_intr()`, `cn20k_rvu_get_mbox_regions()`, `cn20k_rvu_mbox_init()`, `cn20k_free_mbox_memory()`, `cn20k_rvu_disable_afvf_intr()`, `cn20k_rvu_enable_afvf_intr()`, and `rvu_alloc_cint_qint_mem()`. Static handlers are `cn20k_afvf_mbox_intr_handler()` and `cn20k_mbox_pf_common_intr_handler()`. Static `rvu_alloc_mbox_memory()` backs AFPF/AFVF mailbox allocations. `cn20k_mbox_ops` binds handler callbacks.

Control flow: Mailbox init first gates on `is_cn20k()`, assigns CN20K mailbox ops, programs mailbox size config registers, and allocates qmem. AFPF allocation writes each PF mailbox IOVA into RVUM PF address registers; AFVF allocation writes the VF mailbox base to the PF VF mailbox address register. Interrupt registration allocates four `rvu_irq_data` entries for PF or VF interrupt groups, fills status registers, device ranges, queue-work handlers, vector numbers, names, and calls `request_irq()` with CN20K handlers. Handlers clear interrupt status, trace active interrupt bits, enforce memory barriers around mailbox memory, and enqueue RVU work. Enable/disable functions program W1S/W1C interrupt masks for PF/VF mailbox, FLR, and ME sources over the first and second 64-VF banks.

State and persistence: Persistent state includes `rvu->ng_rvu->rvu_mbox_ops`, `pf_mbox_addr`, `vf_mbox_addr`, `rvu->irq_allocated[]`, IRQ names, and hardware mailbox config/address/mask registers. Mailbox qmem remains allocated until `cn20k_free_mbox_memory()`.

Dependencies and integration: Depends on RVU register accessors (`rvu_read64/write64`, `rvupf_read64/write64`), qmem allocation, PCI IRQ vectors, tracepoints, workqueue dispatch (`rvu_queue_work`), and CN20K register definitions in `reg.h`.

Risks: IRQ registration error paths return immediately without freeing previously requested IRQs in the same loop, so caller teardown must handle partial allocation through `irq_allocated`. `INTR_MASK(hw->total_pfs - 64)` must be safe when counts are below 64. Mailbox region pointers use `phys_to_virt()` on qmem bases; platform memory mapping assumptions matter. AFVF enable path enables `RVU_PF_VFME_INT_ENA_W1SX(1)` only for the second bank, unlike disable which clears bank 0 and bank 1.

Test signals: CN20K PF/VF mailbox ping, interrupts across PF ranges 0-63 and 64+, VF counts above and below 64, FLR/ME interrupt handling, qmem leak checks on remove, and partial IRQ registration failure injection validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/mbox_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/nix.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/nix.c

Purpose: Provides the CN20K mailbox handler for NIX admin-queue enqueue operations. It adapts CN20K request/response structure types to the existing generic NIX AQ enqueue implementation.

Important APIs/types/functions: The single function is `rvu_mbox_handler_nix_cn20k_aq_enq(struct rvu *rvu, struct nix_cn20k_aq_enq_req *req, struct nix_cn20k_aq_enq_rsp *rsp)`. It casts the CN20K request and response to generic `struct nix_aq_enq_req` and `struct nix_aq_enq_rsp` before calling `rvu_nix_aq_enq_inst()`.

Control flow and integration: Mailbox dispatch routes CN20K NIX AQ messages to this handler. The handler delegates all validation, hardware AQ programming, polling, and response fill to generic NIX code, relying on layout compatibility between generic and CN20K structures for the shared prefix/operation contract.

State and persistence: No local state. It operates on RVU/NIX hardware state through the delegated generic function and fills the mailbox response supplied by the caller.

Dependencies: Includes CN20K `struct.h` and `../rvu.h`. Depends on `rvu_nix_aq_enq_inst()` accepting the casted request/response.

Risks: This is a type-adapter shim; if CN20K AQ structures diverge in incompatible ways from generic NIX AQ structures, casts become unsafe. There is no additional generation-specific validation here.

Test signals: CN20K mailbox AQ operations for SQ/CQ/RQ contexts, response decoding through CN20K debugfs printers, and build checks for handler registration validate the shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/nix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npa.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npa.c

Purpose: Provides the CN20K mailbox handler for NPA admin-queue enqueue operations. Like the CN20K NIX shim, it delegates to the generic NPA AQ implementation through compatible structure casts.

Important APIs/types/functions: `rvu_mbox_handler_npa_cn20k_aq_enq(struct rvu *rvu, struct npa_cn20k_aq_enq_req *req, struct npa_cn20k_aq_enq_rsp *rsp)` calls `rvu_npa_aq_enq_inst()` after casting to generic `struct npa_aq_enq_req` and `struct npa_aq_enq_rsp`. The function is exported with `EXPORT_SYMBOL()`.

Control flow and integration: CN20K mailbox dispatch invokes this handler for NPA AQ requests. Generic NPA code performs actual AQ instruction construction, submission, and response handling. Exporting the symbol allows other compiled units/modules to reference the CN20K handler.

State and persistence: No local state. Effects are delegated to generic NPA AQ code and ultimately modify/read NPA hardware context state.

Dependencies: Includes CN20K `struct.h`, `../rvu.h`, and relies on `rvu_npa_aq_enq_inst()` plus layout compatibility between CN20K and generic NPA AQ request/response structs.

Risks: Unsafe if CN20K structures stop being layout-compatible with generic AQ structures. The extra `EXPORT_SYMBOL()` broadens linkage surface, so symbol availability and module ownership should be considered. There is no CN20K-specific validation in this wrapper.

Test signals: CN20K NPA aura/pool AQ operations, CN20K NPA debugfs context printing, module symbol checks, and mailbox conformance tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npa.c -->
