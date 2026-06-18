# subset-b-004513 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/ptp.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/ptp.c

## Purpose
`ptp.c` implements the Marvell OcteonTX2/CN10K PTP PCI function used by the RVU Admin Function driver. It maps the PTP CSR BAR, enables and calibrates the hardware PTP clock, exposes clock read/adjust/PPS/timestamp operations through RVU mailbox handlers, and handles CN10K A0/A1 errata for nanosecond rollover and PPS threshold programming. It is not a Linux `ptp_clock_info` provider by itself in this file; instead, AF consumers reach it through `rvu_mbox_handler_ptp_op()` and `rvu_mbox_handler_ptp_get_cap()`.

## Important APIs, Types, and Functions
- Device matching is driven by `ptp_id_table` and the exported `struct pci_driver ptp_driver`.
- `ptp_probe()` allocates `struct ptp`, enables the PCI function, maps BAR0, initializes the spinlock and errata-specific timestamp reader, and records the first discovered block in `first_ptp_block`.
- `ptp_get()` and `ptp_put()` are the RVU side acquisition/release hooks; they detect absent hardware, probe deferral, and failed PTP probe state.
- `ptp_start()` programs clock source selection, timestamp input configuration, rollover registers, PTP enable, atomic set operation, and `PTP_CLOCK_COMP`.
- `ptp_adjfine()` updates frequency compensation from scaled ppm, with an errata-specific recalculation path through `ptp_calc_adjusted_comp()`.
- `ptp_atomic_update()` and `ptp_atomic_adjtime()` use CN10K atomic set/inc/dec CSRs when supported.
- `ptp_pps_on()`, `ptp_set_thresh()`, `ptp_config_hrtimer()`, and `ptp_reset_thresh()` configure PPS output and work around older CN10K threshold timing.
- `ptp_get_clock()` reads the running PTP clock; `ptp_get_tstmp()` reads an external timestamp capture register, with CN10K A-format unpacking.
- `rvu_mbox_handler_ptp_op()` dispatches mailbox operations such as `PTP_OP_ADJFINE`, `PTP_OP_GET_CLOCK`, `PTP_OP_GET_TSTMP`, `PTP_OP_SET_THRESH`, `PTP_OP_PPS_ON`, `PTP_OP_ADJTIME`, and `PTP_OP_SET_CLOCK`.

## Control Flow
Module initialization in `rvu.c` registers `ptp_driver` before the RVU AF driver. When the PTP PCI function probes, `ptp_probe()` maps the register window and stores a global pointer. Later, `rvu_probe()` calls `ptp_get()` and keeps the pointer in `rvu->ptp`; after firmware data is mapped, `ptp_start()` receives the system clock, optional external clock rate, and external timestamp GPIO selector from `rvu->fwdata`.

At runtime, PF/VF drivers send PTP mailbox requests to AF. `rvu_mbox_handler_ptp_op()` validates that `rvu->ptp` exists, then calls the local helper for the requested operation. Clock reads use the function pointer set at probe: old CN10K errata silicon reads seconds and nanoseconds under `ptp_lock` and compensates for rollover; other devices read the nanosecond counter directly. Frequency adjustment computes a fixed-point compensation value and writes `PTP_CLOCK_COMP`. Clock set and adjustment use the atomic timestamp registers; sub-second deltas use hardware increment/decrement while larger deltas compute a replacement timestamp.

PPS enable writes PPS threshold and high/low increment registers. For the CN10K errata path, only a one-second period is accepted and an hrtimer periodically rewrites the threshold before the hardware rollover boundary. Removal cancels the timer when needed, disables PTP in `PTP_CLOCK_CFG`, and frees the in-memory object.

## State and Persistence Behavior
Persistent state is hardware-resident in PTP CSRs: clock enable/source bits, compensation, timestamp capture, atomic update registers, PPS threshold/increment, and rollover registers. Driver state is runtime-only in `struct ptp`: PCI device, mapped CSR base, selected timestamp reader, spinlock, hrtimer, last hrtimer timestamp, clock rate, and computed clock period. `first_ptp_block` is a single global pointer/error sentinel used by RVU probe. There is no disk persistence, and RVU releases only the PCI device reference through `ptp_put()`.

## Dependencies and Integration Points
The file depends on Linux PCI, MMIO, hrtimer, ktime, bitfield, and module APIs. It integrates with `rvu.c` through `ptp_get()`, `ptp_put()`, `ptp_start()`, and the exported `ptp_driver`. It depends on mailbox definitions from `mbox.h` for request/response layouts and on RVU silicon helpers such as `is_rvu_otx2()` for atomic-update capability checks. Firmware data consumed by `rvu_probe()` supplies SCLK, external clock, and external timestamp selector values.

## Risks and Edge Cases
- `first_ptp_block` represents only the first PTP block; multi-block systems would need careful handling.
- `ptp_atomic_adjtime()` has a suspicious negative large-delta branch that sets `ptp_clock_hi = delta - ptp_clock_hi` when the current counter is smaller than the delta; that may not represent a signed subtract modulo the full timestamp domain.
- `ptp_put()` assumes a non-error pointer; callers must not pass an `ERR_PTR`.
- CN10K A0/A1 PPS support is constrained to one-second periods and depends on hrtimer scheduling close to the rollover boundary.
- `ptp_calc_adjusted_comp()` uses integer arithmetic and a loop around rollover behavior; regression tests should cover low/high clock rates and errata variants.
- `ptp_remove()` frees the object but does not explicitly clear `first_ptp_block`; driver unload ordering currently protects normal use, but stale global pointer behavior would be risky under unusual hot-remove ordering.

