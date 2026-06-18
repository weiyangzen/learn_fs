# subset-b-004507 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_prs.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_prs.c

### Purpose
`mvpp2_prs.c` programs and maintains the Marvell PPv2 packet parser TCAM/SRAM. It builds the default parser pipeline for Marvell headers, MAC DA classification, DSA/EDSA, VLAN/VID filtering, L2 ethertypes, PPPoE, IPv4, IPv6, and flow-id generation, then exposes runtime helpers for MAC address acceptance, promiscuous modes, tag modes, VID filters, custom flows, parser hit counters, and re-reading entries from hardware.

### Important APIs, Types, And Functions
The central object is `struct mvpp2_prs_entry`, a software image of one parser TCAM/SRAM row. The file uses `struct mvpp2_prs_shadow` arrays in `struct mvpp2` to remember which hardware rows are valid, their lookup ID, result-info mask, finish state, and UDF kind. Low-level helpers include `mvpp2_prs_hw_write()`, `__mvpp2_prs_init_from_hw()`, `mvpp2_prs_hw_inv()`, TCAM setters/getters for lookup, ports, AI, data bytes, ethertype and VID, and SRAM setters for RI, AI, next lookup, shifts, UDF offsets, lookup-done, and flow generation.

Public entry points are `mvpp2_prs_default_init()`, `mvpp2_prs_init_from_hw()`, `mvpp2_prs_tcam_port_map_get()`, `mvpp2_prs_tcam_data_byte_get()`, `mvpp2_prs_mac_da_accept()`, `mvpp2_prs_update_mac_da()`, `mvpp2_prs_mac_promisc_set()`, `mvpp2_prs_mac_del_all()`, `mvpp2_prs_tag_mode_set()`, `mvpp2_prs_add_flow()`, `mvpp2_prs_def_flow()`, `mvpp2_prs_vid_enable_filtering()`, `mvpp2_prs_vid_disable_filtering()`, `mvpp2_prs_vid_entry_add()`, `mvpp2_prs_vid_entry_remove()`, `mvpp2_prs_vid_remove_all()`, and `mvpp2_prs_hits()`.

### Control Flow
Initialization enters through `mvpp2_prs_default_init()`. It allocates the shadow tables, enables TCAM, clears all 256 TCAM/SRAM rows, invalidates every entry, initializes each port to start at lookup `MVPP2_PRS_LU_MH`, and then installs default entries in order: per-port default flow rows, Marvell-header handling, MAC defaults, DSA/EDSA defaults, VID defaults, L2 ethertypes, VLAN combinations, PPPoE, IPv6, and IPv4. Each default initializer creates one or more `mvpp2_prs_entry` objects, fills match keys and parser actions, updates the shadow row, and commits the row by indirect register writes.

Runtime control paths are row mutation paths protected by `priv->prs_spinlock`. MAC DA programming searches the dedicated MAC TCAM range for an exact DA/mask/port-map match, allocates a free row if needed, updates the port map, writes L2 cast and MAC-me result info, and invalidates rows whose port map becomes empty. VID filtering uses a per-port reserved range, adds VID rows, and installs or removes a guard row that drops unmatched VLAN packets. Tag-mode changes add or remove ports from DSA or EDSA parser rows. Flow helpers allocate flow lookup rows and write result-info match bytes to produce a six-bit flow id.

### State, Persistence, And Dependencies
Parser state persists in hardware TCAM/SRAM registers and in `priv->prs_shadow` plus `priv->prs_double_vlans`. Hardware access uses `mvpp2_read()` and `mvpp2_write()` indirect register programming. The shadow table is authoritative for finding free rows and for scanning by lookup ID or UDF kind; losing sync between shadow and hardware would make later updates allocate over live rows or skip real entries. The spinlock serializes hardware indirect access and shadow mutations, with `lockdep_assert_held()` on internal hardware routines. The implementation depends on Linux networking helpers for Ethernet address classification, netdev address updates, IPv4/IPv6 protocol constants, PPP protocol IDs, and PPv2 register and tag constants from `mvpp2.h` and `mvpp2_prs.h`.

### Integration Points
`mvpp2_main.c` and related MVPP2 setup paths call the default parser initialization during device bring-up, then use the runtime helpers from netdev operations: address changes use `mvpp2_prs_update_mac_da()`, multicast/unicast filter changes use MAC accept/delete helpers, VLAN operations use VID entry helpers, promiscuous/allmulti mode uses `mvpp2_prs_mac_promisc_set()`, port tag configuration uses `mvpp2_prs_tag_mode_set()`, and receive-flow/classifier setup uses `mvpp2_prs_add_flow()` or default flow helpers. Debug paths can inspect parser entries and hit counters through the exported read helpers.

### Risks
TCAM row allocation is range-sensitive. MAC filters, VID filters, default rows, flow rows, VLAN rows, and protocol rows all rely on non-overlapping index ranges; off-by-one mistakes or future range expansion could overwrite reserved rows. Double VLAN AI allocation uses `priv->prs_double_vlans` but does not appear to free AI slots when rows are removed because these default VLAN entries are effectively persistent. Several find paths scan only the shadow table, so any direct hardware invalidation without shadow updates is dangerous. Parser actions use signed shifts, UDF offsets, and AI bits to drive multi-stage lookups; incorrect offsets can silently misclassify packets rather than fail visibly. `mvpp2_prs_hits()` checks `index > MVPP2_PRS_TCAM_SRAM_SIZE`, allowing exactly `MVPP2_PRS_TCAM_SRAM_SIZE`, which is outside the 0..255 row range used elsewhere.

