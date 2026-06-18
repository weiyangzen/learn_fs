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