## Test Signals
- Build and probe with OcteonTX2 and CN10K device IDs, including CN10K A0/A1 errata revisions and later silicon.
- Exercise mailbox operations for clock read, captured timestamp read, fine adjustment, atomic set, atomic adjust, PPS enable/disable, and threshold set.
- Verify `ptp_get()` returns `-ENODEV` with no hardware, `-EPROBE_DEFER` before PTP probe, and probe errors when `ptp_probe()` fails.
- Inject invalid PPS periods on errata devices and periods above eight seconds on all devices.
- Confirm hrtimer cancellation on PPS disable/remove and absence of timer callbacks after teardown.
- Compare adjusted hardware clock drift against expected scaled ppm for both normal and errata compensation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/ptp.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/ptp.h

## Purpose
`ptp.h` declares the small RVU-private PTP device state structure and the PTP driver hooks consumed by the RVU Admin Function. It provides the compile unit contract between the PTP PCI side driver in `ptp.c` and the RVU AF lifecycle in `rvu.c`.

## Important APIs, Types, and Functions
- `struct ptp` stores the PTP PCI device, MMIO base, timestamp read callback, timestamp spinlock, CN10K errata hrtimer state, input clock rate, and derived clock period.
- `struct rvu;` is forward-declared so `ptp_start()` can accept an RVU object without including the full RVU definition in every consumer.
- `ptp_get()` returns a referenced PTP block or an error pointer.
- `ptp_put()` drops the PCI device reference acquired by `ptp_get()`.
- `ptp_start()` programs and enables the PTP clock once RVU firmware data is available.
- `extern struct pci_driver ptp_driver` lets `rvu.c` register and unregister the PTP PCI driver as part of the overall AF module lifecycle.

## Control Flow
The header has no executable control flow. Its declarations are used by `rvu_init_module()` to register the PTP PCI driver before the AF driver, by `rvu_probe()` to acquire and start the PTP block, and by `rvu_remove()`/error unwinds to release it. Runtime mailbox PTP operations are implemented in `ptp.c` and declared indirectly through the mailbox handler macro expansion in `rvu.h`, not here.

## State and Persistence Behavior
All state described here is in-memory and device-lifetime scoped. The hardware clock configuration itself lives in PTP CSRs accessed through `reg_base`; the fields in `struct ptp` are cached pointers, callbacks, and timer bookkeeping. There is no persistent storage.

## Dependencies and Integration Points
The header depends on Linux timecounter/time64 declarations, spinlocks, hrtimers through included kernel headers, and PCI types via users including it. It is included by both `ptp.c` and `rvu.h`, and it sits on the boundary between the PTP PCI function and the broader RVU AF driver.

## Risks and Edge Cases
- The header exposes `struct ptp` internals rather than an opaque type, so future consumers could bypass the locking and helper APIs.
- `clock_rate` and `clock_period` are `u32`; this is adequate for current rates used by the driver but should be reviewed if larger external clock rates are introduced.
- Consumers must respect the `ptp_get()`/`ptp_put()` reference contract and must not dereference error pointers.