### Test Signals
Useful signals include boot-time parser initialization on all supported ports, failure injection for devm allocation and TCAM exhaustion, adding/removing the port MAC, broadcast, multicast, and extra unicast addresses, toggling promiscuous and allmulti modes, changing tag modes among none/MH/DSA/EDSA, adding the maximum supported VID filters per port and verifying the guard drop row, PPPoE IPv4/IPv6 traffic, IPv4 fragments and multicast/broadcast, IPv6 multicast/hop-limit/unknown extension cases, flow steering rule insertion, parser hit counter reads at boundary indices, and traffic tests after repeated address/VLAN updates to catch shadow/hardware drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_prs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_prs.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_prs.h

### Purpose
`mvpp2_prs.h` defines the internal contract for the MVPP2 parser. It describes parser table dimensions, TCAM and SRAM bit layouts, reserved row ranges, result-info and additional-info encodings, lookup identifiers, shadow metadata, parser entry storage, and the public parser helper API used by the rest of the driver.

### Important APIs, Types, And Functions
The header defines `MVPP2_PRS_TCAM_SRAM_SIZE`, TCAM/SRAM word counts, flow-id size and masks, byte-to-word helpers, TCAM enable/data fields, reserved parser entry IDs, per-port MAC and VID filter ranges, SRAM offsets for RI, shift, UDF, AI, next lookup, done/generate bits, and RI masks for MAC, DSA, VLAN, CPU special packets, L2/L3/L4 protocol classification, fragmentation, UDF fields, and drop decisions. `enum mvpp2_prs_udf` identifies shadow UDF categories, and `enum mvpp2_prs_lookup` names the parser stages from `MVPP2_PRS_LU_MH` through `MVPP2_PRS_LU_FLOWS`.

The main data structures are `struct mvpp2_prs_entry`, `struct mvpp2_prs_result_info`, and `struct mvpp2_prs_shadow`. The declared API covers initialization, hardware row readback, TCAM data inspection, MAC DA filtering, tag mode updates, custom flow rows, default flow selection, VID filter enable/disable/add/remove, promiscuous mode, MAC filter cleanup, netdev MAC address update, and hit counter access.

### Control Flow
The header does not implement control flow, but it fixes the parser state machine consumed by `mvpp2_prs.c`: packet parsing starts at Marvell-header lookup, advances through MAC, DSA, VLAN, VID, L2, PPPoE, IPv4/IPv6, and ends at flow lookup. The reserved entry IDs encode where default and dynamic rows are expected to live, so callers indirectly depend on those ranges when invoking runtime update helpers.

### State, Persistence, And Dependencies
The header owns no storage itself. It defines the shape of persistent state stored in hardware and mirrored in `struct mvpp2_prs_shadow`. It depends on `mvpp2.h` for register and device types and includes kernel netdevice/platform headers for `struct mvpp2`, `struct mvpp2_port`, `struct net_device`, and address/VID-facing APIs.

### Integration Points
This is included by `mvpp2_prs.c` and by MVPP2 modules that need parser lifecycle or filter updates. The constants also tie parser RI values to downstream classifier and receive logic, since result-info bits tell later hardware/software whether a frame is dropped, addressed to the port, VLAN tagged, ARP/IP/PPPoE, fragmented, TCP/UDP, or special CPU-directed traffic.

### Risks
The file hardcodes parser row partitioning and assumes three VID-filtered ports, fixed 256-row hardware, and specific TCAM/SRAM bit packing. Any hardware variant with different row count, lookup encoding, or filter capacity requires coordinated changes here and in `mvpp2_prs.c`. Because many macros are raw bit positions, overlap errors are easy to introduce and hard to detect by compilation. The API exposes low-level parser mutation primitives broadly inside the driver, so call ordering and locking expectations must be respected by consumers.

### Test Signals
Compile coverage should catch most type and prototype changes. Runtime test signals mirror parser behavior: parser default initialization, all parser lookup transitions, MAC and VLAN filter capacity boundaries, DSA/EDSA modes, flow-id generation, drop decisions from RI masks, hit counter access, and traffic classification for L2, PPPoE, IPv4, IPv6, multicast, broadcast, fragmented, and unknown-protocol packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_prs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_tai.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_tai.c

### Purpose
`mvpp2_tai.c` implements PTP hardware clock support for the Marvell PP2.2 Time Application Interface. It registers a `ptp_clock`, supports fine frequency adjustment, time adjustment, get/set time, periodic timestamp refresh, and conversion of compact RX/TX hardware timestamps into full kernel hardware timestamps.

### Important APIs, Types, And Functions
The local `struct mvpp2_tai` stores `ptp_clock_info`, the registered `ptp_clock`, MMIO base, a spinlock, the fixed-point clock period, and a cached full timestamp refreshed every two seconds. Register helpers are `mvpp2_tai_modify()`, `mvpp2_tai_write()`, `mvpp2_tai_read()`, `mvpp22_tai_read_ts()`, `mvpp2_tai_write_tlv()`, and `mvpp2_tai_op()`. PTP callbacks are `mvpp22_tai_adjfine()`, `mvpp22_tai_adjtime()`, `mvpp22_tai_gettimex64()`, `mvpp22_tai_settime64()`, and `mvpp22_tai_aux_work()`.

Driver-facing APIs are `mvpp22_tai_probe()`, `mvpp22_tai_ptp_clock_index()`, `mvpp22_tai_tstamp()`, `mvpp22_tai_start()`, and `mvpp22_tai_stop()`. The implementation also calculates fractional period adjustments through `mvpp22_calc_frac_ppm()` and initializes hardware step size with `mvpp22_tai_set_step()` and `mvpp22_tai_init()`.

### Control Flow
Probe allocates `struct mvpp2_tai`, points it at `priv->iface_base`, sets a nominal 3 ns period in 32.32 fixed point, releases the TAI reset, fills the PTP callback table, registers a cleanup action, registers the PTP clock, and stores it in `priv->tai`. `mvpp22_tai_start()` immediately reads the time through the aux worker and schedules periodic refreshes. `mvpp22_tai_tstamp()` combines the cached seconds with the 2-bit seconds and 30-bit nanoseconds in queue timestamps, adjusting by a small modulo delta.

PTP operations serialize register access with `tai->lock`. `gettimex64()` triggers a capture, records system pre/post timestamps around that trigger, reads the valid capture bank, and returns `-EBUSY` if neither capture valid bit is set. `settime64()` writes TLV registers and triggers an update with phase update enabled. `adjtime()` writes a delta and triggers increment or decrement. `adjfine()` converts scaled ppm to a signed fractional nanosecond period delta and triggers a frequency update.

### State, Persistence, And Dependencies
Persistent state includes the hardware TOD counter, TLV staging registers, frequency step registers, registered PTP clock, and cached `tai->stamp`. The cache is not a durable store; it is a reconstruction aid for compact packet timestamps. The code depends on Linux PTP clock infrastructure, `ptp_schedule_worker()`, `ptp_cancel_worker_sync()`, `ptp_read_system_prets/postts()`, MMIO helpers, spinlocks, and MVPP22 TAI register offsets from `mvpp2.h`.

### Integration Points
MVPP2 probe code calls `mvpp22_tai_probe()` for PP2.2 hardware, starts/stops the PTP worker with interface lifetime, exposes the PTP clock index to timestamping configuration paths, and uses `mvpp22_tai_tstamp()` from packet completion paths to populate `skb_shared_hwtstamps`.

### Risks
The file explicitly warns that external use of `PTP_EVENT_REQ` can trigger the currently programmed TCF operation and cannot be masked, so board mux configuration can corrupt time reads or updates outside driver control. `mvpp22_tai_tstamp()` depends on the aux worker refreshing `tai->stamp` often enough that the 2-bit seconds field can be reconstructed; long stalls can misplace timestamps by multiples of four seconds. Busy loops are avoided, but capture can fail with `-EBUSY`. The period is hardcoded for the 333.333333 MHz-derived clock as exactly 3 ns to avoid documented rounding error, so different clocking would need a new calculation.

### Test Signals
Useful tests include PTP clock registration/removal, `phc2sys`/`ptp4l` time read and adjustment paths, `adjfine()` at positive/negative extremes and `S64_MIN` rejection in `adjtime()`, RX/TX timestamp reconstruction around second wrap and after worker delays, settime followed by gettimex consistency, module unload cleanup, and board-level validation that PTP_EVENT_REQ muxes are not enabled while this driver owns the TAI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_tai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/Kconfig

### Purpose
`Kconfig` defines the build-time configuration symbol for the Marvell Octeon PCI Endpoint NIC driver. It allows the driver to be built in or as the `octeon_ep` module.

### Important APIs, Types, And Functions
The single symbol is `CONFIG_OCTEON_EP`, declared as a tristate named "Marvell Octeon PCI Endpoint NIC Driver". It depends on `64BIT`, `PCI`, and `PTP_1588_CLOCK_OPTIONAL`. The help text identifies the supported functionality and points to `Documentation/networking/device_drivers/ethernet/marvell/octeon_ep.rst` for supported devices.

### Control Flow
There is no runtime control flow. The Kconfig symbol gates whether the Makefile builds the Octeon EP objects and whether the driver is available to PCI device probing.

### State, Persistence, And Dependencies
The persistent effect is the kernel configuration value. The dependencies ensure the target has 64-bit support, PCI infrastructure, and optional PTP clock support before compiling this network driver.

### Integration Points
The symbol is consumed by the local `Makefile` through `obj-$(CONFIG_OCTEON_EP) += octeon_ep.o`. It also integrates with kernel menu configuration and module packaging.

### Risks
The dependency set is intentionally small. If future code makes a non-optional dependency mandatory, the Kconfig should be updated or builds can fail under uncommon configurations. The help text references external documentation, so stale device support docs would mislead users without affecting compilation.

### Test Signals
Build the driver as built-in, as a module, and disabled. Also test minimal 64-bit PCI configs with and without PTP optional support to ensure the dependency expression matches included headers and feature use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/Makefile

### Purpose
The Octeon EP `Makefile` declares how the Marvell Octeon PCI Endpoint NIC driver is linked from its component objects.

### Important APIs, Types, And Functions
It builds `octeon_ep.o` when `CONFIG_OCTEON_EP` is enabled. The composite object includes `octep_main.o`, `octep_cn9k_pf.o`, `octep_tx.o`, `octep_rx.o`, `octep_ethtool.o`, `octep_ctrl_mbox.o`, `octep_ctrl_net.o`, `octep_pfvf_mbox.o`, and `octep_cnxk_pf.o`.

### Control Flow
There is no runtime flow. Build flow is controlled by Kbuild: the composite object is linked from the listed objects and then built in or emitted as the `octeon_ep` module according to the tristate value.

### State, Persistence, And Dependencies
The file persists only build composition. It depends on source files providing the expected symbols used across the driver, especially chip-specific setup hooks, datapath code, ethtool operations, control mailbox, control network protocol, and PF/VF mailbox support.

### Integration Points
The Makefile is reached from the parent Marvell Ethernet Kbuild when `CONFIG_OCTEON_EP` is selected. The object list is the local integration point tying shared main/datapath code to both CN9K and CNXK PF implementations.

### Risks
Adding a new source file without updating this list will compile locally only if it is included elsewhere, which is not the normal pattern. Removing or reordering objects rarely matters for Kbuild but missing chip-specific objects would leave PCI ID setup paths unresolved.