## Test Signals
- Compile all RVU AF files with this header included in both PTP and non-PTP call sites.
- Static analysis should flag direct `struct ptp` field access outside `ptp.c` if new consumers are added.
- Probe/remove tests should verify reference balance between `ptp_get()` and `ptp_put()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rpm.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rpm.c

## Purpose
`rpm.c` implements CN10K RPM/RPM2 MAC operations behind the common CGX/RPM `mac_ops` interface. It reads and writes RPM CSRs for LMAC enablement, pause/PFC flow control, PTP timestamp prepending, internal loopback, statistics, FEC counters, FIFO sizing, MAC reset, and X2P reset handling. The RVU CGX mailbox layer calls these operations without needing to know whether the physical MAC is older CGX, RPM, or RPM2.

## Important APIs, Types, and Functions
- `rpm_mac_ops` and `rpm2_mac_ops` populate the common `struct mac_ops` callback table with RPM-specific register offsets, interrupt registers, feature limits, statistic counts, and function pointers.
- `is_dev_rpm2()` distinguishes CN10KB RPM2 from RPM.
- `rpm_get_mac_ops()` selects the correct ops table.
- `rpm_get_nr_lmacs()` and `rpm2_get_nr_lmacs()` derive active LMAC count from LMAC bitmap CSRs.
- `rpm_lmac_tx_enable()`, `rpm_lmac_rx_tx_enable()`, and `rpm_enadis_rx()` control MAC Tx/Rx enable bits.
- `rpm_lmac_enadis_pause_frm()`, `rpm_lmac_pause_frm_config()`, `rpm_lmac_get_pause_frm_status()`, and `rpm_lmac_enadis_rx_pause_fwding()` implement 802.3x pause behavior.
- `rpm_lmac_pfc_config()`, `rpm_lmac_get_pfc_frm_cfg()`, and `rpm_cfg_pfc_quanta_thresh()` implement priority flow control class masks and quanta registers.
- `rpm_get_rx_stats()`, `rpm_get_tx_stats()`, `rpm_stats_reset()`, and `rpm_get_fec_stats()` read latched counter pages and reset statistics.
- `rpm_lmac_internal_loopback()` and `rpmusx_lmac_internal_loopback()` configure PCS loopback, rejecting SGMII/QSGMII LPC modes.
- `rpm_lmac_ptp_config()` enables RX timestamp prepending and one-step timestamp mode.
- `rpm_lmac_reset()` resets PFC-related CSRs and clears loopback on PF-requested FLR; `rpm_x2p_reset()` gates MAC-to-NIX path reset.

## Control Flow
`rvu_cgx_init()` obtains MAC private data through CGX helpers and calls `get_mac_ops()`, which can return the tables defined here. From then on, mailbox handlers in `rvu_cgx.c` route MAC requests through the table. For example, a CGX/RPM start request calls `mac_rx_tx_enable`, pause requests call `mac_enadis_pause_frm`, PTP RX enable calls `mac_enadis_ptp_config`, and stats requests call `mac_get_rx_stats`/`mac_get_tx_stats`.

Most helpers validate the LMAC through `is_lmac_valid()` and then perform direct read-modify-write sequences using `rpm_read()`/`rpm_write()`, which delegate to CGX MMIO accessors. Statistic and FEC paths acquire `rpm->lock` because reading a low counter latches a shared high register. Flow-control configuration is layered: PFC quanta helpers update per-class pause timers, RPM/RPM2 backpressure helpers update the correct generation-specific override register, and public pause/PFC helpers update MAC command config bits.

## State and Persistence Behavior
Driver state lives in the shared RPM/CGX private object (`rpm_t`): PCI device, lock, FIFO length, LMAC bitmap, max LMAC count, MAC ops pointer, and per-LMAC link metadata. Hardware state persists in RPM CSRs until reset: command config bits, pause/PFC class registers, stats counters, FEC capture state, PTP prepend and one-step mode, loopback bits, and X2P reset. The driver does not persist configuration outside hardware and in-memory link state.

## Dependencies and Integration Points
The file depends on `cgx.h` and `lmac_common.h` for `rpm_t`, `struct mac_ops`, LMAC validation, firmware-interface command helpers, link mode data, and generic CGX read/write access. It is integrated by `rvu_cgx.c` through `get_mac_ops()` and by mailbox handlers that expose MAC control to PF/VF drivers. PTP configuration integrates with NPC parser timestamp shifting and MCS configuration through callers in `rvu_cgx.c`.

## Risks and Edge Cases
- Many functions return `-ENODEV` on invalid LMAC, but some void helpers silently return; callers should not assume a hardware write occurred.
- `rpm_lmac_tx_enable()` returns the previous Tx-enabled state rather than a conventional zero/negative status, which is intentional for its caller but easy to misuse.
- Flow-control paths must prevent conflicting 802.3x pause and PFC modes; this file depends on `rvu_cgx.c` permission and conflict checks for some cases.
- Statistic and FEC high-half registers are shared and must remain protected by `rpm->lock`; adding unlocked reads risks mixed counter values.
- RPM2 has different global/per-LMAC backpressure and PFC registers; wrong ops selection would corrupt unrelated register space.
- FIFO partition logic depends on LMAC bitmap and high-performance LMAC fields; unusual three-LMAC and eight-LMAC RPM2 layouts need coverage.

## Test Signals
- Exercise all `mac_ops` callbacks on RPM and RPM2 hardware or MMIO mocks.
- Verify invalid LMAC handling for each public helper.
- Validate pause/PFC enable, disable, class mask, quanta, and conflict behavior from mailbox callers.
- Read RX/TX/FEC statistics under concurrent access and confirm high/low halves are consistent.
- Run PTP RX enable/disable tests that also verify NPC parser shift and one-step mode side effects through the caller path.
- Test FLR/reset paths for PFC CSR reset, loopback clearing, RX disable before X2P reset, and X2P reset release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rpm.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rpm.h

## Purpose
`rpm.h` defines RPM/RPM2 device IDs, register offsets, bit masks, constants, and function prototypes for the CN10K RPM MAC implementation. It is the register contract used by `rpm.c`, CN10K channel programming in `rvu_cn10k.c`, and generic CGX/RPM integration code.

## Important APIs, Types, and Functions
- Device IDs include `PCI_DEVID_CN10K_RPM`, `PCI_SUBSYS_DEVID_CNF10KB_RPM`, and `PCI_DEVID_CN10KB_RPM`.
- Register macros describe common RPM CSRs such as `RPMX_CMRX_CFG`, `RPMX_CMR_GLOBAL_CFG`, `RPMX_CMRX_LINK_CFG`, `RPMX_MTI_MAC100X_COMMAND_CONFIG`, PCS loopback, statistics, FEC, pause, PFC, and timestamp mode registers.
- RPM2-specific macros describe alternative CSR offsets such as `RPM2_CMRX_SW_INT`, `RPM2_CMR_CHAN_MSK_OR`, `RPM2_CMR_RX_OVR_BP`, `RPM2_CMRX_PRT_CBFC_CTL`, `RPM2_CMRX_RX_LMACS`, and `RPM2_USX_PCSX_CONTROL1`.
- Bit masks include Rx/Tx enable, PTP prepend and one-step support, pause ignore/disable/forwarding bits, PFC class mask, FEC capture/clear bits, channel base/range fields, and X2P reset.
- Prototypes expose all RPM callback implementations used by the `mac_ops` tables, including LMAC count/type/FIFO queries, loopback, pause/PFC, stats, PTP, reset, and Rx/Tx control.

## Control Flow
The header has no runtime control flow. It shapes how `rpm.c` performs register read-modify-write sequences and how other files call RPM helpers. `rvu_cn10k.c` also uses `RPMX_CMRX_LINK_CFG` and its base/range masks when programming RPM channel windows.

## State and Persistence Behavior
The file defines hardware register layout rather than owning state. Values written through these macros persist in RPM/RPM2 CSRs until reset or later reconfiguration. The prototypes operate on opaque `void *rpmd`/`void *cgxd` handles that point to CGX/RPM private runtime state managed elsewhere.

## Dependencies and Integration Points
`rpm.h` includes Linux bit helpers and depends on types declared by included users, notably `struct cgx_fec_stats_rsp`. It is included by the RPM implementation and can be reached indirectly through CGX/RVU code. It forms the bridge between generic MAC operations and generation-specific RPM register offsets.

## Risks and Edge Cases
- Some macros are duplicated, such as pause and statistic register definitions; future edits must avoid diverging duplicate values.
- RPM and RPM2 offsets differ for several features; using RPM macros on RPM2 paths can write the wrong registers.
- Function prototypes use `void *` handles, so type safety is delegated to callers.
- Bitfield masks such as `RPM_PFC_CLASS_MASK` encode packed register layout; any hardware revision change needs coordinated updates in both header and implementation.

## Test Signals
- Compile-test all consumers after changing register macros or prototypes.
- Static analysis should check duplicate macro definitions for value consistency.
- Hardware register tests should verify RPM and RPM2 offsets used by `rpm.c` and `rvu_cn10k.c`.
- ABI-style tests should confirm `mac_ops` callback signatures stay aligned with prototypes in this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu.c

## Purpose
`rvu.c` is the core Marvell OcteonTX2/CN10K RVU Admin Function PCI driver. It discovers implemented RVU hardware blocks, resets and initializes AF-owned resources, manages LF allocation for PF/VF functions, configures MSI-X vector ownership, initializes mailbox channels, processes AF mailbox messages, handles PF/VF FLR teardown, registers interrupts, enables AF SR-IOV VFs, starts CGX/NIX/NPA/NPC/MCS/CPT/SDP support, and owns module-level registration of CGX, PTP, MCS, and RVU PCI drivers.

## Important APIs, Types, and Functions
- Resource bitmap helpers: `rvu_alloc_rsrc()`, `rvu_alloc_rsrc_contig()`, `rvu_free_rsrc()`, `rvu_rsrc_free_count()`, `rvu_alloc_bitmap()`, and related checks.
- Block and PF/VF mapping helpers: `rvu_get_lf()`, `rvu_get_blkaddr()`, `rvu_update_rsrc_map()`, `rvu_get_pf_numvfs()`, `rvu_get_hwvf()`, `rvu_get_pfvf()`, `is_pffunc_map_valid()`, and `rvu_get_blkaddr_from_slot()`.
- Hardware setup helpers: `rvu_check_block_implemented()`, `rvu_reset_all_blocks()`, `rvu_setup_hw_capabilities()`, `rvu_setup_hw_resources()`, `rvu_setup_msix_resources()`, and `rvu_setup_pfvf_macaddress()`.
- Mailbox handlers in this file include `ready`, `attach_resources`, `detach_resources`, `msix_offset`, `free_rsrc_cnt`, `vf_flr`, `get_hw_cap`, `set_vf_perm`, and `ndc_sync_op`.
- Mailbox core is implemented by `rvu_process_mbox_msg()`, `__rvu_mbox_handler()`, `rvu_queue_work()`, `rvu_mbox_init()`, and `rvu_mbox_destroy()`.
- FLR logic is implemented by `__rvu_flr_handler()`, `rvu_blklf_teardown()`, `rvu_flr_handler()`, `rvu_afvf_flr_handler()`, and `rvu_flr_intr_handler()`.
- Interrupt lifecycle is handled by `rvu_register_interrupts()`, `rvu_unregister_interrupts()`, `rvu_enable_mbox_intr()`, and AFVF interrupt helpers.
- PCI/module lifecycle is handled by `rvu_probe()`, `rvu_remove()`, `rvu_shutdown()`, `rvu_init_module()`, and `rvu_cleanup_module()`.

## Control Flow
Module init registers dependent PCI drivers first (`cgx_driver`, `ptp_driver`, `mcs_driver`) and then registers `rvu_driver`. `rvu_probe()` allocates `struct rvu` and `struct rvu_hwinfo`, enables PCI, maps AF/PF BARs, acquires the PTP block, reads module profile parameters, discovers implemented blocks, resets all blocks, sets capability flags, and calls `rvu_setup_hw_resources()`.

`rvu_setup_hw_resources()` reads RVU constants, initializes block descriptors and LF bitmaps for NPA/NIX/SSO/SSOW/TIM/CPT, allocates PF/VF state arrays, maps firmware data, maps MSI-X tables, scans pre-provisioned LFs, programs channel bases, initializes NPC/CGX/exact-match/NPA/NIX/SDP/MCS/CPT, starts CGX link-up, and unblocks NIX broadcast XON. Back in probe, AF-PF mailbox channels, FLR work, interrupts, devlink, AF VFs, debugfs, RVU switch lock, PTP start, and AF CINT/QINT memory are initialized.

Runtime mailbox interrupts queue per-PF/per-VF work. `__rvu_mbox_handler()` stamps trusted `pcifunc` identity based on the interrupt source, dispatches through the generated `MBOX_MESSAGES` switch in `rvu_process_mbox_msg()`, allocates responses, records handler return codes, and sends replies. Attach resource messages validate availability under `rsrc_lock`, allocate block LFs, write LF config registers, update software counts, and assign MSI-X offsets. Detach and FLR paths tear down NIX/NPA/CPT and other block LFs, reset hardware LFs, restore LMTST maps, detach resource maps, clear MCAM entries, reset MAC state, and notify MCS when present.

Removal reverses the lifecycle: debugfs/devlink/interrupts/FLR work/CGX/firmware/MCS/mailbox/SR-IOV are torn down, blocks are reset, resources freed, RVUM revision cleared, PTP reference dropped, PCI regions released, and memory freed.

## State and Persistence Behavior
`struct rvu` owns runtime state for mapped BARs, hardware info, PF/VF arrays, resource locks, mailbox workqueues, FLR workqueue, MSI-X mappings, CGX maps, firmware data, PTP, MCS/CPT locks, representor state, and devlink/debugfs handles. `struct rvu_hwinfo` owns block descriptors, capability flags, NIX/NPC resource models, and channel bases. `struct rvu_pfvf` stores per-function LF ownership, MSI-X allocation, queue memory pointers, NIX/NPA bitmaps, MAC addresses, channel ranges, PTP timestamp flag, default multicast/promisc state, LMT map defaults, and permissions. Hardware state persists in RVU block registers until reset; the software state is rebuilt at probe and destroyed at remove. Firmware data is memory-mapped read-only-ish shared platform state.

## Dependencies and Integration Points
This file is the hub for `cgx`, `ptp`, `mcs`, `npc`, `npa`, `nix`, `cpt`, `sdp`, devlink, debugfs, mailbox, CN10K, and CN20K support. It depends on Linux PCI/MSI-X/DMA/workqueue/interrupt/mutex APIs and on AF register definitions from `rvu_reg.h`. It integrates with PF/VF netdev drivers exclusively through mailbox shared memory and interrupts. It also maps firmware data from CGX-provided base addresses and configures PTP from firmware clock fields.

## Risks and Edge Cases
- `rvu_lookup_rsrc()` spins without a timeout while waiting for a lookup bit to clear.
- `rvu_clear_msix_offset()` uses the returned offset even if `rvu_get_msix_offset()` reports `MSIX_VECTOR_INVALID`, so callers rely on prior mapping consistency.
- Error unwinding in `rvu_setup_hw_resources()` is broad and crosses many subsystems; partial initialization needs leak and double-free coverage.
- `rvu_remove()` destroys the AF-PF mailbox before disabling SR-IOV/AFVF mailbox, while live VFs could still be quiescing; interrupt disable ordering is critical.
- `rvu_mbox_init()` assigns `rvu->ng_rvu` each time it initializes a mailbox class; ownership/freeing must stay aligned for AFPF and AFVF paths.
- Resource attach supports modify semantics by detaching and reattaching multi-slot blocks, making partial failure rollback important.
- FLR ordering encodes inter-block dependencies; changing it can leak packet sources, pools, MCAM entries, or MAC state.
- Firmware data mismatch or absence changes MAC/PTP/channel behavior and must be handled gracefully.

## Test Signals
- Probe/remove and repeated module load/unload across OcteonTX2, CN10K, CN20K, with and without NIX1/CPT1/MCS/PTP/firmware data.
- Fault injection for allocation failures, mailbox region mapping failures, MSI-X mapping failures, subsystem init failures, and interrupt registration failures.
- Mailbox tests for attach/detach/modify/free-count/msix-offset/ready/hw-cap/permissions/NDC sync, including invalid PF/VF IDs.
- FLR tests for PF, VF, AFVF, and mailbox-requested VF FLR with NIX/NPA/CPT/TIM/SSO/SSOW resources attached.
- Concurrency tests around `rsrc_lock`, `mbox_lock`, and `flr_lock` with simultaneous mailbox attach/detach and FLR.
- SR-IOV tests with too few vectors, more VFs than LBK channels, and >64 VF interrupt sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu.h

## Purpose
`rvu.h` is the central private header for the OcteonTX2/CN10K RVU Admin Function driver. It defines PCI IDs, PF/VF encoding helpers, hardware capability models, per-block and per-function state, mailbox workqueue state, firmware-data layout, the top-level `struct rvu`, MMIO accessors, silicon capability helpers, channel helpers, and cross-file function prototypes for all AF subsystems.

## Important APIs, Types, and Functions
- PF/VF helpers include `rvu_make_pcifunc()`, `rvu_pcifunc_pf_mask()`, `rvu_get_pf()`, `is_vf()`, `is_pffunc_af()`, `is_lbk_vf()`, `is_pf_cgxmapped()`, and `is_cgx_vf()`.
- Core resource types include `struct rsrc_bmap`, `struct rvu_block`, and `struct rvu_pfvf`.
- `struct rvu_hwinfo` stores global hardware constants, channel bases, block descriptors, NIX/NPC resource containers, and capability flags in `struct hw_cap`.
- Mailbox/interrupt state is represented by `struct rvu_work`, `struct mbox_wq_info`, `struct rvu_irq_data`, and `struct mbox_ops`.
- `struct rvu_fwdata` mirrors firmware-provided platform data, including MAC addresses, clocks, MSI-X table base, PTP external clock/timestamp fields, channel data, alternate-AF notification info, and CGX LMAC firmware data.
- `struct rvu` is the top-level AF object containing BAR mappings, PCI device, hardware model, PF/VF arrays, locks, mailbox queues, FLR state, MSI-X state, CGX maps, firmware data, PTP pointer, devlink/debugfs, representor state, MCS/CPT locks, and CN20K extension pointer.
- MMIO accessors `rvu_write64()`, `rvu_read64()`, `rvupf_write64()`, `rvupf_read64()`, and `rvu_bar2_sel_write64()` centralize AF/PF BAR register access.
- Inline silicon helpers such as `is_rvu_otx2()`, `is_cn10kb()`, `is_cgx_mapped_to_nix()`, and `is_rvu_supports_nix1()` gate generation-specific behavior.
- Function prototypes expose RVU core, CGX, NPA, NIX, NPC, CPT, CN10K, MCS, switch, SDP, debugfs, and representor APIs to sibling files.

## Control Flow
The header itself contains only inline helper control flow. Runtime flow is implemented in `rvu.c` and subsystem files. Its helper functions are used throughout initialization, mailbox handling, channel calculation, PF/VF validation, block lookup, CGX permission checks, and generation-specific branching. The `MBOX_MESSAGES` macro expansion declares all mailbox handler prototypes, making mailbox dispatch in `rvu.c` compile-time synchronized with `mbox.h`.

## State and Persistence Behavior
The structures in this header describe all major in-memory state for the AF driver. Hardware ownership is mirrored in resource bitmaps, LF-to-`pcifunc` maps, PF/VF counters, MSI-X maps, NIX/NPA/NPC structures, and CGX/PF maps. Firmware data is memory-mapped platform state, not allocated by the driver. No disk persistence exists. Hardware configuration persists in CSRs until FLR, block reset, or device removal, while software mirrors are rebuilt at probe.

## Dependencies and Integration Points
The header includes Linux PCI/devlink/silicon helpers and RVU-local headers for structures, devlink, common definitions, mailbox messages, NPC, registers, and PTP. It is included by most AF implementation files and is the main integration point between independent subsystems such as NIX, NPA, NPC, CPT, CGX/RPM, MCS, SDP, switchdev-like representors, debugfs, and CN10K/CN20K support.

## Risks and Edge Cases
- `struct rvu_fwdata` must stay exactly aligned with firmware; `FWDATA_CGX_LMAC_OFFSET` and reserved fields make this fragile.
- PF/VF bit layout changes for CN20K are handled by inline helpers; callers must use helpers rather than hard-coded shifts.
- Many prototypes accept raw `u16 pcifunc` and `void *` subsystem handles, so validation has to happen at API boundaries.
- `struct rvu_pfvf` carries many subsystem-owned fields; teardown ordering must respect ownership to avoid leaks or stale hardware state.
- Channel helpers assume NIX constants are readable from NIX0 and that programmable channel bases have already been initialized.
- Header-level inline helpers read MMIO in some cases, so they are not side-effect-free predicates.

## Test Signals
- Compile coverage across OcteonTX2, CN10K, CN20K, debugfs enabled/disabled, and all mailbox handler declarations.
- Static analysis for direct PF/VF shift/mask use outside helper functions.
- Firmware ABI tests validating `struct rvu_fwdata` size, offset, magic, version, and CGX LMAC union layout.
- Unit or mock tests for channel helpers under programmable and non-programmable channel modes.
- Probe/FLR teardown tests that watch all `struct rvu_pfvf` counters and bitmaps return to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_cgx.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_cgx.c

## Purpose
`rvu_cgx.c` connects RVU AF resource management to physical CGX/RPM MAC ports. It maps CGX/RPM LMACs to RVU PFs, initializes MAC event handling, forwards link changes to PF drivers over AF-to-PF mailbox messages, exposes CGX/RPM mailbox handlers for link, stats, MAC addresses, promiscuous mode, PTP RX timestamping, pause/PFC, loopback, FEC, and link mode, and coordinates CGX start/stop reference counts across PF/VF NIX users.

## Important APIs, Types, and Functions
- `struct cgx_evq_entry` wraps queued link events for workqueue delivery.
- `is_mac_feature_supported()`, `is_cgx_config_permitted()`, `rvu_cgx_pdata()`, `rvu_first_cgx_pdata()`, `cgxlmac_to_pf()`, and mapping helpers provide lookup and permission checks.
- `rvu_map_cgx_lmac_pf()` builds `pf2cgxlmac_map` and `cgxlmac2pf_map`, allocates NPC pkinds, maps CGX links to NIX blocks, and counts CGX-mapped PFs/VFs.
- `cgx_lmac_event_handler_init()`, `cgx_lmac_postevent()`, `rvu_cgx_send_link_info()`, `cgx_evhandler_task()`, and `cgx_notify_pfs()` implement asynchronous link notifications.
- `rvu_cgx_init()`, `cgx_start_linkup()`, and `rvu_cgx_exit()` own CGX/RPM integration lifecycle.
- MAC control helpers include `rvu_cgx_config_rxtx()`, `rvu_cgx_tx_enable()`, `rvu_cgx_config_tx()`, `rvu_cgx_start_stop_io()`, `rvu_cgx_disable_dmac_entries()`, and `rvu_mac_reset()`.
- Mailbox handlers cover stats, FEC stats, MAC address set/add/del/get/reset/update/max, promiscuous enable/disable, PTP RX enable/disable, link event enable/disable, link info, features, internal loopback, pause frame config, PFC config, PHY FEC stats, FEC mode, aux firmware link info, and link mode changes.

## Control Flow
During `rvu_setup_hw_resources()`, `rvu_cgx_init()` discovers the maximum CGX ID, stores CGX private data pointers, maps active LMACs to PF IDs starting at `PF_CGXMAP_BASE`, clears X2P reset on MAC blocks, registers link event callbacks, creates an event workqueue, and initializes `cgx_cfg_lock`. After NIX initialization, `cgx_start_linkup()` enables RX for all LMACs and starts firmware link-up.

CGX/RPM link changes arrive through a callback that can run in interrupt context. The callback allocates an event entry with `GFP_ATOMIC`, pushes it to a spinlock-protected queue, and queues work. The worker sends link events to mapped PFs that enabled notifications. It serializes mailbox-up sends with `rvu->mbox_lock`, allocates an AF-to-PF message, waits for mailbox availability, sends, and waits for the PF response.

Mailbox requests from PFs enter handlers that typically validate the caller is a CGX-mapped PF, translate PF to `(cgx_id,lmac_id)`, fetch `mac_ops`, and call the MAC-specific CGX/RPM helper. PTP RX enable also configures NPC timestamp parser shifting, marks `pfvf->hw_rx_tstamp_en`, and informs MCS. CGX start/stop uses `cgx_cfg_lock` and `parent_pf->cgx_users` so the physical MAC starts when the first PF/VF NIX user starts and stops when the last user stops.

## State and Persistence Behavior
`rvu_cgx.c` fills CGX-related fields in `struct rvu`: `cgx_idmap`, `pf2cgxlmac_map`, `cgxlmac2pf_map`, `cgx_mapped_pfs`, `cgx_mapped_vfs`, notification bitmap, event queue/list/workqueue, and `cgx_cfg_lock`. Per-function state in `struct rvu_pfvf` tracks MAC address, default MAC, CGX in-use flag, user count on the parent PF, and PTP RX timestamp enablement. Hardware state persists in CGX/RPM MAC registers, DMAC filters or NPC exact-match tables, link mode/FEC configuration, pause/PFC state, loopback, PTP timestamp prepending, and Rx/Tx enable bits.

## Dependencies and Integration Points
The file depends on CGX/RPM APIs from `cgx.h` and `lmac_common.h`, MAC ops, NPC exact-match and parser configuration, NIX cumulative stats, MCS PTP configuration, RVU mailbox infrastructure, firmware CGX link data in `rvu_fwdata`, and RVU resource mappings from `rvu.h`. It is called by `rvu.c` during init/exit and by NIX/FLR paths for MAC start/stop and reset.

## Risks and Edge Cases
- Permission checks differ by handler: some reject VFs, some acknowledge unmapped functions, and MAC address set only checks PF mapping; caller expectations need coverage.
- Event delivery waits synchronously for PF mailbox responses from the event worker, so a non-responsive PF can delay later link events.
- `rvu_map_cgx_lmac_pf()` assumes PF IDs starting at 1 are available and that active LMAC count fits allocated mapping arrays.
- `rvu_cgx_exit()` loops through `cgx <= cgx_cnt_max` while `rvu_cgx_pdata()` rejects `>= cgx_cnt_max`; harmless but easy to misread.
- PTP RX enable changes both MAC and NPC parser behavior; partial failure can leave MAC timestamp prepending enabled if NPC configuration fails after the MAC write.
- Pause/PFC configuration depends on both MAC feature bits and shared verification against PF/VF flow-control ownership.
- `rvu_cgx_start_stop_io()` reference counting must remain balanced across PF/VF start/stop and FLR paths.

## Test Signals
- Probe with no CGX devices, sparse CGX IDs, multiple LMACs per CGX, RPM2 eight-LMAC layouts, and NIX1-connected links.
- Link event tests for notification disabled/enabled, current-link replay, mailbox-up timeout/failure, and queue cleanup on exit.
- Mailbox permission tests for PF, VF, LBK VF, non-CGX PF, and exact-match-enabled variants.
- PTP RX enable/disable tests covering MAC, NPC parser, `hw_rx_tstamp_en`, and MCS side effects, including injected NPC failure.
- Pause/PFC conflict tests and flow-control ownership validation across PF/VF users.
- Start/stop/FLR tests validating `cgx_users`, `cgx_in_use`, MAC reset, DMAC cleanup, and stats reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_cgx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_cn10k.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_cn10k.c

## Purpose
`rvu_cn10k.c` contains CN10K-specific RVU AF helpers for APR LMTST map-table management, programmable channel numbering, NIX/RPM/LBK channel programming, and CN10K NIX/APR block initialization. It supplements the generic RVU core with features absent or different on older OcteonTX2 silicon.

## Important APIs, Types, and Functions
- `lmtst_map_table_ops()` temporarily maps the APR LMT map table, reads or writes an entry, programs entry word1 defaults on writes, and flushes the APR interceptor cache.
- `rvu_get_lmtst_tbl_index()` maps a `pcifunc` to its two-word LMT map table entry offset.
- `rvu_get_lmtaddr()` asks RVUM/SMMU translation registers to translate a PF/VF IOVA to a physical LMTLINE address.
- `rvu_update_lmtaddr()` stores the original LMT base in `pfvf->lmt_base_addr` and writes a replacement.
- `rvu_mbox_handler_lmtst_tbl_setup()` handles local LMT memory, shared-primary LMT region setup, scheduled LMTST enable, line-prefetch disable, and ordered early-completion disable.
- `rvu_reset_lmt_map_tbl()` restores saved LMT base and word1 values during FLR.
- `rvu_set_channels_base()` computes channel bases and marks `hw->cap.programmable_chans`.
- `rvu_program_channels()` applies programmable channel configuration to NIX, LBK, and RPM blocks.
- `rvu_nix_block_cn10k_init()` sets NIX vWQE timer and RX/global clock bits.
- `rvu_apr_block_cn10k_init()` raises APR LMTST throttling.

## Control Flow
Generic RVU setup calls `rvu_apr_block_cn10k_init()` before resource discovery on non-OcteonTX2 devices. Later, `rvu_set_channels_base()` reads NIX constants, fills CGX/LBK/SDP/CPT link counts and default channel bases, and, when programmable channels are supported, computes compact contiguous channel windows ordered LBK, SDP, CGX, CPT. After NIX/SDP setup, `rvu_program_channels()` writes the computed windows into each NIX link config, each LBK P2X/X2P config, and each RPM LMAC link config.

At runtime, PF/VF drivers can send `lmtst_tbl_setup`. The handler optionally translates a local LMT IOVA into a physical address, updates the caller's LMT map entry, mirrors a base pcifunc's LMT address for shared mode, and updates word1 flags for scheduled LMTST behaviors. Original values are saved only once in `struct rvu_pfvf` so `rvu_reset_lmt_map_tbl()` can restore them on FLR. LMT table writes flush APR LMT cache immediately.

## State and Persistence Behavior
The file updates `struct rvu_hwinfo` channel fields (`cgx`, `lmac_per_cgx`, link counts, channel bases, programmable channel capability) and per-function LMT defaults (`lmt_base_addr`, `lmt_map_ent_w1`). Hardware state persists in APR LMT map table memory, APR LMT configuration/control CSRs, RVUM SMMU translation registers, NIX link channel registers, LBK link channel registers, RPM LMAC channel registers, and NIX AF config/timer registers. Saved LMT defaults are runtime-only and are cleared after FLR restoration.

## Dependencies and Integration Points
The file depends on RVU core MMIO helpers, CGX/RPM LMAC read/write helpers, APR/RVU/NIX/LBK/RPM register definitions, Linux PCI device iteration for LBK programming, and `rvu->rsrc_lock` for SMMU translation serialization. It integrates with `rvu.c` setup, mailbox dispatch through `rvu_mbox_handler_lmtst_tbl_setup()`, FLR cleanup via `rvu_reset_lmt_map_tbl()`, and NIX initialization through `rvu_nix_block_cn10k_init()`.

## Risks and Edge Cases
- `lmtst_map_table_ops()` maps and unmaps the entire LMT table on every operation; failures or high-frequency calls can be expensive.
- `rvu_get_lmtaddr()` serializes translation with `rsrc_lock`, but callers must ensure the IOVA remains valid during translation and subsequent use.
- Saved LMT defaults use zero as "not saved"; if a legitimate original value is zero, restoration of that field is skipped.
- Channel base computation must fit CPT into channels 2048-4095; otherwise initialization fails.
- `rvu_lbk_set_channels()` iterates PCI LBK devices and has a late `pci_dev_put()` only on the error path; PCI reference handling deserves scrutiny.
- RPM channel programming assumes 16 channels per LMAC because no read-only constant exists.
- LMT map word1 writes OR new bits into existing values, so clearing previously enabled options requires FLR/reset rather than a second setup call.

## Test Signals
- CN10K probe tests with programmable channels disabled and enabled, including NIX1, multiple LBK devices, RPM/RPM2 LMAC counts, and CPT channel windows.
- LMTST mailbox tests for local region translation, shared base pcifunc, scheduled LMTST flags, word1 updates, invalid/null IOVA, and translation errors.
- FLR tests confirming LMT base and word1 restoration and clearing of saved defaults.
- MMIO mock tests verifying APR cache flush sequence after LMT writes.
- Channel programming tests validating NIX/LBK/RPM base/range fields and no overlap between LBK, SDP, CGX, and CPT windows.
- Regression coverage for `rvu_nix_block_cn10k_init()` and `rvu_apr_block_cn10k_init()` register bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_cn10k.c -->