### Test Signals
Run kernel build coverage for `CONFIG_OCTEON_EP=y` and `m`; verify all listed objects compile and link, and use `modinfo octeon_ep` or link logs to confirm the composite module contains the expected support files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cn9k_pf.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cn9k_pf.c

### Purpose
`octep_cn9k_pf.c` provides the CN93/CN98 physical-function hardware operations for the Octeon EP NIC driver. It initializes chip-specific register windows, ring limits, queue registers, PF/VF mailbox registers, interrupt handlers, reset behavior, and the `oct->hw_ops` function table used by common driver code.

### Important APIs, Types, And Functions
The exported entry point is `octep_device_setup_cn93_pf()`. It installs hardware operations for IQ/OQ setup, PF/VF mailbox setup, non-IOQ and IOQ interrupt handlers, soft reset, register reinitialization, interrupt enable/disable, polling, IQ read-index updates, queue enable/disable/reset, and register dumps.

Important internal functions include `cn93_dump_regs()`, `cn93_reset_iq()`, `cn93_reset_oq()`, `octep_reset_io_queues_cn93_pf()`, `octep_setup_pci_window_regs_cn93_pf()`, `octep_configure_ring_mapping_cn93_pf()`, `octep_init_config_cn93_pf()`, `octep_setup_iq_regs_cn93_pf()`, `octep_setup_oq_regs_cn93_pf()`, `octep_setup_mbox_regs_cn93_pf()`, PF/VF mailbox and OEI poll/interrupt handlers, error interrupt handlers, `octep_soft_reset_cn93_pf()`, `octep_soft_reset_cn98_pf()`, and queue enable/disable helpers.

### Control Flow
Setup installs the ops table, sets PCI windowed CSR access pointers, reads `CN93_SDP_MAC_NUMBER` to determine the PCIe port, initializes configuration from hardware ring-info CSRs, maps PF rings to this function, and for CN93 marks firmware status as running through a window write. Configuration reads VF and PF ring topology, fills default IQ/OQ descriptor and coalescing values, configures MSI-X counts/names, computes control-mailbox BAR memory from BAR4 plus SR-IOV function link offset, and sets default firmware heartbeat policy.

Queue setup waits for ring idle, programs descriptor DMA base and ring size, stores doorbell/count/interrupt MMIO pointers into `struct octep_iq` or `struct octep_oq`, resets instruction counters, and configures interrupt thresholds. Runtime interrupt flow acknowledges PF/VF mailbox bits and schedules mailbox work per VF, acknowledges OEI events and queues control mailbox work or resets heartbeat miss count, logs and clears ring/DMA/MISC errors, and schedules NAPI for IOQ interrupts. Reinit reruns IQ/OQ setup, enables interrupts and queues, and posts RX credits.

### State, Persistence, And Dependencies
State is stored in `oct->conf`, `oct->hw_ops`, `oct->pcie_port`, PCI window register pointers, per-queue MMIO register pointers, PF/VF mailbox structures, heartbeat counters, and hardware CSRs. The code depends on CN9K register macros, common Octeon device structures, PCI SR-IOV capability access, NAPI, workqueues, and shared control/PF-VF mailbox tasks.

### Integration Points
Common probe code selects this setup function for CN93/CN98 PF PCI IDs. The common datapath calls the installed ops to program queues, enable interrupts, reset queues, update Tx completion indices, and dump registers. SR-IOV and mailbox code consume `setup_mbox_regs` and mailbox interrupt scheduling. Control-plane code relies on OEI mailbox events to schedule firmware message processing.

### Risks
Several idle waits spin without an explicit timeout, so wedged hardware can stall setup. Interrupt masks are built with `1ULL << (srn + i)`, so invalid ring numbering above 63 would overflow; CN93 has two mailbox registers but many other masks are single 64-bit values. CN98 deliberately skips soft reset, while CN93 performs a core-domain reset and manipulates firmware status around a documented hardware bug; wrong chip detection can produce stale firmware status or unexpected reset behavior. `octep_get_ethtool_stats()` later assumes queue stats for `OCTEP_MAX_QUEUES`, so active ring count consistency matters.

### Test Signals
Test CN93 and CN98 probe/remove, queue reset/setup/enable/disable, firmware reset and module removal after unexpected device reset, PF/VF mailbox interrupts for VFs above and below queue 64, OEI mailbox and heartbeat events, IOQ NAPI scheduling, ring error interrupt logging/clear, SR-IOV function-link-derived control mailbox address, register dumps, and recovery through `reinit_regs()` with traffic before and after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cn9k_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cnxk_pf.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cnxk_pf.c

### Purpose
`octep_cnxk_pf.c` provides CNXK physical-function hardware operations for the Octeon EP NIC driver. It is the CNXK counterpart to the CN9K PF file, with CNXK register offsets, interrupt layout, RX watermark handling, soft reset, and queue setup details.

### Important APIs, Types, And Functions
The exported entry point is `octep_device_setup_cnxk_pf()`, which fills the `oct->hw_ops` table. Key helpers are `cnxk_dump_regs()`, `cnxk_reset_iq()`, `cnxk_reset_oq()`, `octep_reset_io_queues_cnxk_pf()`, `octep_setup_pci_window_regs_cnxk_pf()`, `octep_configure_ring_mapping_cnxk_pf()`, `octep_init_config_cnxk_pf()`, `octep_setup_iq_regs_cnxk_pf()`, `octep_setup_oq_regs_cnxk_pf()`, `octep_setup_mbox_regs_cnxk_pf()`, mailbox/OEI pollers and interrupt handlers, error interrupt handlers, `octep_soft_reset_cnxk_pf()`, `octep_reinit_regs_cnxk_pf()`, interrupt enable/disable, IQ read-index update, queue enable/disable, and register dump helpers.

### Control Flow
Setup installs all CNXK ops, initializes PCI window registers, reads the PCIe port from `CNXK_SDP_MAC_NUMBER`, initializes configuration from CNXK PF/VF ring CSRs, maps PF rings, and marks firmware status running through a PCI window write. IQ setup waits for idle, configures 64-byte instructions and endian/size settings, writes descriptor base/size, stores queue MMIO pointers, resets completion count, and programs interrupt levels. OQ setup waits for idle, programs maximum watermark first, writes descriptor base/size, retries base programming for up to about 10 seconds if hardware does not latch it, configures packet buffer size, stores credit/count pointers, programs interrupt coalescing, and then sets the configured backpressure watermark.

Interrupt flow mirrors CN9K but uses CNXK register names and a CNXK non-IOQ MSI-X layout with OEI entries and a trailing IOQ name. PF/VF mailbox interrupts schedule per-VF mailbox work, OEI handles control mailbox and heartbeat, IOQ interrupts schedule NAPI, and error handlers log/clear ring, VF, DMA, PP, and misc error registers. Soft reset writes firmware status downing, asserts a chip-domain reset, delays briefly, and restores the window write mask.

### State, Persistence, And Dependencies
State persists in hardware CSRs, `oct->conf`, `oct->hw_ops`, per-queue register pointers, `oct->pcie_port`, heartbeat state, and mailbox/control work items. Dependencies include CNXK register definitions, common Octeon device and queue structures, PCI SR-IOV capability reads, jiffies/time helpers for OQ register retry, workqueue scheduling, and NAPI.

### Integration Points
Common Octeon probe code selects `octep_device_setup_cnxk_pf()` for CNXK PF PCI IDs. The common Tx/Rx datapath uses the installed queue operations and read-index callback. Control mailbox processing is driven by OEI events queued here. SR-IOV PF/VF mailbox support depends on the mailbox register setup and mailbox interrupt handlers.

### Risks
The idle waits for IQ/OQ setup have no explicit timeout; only the OQ descriptor-base latch retry is bounded. Interrupt masks still use 64-bit shifts based on `srn + i`, so ring numbering must stay within the mask model. `octep_setup_oq_regs_cnxk_pf()` can return `-EFAULT` or `-EAGAIN`, so callers must respect OQ setup failure or the queue may run with stale DMA base. The PF/VF mailbox poller only checks one mailbox interrupt register, unlike CN9K's two-register handling, so VF/ring topology assumptions are chip-specific and should not be generalized blindly.

### Test Signals
Exercise CNXK probe/remove, queue setup with descriptor-base retry, RX watermark/backpressure programming, soft reset and reinit, OEI control mailbox and heartbeat events, PF/VF mailbox delivery across supported VF counts, IOQ NAPI scheduling, all non-IOQ error interrupt handlers, register dump output, traffic before/after reset, and failure paths when OQ base programming returns `ULLONG_MAX` or times out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cnxk_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_config.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_config.h

### Purpose
`octep_config.h` defines static defaults, access macros, and configuration structures for Octeon EP queue, SR-IOV, MSI-X, control mailbox, firmware, heartbeat, offload, and MTU settings.

### Important APIs, Types, And Functions
Constants define IQ/OQ descriptor counts, 32/64-byte instruction modes, doorbell batching, interrupt thresholds, RX buffer size and refill threshold, queue wake threshold, MTU defaults, MSI-X name length, RX watermark, and firmware heartbeat defaults. `CFG_GET_*` macros provide shorthand accessors for nested fields in `struct octep_config`.

The main types are `struct octep_iq_config`, `struct octep_oq_config`, `struct octep_pf_ring_config`, `struct octep_sriov_config`, `struct octep_msix_config`, `struct octep_ctrl_mbox_config`, `struct octep_fw_info`, and aggregate `struct octep_config`.

### Control Flow
This header implements no control flow. Chip-specific PF setup files populate `struct octep_config` from hardware CSRs and defaults, while common queue, interrupt, mailbox, ethtool, and control-plane code reads it through direct fields or accessor macros.

### State, Persistence, And Dependencies
The configuration object is persistent per `struct octep_device` during driver lifetime. It captures maximum and active ring counts, SR-IOV limits, queue sizes, coalescing policy, BAR memory address for the control mailbox, firmware-provided interface info, offload flags, and heartbeat policy. It depends on networking constants such as `ETH_MIN_MTU`, `IFNAMSIZ`, `SKB_WITH_OVERHEAD()`, and `PAGE_SIZE`.

### Integration Points
CN9K/CNXK setup fills the configuration. Tx/Rx ring allocation and queue programming use IQ/OQ values. Interrupt allocation uses MSI-X counts and names. Control net initialization uses `CFG_GET_CTRL_MBOX_MEM_ADDR()`. Ettool channel reporting uses active/max IO rings. Firmware info returned over the control net protocol is stored in `fw_info`.

### Risks
Many macros are simple field accessors, so they do not validate null pointers or bounds. Queue descriptor counts are fixed at 1024 and documented as power-of-two; changing them affects ring wrap logic. `OCTEP_OQ_BUF_SIZE` depends on page-size SKB overhead and may vary by architecture. Active counts are populated from hardware and used in loops and interrupt masks, so invalid firmware/CSR values can propagate widely.

### Test Signals
Build on architectures with different page sizes, validate active ring counts against allocated arrays and interrupt masks, verify MTU boundary behavior, check RX refill and queue wake thresholds under traffic, confirm heartbeat defaults are overridden when firmware info is fetched, and test offload feature negotiation through `struct octep_fw_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cp_version.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cp_version.h

### Purpose
`octep_cp_version.h` defines the packed integer encoding used for Octeon EP control-plane protocol versions.

### Important APIs, Types, And Functions
The only public macro is `OCTEP_CP_VERSION(a, b, c)`, which packs three 8-bit version components into a 24-bit value with major in bits 23:16, minor in bits 15:8, and patch in bits 7:0.

### Control Flow
There is no control flow. The macro is used as a comparable integer by control-net version gates.

### State, Persistence, And Dependencies
The header owns no state. Its output values are stored in `octep_ctrl_mbox.version` and command-version tables in `octep_ctrl_net.c`.

### Integration Points
`octep_ctrl_net.h` includes this header, and `octep_ctrl_net.c` uses it to define `OCTEP_CP_VERSION_CURRENT` and minimum command versions for host-to-firmware and firmware-to-host commands.

### Risks
Each component is masked to 8 bits, so values above 255 wrap silently. Integer ordering works for major/minor/patch comparisons only while this packed format remains consistent across host and firmware. The file uses a BSD-3-Clause SPDX line while most local driver files are GPL-2.0, so license compatibility should remain intentional.

### Test Signals
Compile protocol users and validate version negotiation with firmware minimum and maximum versions, especially for commands added after 1.0.0 such as offload configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cp_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_mbox.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_mbox.c

### Purpose
`octep_ctrl_mbox.c` implements the low-level BAR-memory control mailbox shared between the host driver and Octeon firmware. It validates firmware readiness, initializes queue metadata, sends scatter-gather messages on the host-to-firmware ring, receives messages from the firmware-to-host ring, and tears the mailbox down.

### Important APIs, Types, And Functions
Public functions are `octep_ctrl_mbox_init()`, `octep_ctrl_mbox_send()`, `octep_ctrl_mbox_recv()`, and `octep_ctrl_mbox_uninit()`. Internal helpers define the BAR memory layout, queue offsets, circular queue increment/space/depth calculations, and wrap-aware `octep_write_mbox_data()` / `octep_read_mbox_data()` copies.

The implementation uses `struct octep_ctrl_mbox`, `struct octep_ctrl_mbox_q`, `struct octep_ctrl_mbox_msg`, and scatter-gather buffers described in `octep_ctrl_mbox.h`.

### Control Flow
Initialization checks a non-null mailbox and BAR pointer, reads the magic number, requires firmware status `READY`, reads firmware min/max protocol versions and BAR memory size, writes host status `INIT`, initializes queue locks, reads H2F/F2H queue sizes and producer/consumer register addresses, computes queue base pointers, writes host protocol version, uses a write memory barrier, and marks host status `READY`.

Send checks firmware status, locks the H2F queue, reads producer/consumer indices, verifies available space for header plus payload, writes the message header and SG payload segments with wrap handling, publishes the new producer index, and unlocks. Receive checks firmware status, locks F2H, verifies at least a header is available, reads the header and payload into caller buffers, writes the new consumer index, and unlocks. Uninit clears host version/status, uses a barrier, and destroys locks.

### State, Persistence, And Dependencies
Persistent state is shared in BAR memory: magic, host/firmware status, host/firmware versions, queue sizes, producer/consumer indices, and ring payload bytes. Host-side state stores queue pointers and mutexes in `struct octep_ctrl_mbox`. Dependencies include MMIO accessors, `memcpy_toio()`/`memcpy_fromio()`, mutexes, PCI/device logging, and the configuration/main Octeon headers.

### Integration Points
`octep_ctrl_net.c` initializes this mailbox, wraps messages in the control network protocol, waits for responses, and polls firmware notifications. Chip-specific PF files provide the BAR memory base in `octep_config`. OEI interrupts schedule the control mailbox task that drains messages.

### Risks
The circular queue depth/space helpers use `abs(pi - ci) % sz`, which treats producer and consumer as ordinary wrapped offsets and cannot distinguish full from empty without the protocol leaving slack; boundary conditions need firmware agreement. `octep_ctrl_mbox_recv()` does not validate null `mbox`/`msg` before reading firmware status, unlike send/init/uninit. Receive trusts `msg->hdr.s.sz` after reading the header and copies only as many bytes as caller SG buffers allow, leaving oversize-message truncation/consumer advancement behavior dependent on SG sizing. Send does not verify that SG buffers cover the declared payload size.

### Test Signals
Test mailbox init failures for null BAR, bad magic, firmware not ready, and version ranges. Exercise send and receive with wrapping payloads, exact-fit messages, empty rings, insufficient space, SG lists shorter/longer than declared payload, firmware status loss during operation, concurrent senders/receivers, uninit ordering, and integration with control-net request/response timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_mbox.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_mbox.h

### Purpose
`octep_ctrl_mbox.h` defines the BAR-memory mailbox ABI between the Octeon EP host driver and firmware, including layout documentation, message header format, SG message buffers, ring metadata, mailbox state, status values, flags, and the low-level mailbox API.

### Important APIs, Types, And Functions
Important constants include `OCTEP_CTRL_MBOX_MAGIC_NUMBER`, message header flags for request, response, notification, and custom messages, and `OCTEP_CTRL_MBOX_MSG_DESC_MAX`. `enum octep_ctrl_mbox_status` defines invalid/init/ready/uninit states. `union octep_ctrl_mbox_msg_hdr` encodes VF routing, payload size, flags, and message id. `struct octep_ctrl_mbox_msg_buf`, `struct octep_ctrl_mbox_msg`, `struct octep_ctrl_mbox_q`, and `struct octep_ctrl_mbox` describe caller buffers, queue MMIO pointers, locks, BAR memory, and supported firmware versions. The declared functions are init, send, receive, and uninit.

### Control Flow
The header documents a shared memory layout: fixed info block, host and firmware version/status areas, H2F queue info, F2H queue info, then two variable-size queues. Runtime control flow is implemented in `octep_ctrl_mbox.c`, but callers are expected to initialize the mailbox before sending/receiving and uninitialize it on device teardown.

### State, Persistence, And Dependencies
The ABI persists in PCI BAR memory shared with firmware. Host state tracks the BAR base, queue bases, producer/consumer register pointers, queue sizes, two mutexes, and firmware-supported version interval. The header itself depends on kernel bit macros and types included by consumers.

### Integration Points
`octep_ctrl_net` embeds mailbox messages to implement network control commands. Chip-specific PF setup supplies the `barmem` address. PF/VF and firmware notification paths use the header flags to distinguish responses from async notifications and VF-targeted messages.

### Risks
This is a binary ABI with firmware. Bitfield layout in `union octep_ctrl_mbox_msg_hdr` must match firmware compiler/endianness expectations. The header has a leading space before the include guard directive, harmless for C but unusual. Payload sizes and maximum SG descriptors are caller-managed; a mismatch between `hdr.s.sz` and SG buffers can cause truncation or stale data at the protocol layer. Version fields are split across host and firmware status areas and must be updated with the barriers in the C implementation.

### Test Signals
ABI tests should verify header size, field offsets, BAR layout offsets, status transitions, request/response/notify flag interpretation, VF index routing, max SG behavior, firmware version negotiation, and compatibility with firmware built independently of the host driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_mbox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_net.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_net.c

### Purpose
`octep_ctrl_net.c` implements the Octeon EP network control protocol on top of the low-level control mailbox. It sends host-to-firmware commands for link status, RX state, MAC address, MTU, interface stats, link information, firmware info, device removal, and offloads; it also processes firmware responses and link notifications.

### Important APIs, Types, And Functions
Public APIs include `octep_ctrl_net_init()`, `octep_ctrl_net_get_link_status()`, `octep_ctrl_net_set_link_status()`, `octep_ctrl_net_set_rx_state()`, `octep_ctrl_net_get_mac_addr()`, `octep_ctrl_net_set_mac_addr()`, `octep_ctrl_net_get_mtu()`, `octep_ctrl_net_set_mtu()`, `octep_ctrl_net_get_if_stats()`, `octep_ctrl_net_get_link_info()`, `octep_ctrl_net_set_link_info()`, `octep_ctrl_net_recv_fw_messages()`, `octep_ctrl_net_get_info()`, `octep_ctrl_net_dev_remove()`, `octep_ctrl_net_set_offloads()`, and `octep_ctrl_net_uninit()`.

Internal helpers are `init_send_req()`, `octep_send_mbox_req()`, `process_mbox_resp()`, and `process_mbox_notify()`. The file maintains `ctrl_net_msg_id` and command-version tables for host-to-firmware and firmware-to-host commands.

### Control Flow
Initialization creates the response wait queue and wait list, fills `oct->ctrl_mbox` with current host protocol version and BAR memory from config, initializes the low-level mailbox, logs version ranges, and stores the firmware stats offset. Each get/set API builds a stack `octep_ctrl_net_wait_data`, initializes a mailbox request header and one SG buffer, fills a command-specific payload, sends it, and optionally waits up to 500 ms for a matching response.

`octep_send_mbox_req()` rejects commands outside the firmware-supported version interval, sends through `octep_ctrl_mbox_send()`, queues wait data on `oct->ctrl_req_wait_list` for synchronous requests, sleeps on `oct->ctrl_req_wait_q`, removes the wait-list node, and checks firmware reply status. `octep_ctrl_net_recv_fw_messages()` drains all currently available firmware messages; responses are copied into the matching wait-data object by message id, while notifications update netdev carrier state or forward VF notifications to PF/VF mailbox handling.

### State, Persistence, And Dependencies
State lives in `oct->ctrl_mbox`, `oct->ctrl_req_wait_q`, `oct->ctrl_req_wait_list`, `oct->ctrl_mbox_ifstats_offset`, cached `oct->link_info`, firmware stats fields, netdev carrier state, and the atomic message id. The protocol depends on `octep_ctrl_mbox`, firmware version compatibility, `octep_ctrl_net.h` ABI structures, wait queues, list operations, PCI/netdev logging, and PF/VF notification support.

### Integration Points
Main driver open/close/configuration paths use these APIs to synchronize MTU, MAC, link, RX state, offloads, firmware info, and device removal with firmware. Ettool uses link-info and stats commands. Chip-specific PF OEI interrupt handlers schedule control mailbox work, which calls `octep_ctrl_net_recv_fw_messages()`. PF/VF support receives VF notifications through `octep_pfvf_notify()`.

### Risks
The wait list is modified without an obvious local lock; correctness depends on serialization by caller/task context or external locking. `wait_event_interruptible_timeout()` returns negative on signal, but the code treats only `ret == 0 || ret == 1` as timeout-like and does not explicitly handle `ret < 0`, so interrupted waits can proceed to inspect an unset response. Message id masking uses `GENMASK(sizeof(msg_id) * BITS_PER_BYTE, 0)`, which requests one bit more than the 16-bit field width before assignment truncates. Version checks index command-version arrays by firmware-supplied or caller-filled command values, so invalid command values need bounds discipline.

### Test Signals
Test every get/set command against firmware versions 1.0.0 and 1.0.1 boundaries, synchronous response matching under concurrent requests, timeout and interrupted wait behavior, malformed response ids, firmware notifications for link up/down while netdev is running/stopped, VF-targeted notifications, mailbox receive drain loops, stats fetch failures, dev-remove during uninit with pending requests, and offload command rejection when firmware max version is below 1.0.1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_net.h -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_net.h

### Purpose
`octep_ctrl_net.h` defines the host/firmware network-control protocol layered on the Octeon EP control mailbox. It enumerates commands, command directions, states, replies, request/response payloads, link/offload structures, max transfer union, wait-data storage, and public control-net APIs.

### Important APIs, Types, And Functions
Key enums are `octep_ctrl_net_cmd`, `octep_ctrl_net_state`, `octep_ctrl_net_reply`, `octep_ctrl_net_h2f_cmd`, and `octep_ctrl_net_f2h_cmd`. Request/response headers carry sender, receiver, command, and reply fields. Payload structs cover MTU, MAC address, link/RX state, link modes/autoneg/pause/speed, offloads, interface stats, and firmware info. `union octep_ctrl_net_max_data` sizes mailbox buffers for any protocol message. `struct octep_ctrl_net_wait_data` stores pending synchronous requests on a list with response data.

The declared API covers initialization, link status set/get, RX state, MAC set/get, MTU set/get, interface stats, link info set/get, firmware message receive, firmware info fetch, device removal notification, offload setting, and uninitialization.

### Control Flow
The header describes request/response shapes. Callers invoke the C implementation to build H2F requests and wait for H2F responses. Firmware can send F2H link-status notifications, which the implementation either applies to the PF netdev or forwards for VF handling.

### State, Persistence, And Dependencies
The protocol state persists in in-flight wait-data objects, firmware-visible command payloads, and cached device fields populated from responses. The header depends on `octep_cp_version.h`, firmware info from `octep_config.h` via included users, and statistics/link types from `octep_main.h` through C-file include order.

### Integration Points
Ettool depends on link info and interface stats types. Main netdev operations depend on MAC, MTU, link, RX state, offload, and device removal APIs. PF/VF mailbox code integrates through VF notification routing. The low-level mailbox uses the message sizes and buffers defined here as payloads.

### Risks
This is a packed firmware ABI. Field sizes, alignment, enum values, and command IDs must stay stable across host and firmware. The `link_info` structure uses 64-bit bitmaps internally, while ethtool code stores some fields in `u32`, so newly added high link-mode bits could be truncated. The wait-data object embeds list nodes and stack request/response storage, making lifetime correct only while synchronous waits remain active and properly removed.

### Test Signals
Validate structure sizes and offsets against firmware, command enum compatibility, max-data sizing, link mode bitmaps above 32 bits, VF id routing with `OCTEP_CTRL_NET_INVALID_VFID`, all public API payloads, async F2H link notification parsing, and wait-data cleanup during timeout and uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ethtool.c

### Purpose
`octep_ethtool.c` provides ethtool support for the Octeon EP NIC driver. It reports driver identity, link state, global and per-queue statistics, supported/advertised link modes, link settings updates, and channel counts.

### Important APIs, Types, And Functions
The public entry point is `octep_set_ethtool_ops()`, which assigns `octep_ethtool_ops` to a netdev. Operations include `octep_get_drvinfo()`, `octep_get_strings()`, `octep_get_sset_count()`, `octep_get_ethtool_stats()`, `octep_get_link_ksettings()`, `octep_set_link_ksettings()`, and `octep_get_channels()`. Static string tables define global stats and per-Tx/per-Rx queue stat names. `OCTEP_SET_ETHTOOL_LINK_MODES_BITMAP` maps firmware Octeon link-mode bits to ethtool link-mode bits.

### Control Flow
Stats reporting builds ethtool string output for global counters and active queues, then fetches firmware interface stats through `octep_ctrl_net_get_if_stats()` and aggregates software per-queue stats from `oct->stats_iq[]` and `oct->stats_oq[]`. Link settings get flow fetches firmware link info, clears ethtool supported/advertising bitmaps, maps Octeon speed bits, sets autoneg and pause bits, reports fibre port, and returns speed/duplex only when carrier is up. Link settings set flow validates duplex, autoneg support, and advertising subset, maps ethtool advertised modes back to Octeon bits, sends new link info to firmware, and updates the cached `oct->link_info` on success. Channel reporting exposes maximum and active IO ring counts from config.

### State, Persistence, And Dependencies
State is read from `struct octep_device`: PCI device, config, queue stats, firmware stats caches, link info cache, and netdev carrier. Persistent link changes are delegated to firmware through `octep_ctrl_net_set_link_info()`. Dependencies include Linux ethtool APIs, PCI naming, netdev private data, Octeon config macros, firmware control-net APIs, and Octeon link-mode constants.

### Integration Points
Main netdev setup calls `octep_set_ethtool_ops()`. User space reaches these operations through `ethtool -i`, `-S`, `-k`-like stats consumers, `ethtool <dev>` link settings, and channel queries. Control-net firmware commands supply hardware stats and link information; queue datapath code supplies software queue counters.

### Risks
`octep_get_sset_count()` uses the active queue count, but `octep_get_ethtool_stats()` loops over `OCTEP_MAX_QUEUES` for per-queue stats, which can write more values than the string/count path exposes if active queues are less than the maximum. Firmware command errors from stats and link-info getters are ignored, so ethtool can report stale or zeroed cached values. Link-mode mapping in `octep_get_link_ksettings()` stores 64-bit firmware bitmaps in `u32`, truncating high bits if future modes use them. The set path compares `cmd->base.autoneg` to `link_info->autoneg`, but `link_info->autoneg` is a firmware bitfield, not just `AUTONEG_ENABLE/DISABLE`.

### Test Signals
Run `ethtool -i`, `ethtool -S`, link settings get/set, and channel queries with different active queue counts. Validate stats buffer sizing, firmware stats failure behavior, link mode mapping for all advertised speeds, autoneg and pause reporting, unsupported duplex rejection, advertising subset rejection, firmware link-info set failures, carrier up/down reporting, and high-bit link-mode preservation if new firmware modes are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ethtool.c -->
