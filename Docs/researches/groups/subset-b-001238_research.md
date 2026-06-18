# subset-b-001238 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_hw_types.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_hw_types.h

## Purpose
This header is the hardware contract for the Marvell OcteonTX2/CN10K CPT crypto accelerator driver. It defines PCI IDs, MSI-X vector counts, mailbox interrupt offsets, CPT PF/LF/RVU register offsets, hardware completion codes, and packed register/instruction/result layouts used by both PF and VF code.

## Important APIs, types, and constants
Key constants include `OTX2_CPT_PCI_PF_DEVICE_ID`, `OTX2_CPT_PCI_VF_DEVICE_ID`, `CN10K_CPT_PCI_*`, `OTX2_CPT_MAX_ENGINE_GROUPS`, `OTX2_CPT_INST_SIZE`, `OTX2_CPT_LF_MSIX_VECTORS`, and register macros such as `OTX2_CPT_LF_Q_BASE`, `OTX2_CPT_LF_NQX()`, `OTX2_CPT_PF_VFX_MBOXX()`, and `OTX2_CPT_LMT_LF_LMTLINEX()`. `enum otx2_cpt_comp_e` maps hardware completion states, while `enum otx2_cpt_ucode_comp_code_e` maps selected microcode errors. Core ABI types are `union otx2_cpt_inst_s`, `union otx2_cpt_res_s`, `union otx2_cptx_lf_ctl`, `union otx2_cptx_lf_done_wait`, `union otx2_cptx_lf_inprog`, `union otx2_cptx_lf_q_base`, `union otx2_cptx_lf_q_size`, and `union otx2_cptx_af_lf_ctrl`.

## Control flow and integration
This file has no executable control flow, but it controls how executable code writes registers and interprets hardware memory. `otx2_cptlf.h` uses LF queue register unions to enable queues, set queue base/size, and fill CPT instructions. `otx2_cptvf_reqmgr.c` polls `otx2_cpt_res_s` completion codes. PF microcode code uses AF register offsets from common RVU headers plus the completion/result definitions here. PF and VF probe tables use the device IDs.

## State and persistence
State represented here lives either in MMIO registers or DMA-visible command/result memory. Queue enablement, done counts, in-flight counts, engine group masks, and instruction/result buffers are transient hardware state; there is no disk persistence. Bitfield layout and endian assumptions are persistent ABI requirements across the driver and firmware.

## Dependencies and integration points
The header depends only on Linux integer types but is consumed by PF, VF, LF, mailbox, request manager, and algorithm paths. It also implicitly depends on RVU mailbox definitions and Marvell register addressing conventions used in `rvu_reg.h` and `otx2_cpt_common.h`.

## Risks and edge cases
The largest risk is ABI drift: bitfield ordering, register offsets, alignment, or completion-code interpretation changes would break DMA commands or MMIO programming. `union otx2_cpt_res_s` differs between CN9K and CN10K layouts, so hardware-operation callbacks must choose the correct completion-code accessor. Queue control comments require quiescent writes; callers must respect these ordering rules.

## Test signals
Useful signals include successful PF/VF probe on OTX2 and CN10K devices, LF queue enable/disable without hardware warnings, completion-code decoding for success/fault/hardware/instruction errors, mailbox interrupt delivery, and crypto self-tests covering both CN9K and CN10K result layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_hw_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_mbox_common.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_mbox_common.c

## Purpose
This file provides shared CPT mailbox helpers used by PF and VF paths to communicate with RVU AF/PF firmware. It wraps mailbox allocation, send/wait behavior, AF register read/write requests, LF resource attach/detach, MSI-X offset queries, LF reset, and CN10K LMTST table setup.

## Important APIs and functions
Exported helpers include `otx2_cpt_send_mbox_msg()`, `otx2_cpt_send_ready_msg()`, `otx2_cpt_send_af_reg_requests()`, `otx2_cpt_add_write_af_reg()`, `otx2_cpt_read_af_reg()`, `otx2_cpt_write_af_reg()`, `otx2_cpt_detach_rsrcs_msg()`, `otx2_cpt_msix_offset_msg()`, `otx2_cpt_sync_mbox_msg()`, `otx2_cpt_lf_reset_msg()`, and `otx2_cpt_lmtst_tbl_setup_msg()`. `otx2_cpt_add_read_af_reg()` is file-local and queues a read request for later send.

## Control flow
Each helper allocates a typed mailbox request with `otx2_mbox_alloc_msg_rsp()`, fills the message ID/signature/pcifunc fields, populates request-specific payload, and sends through `otx2_cpt_send_mbox_msg()`. Register reads and writes use `MBOX_MSG_CPT_RD_WR_REGISTER`; batched writes can be queued with `otx2_cpt_add_write_af_reg()` and flushed by `otx2_cpt_send_af_reg_requests()`. Attach/detach calls validate asynchronous response side effects by checking `lfs->are_lfs_attached`, which mailbox response handlers update.

## State and persistence
The helpers mutate mailbox buffers and fields in `struct otx2_cptlfs_info`, especially `are_lfs_attached`, LF MSI-X offsets, and LMT metadata. Register read results are written through response-owned `ret_val` pointers. No persistent storage is used; all state is device, mailbox, or DMA/MMIO state.

## Dependencies and integration points
This file depends on the common RVU mailbox API from `mbox.h`, CPT LF structures from `otx2_cptlf.h`, and response handlers in `otx2_cptpf_mbox.c` and `otx2_cptvf_mbox.c` to complete state updates. PF/VF probe and LF init paths call these helpers before enabling queues or registering interrupts.

## Risks and edge cases
Allocation failure consistently returns `-EFAULT`, while mailbox timeout returns `-EIO` and other errors collapse to `-EFAULT`. Attach/detach correctness depends on response handlers updating `are_lfs_attached`; if responses are dropped or processed by the wrong LF block, callers see `-EINVAL`. `otx2_cpt_detach_rsrcs_msg()` hard-codes `cptlfs = 1`, which is intentional for current cleanup but worth checking if multi-LF detach semantics change.

## Test signals
Probe logs should show ready-message success, valid MSI-X offsets for every LF, successful attach/detach transitions, AF register reads returning expected constants, and no timeout path from `otx2_mbox_wait_for_rsp()`. Fault injection on mailbox allocation and timeout paths should unwind PF/VF probe cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_mbox_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_reqmgr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_reqmgr.h

## Purpose
This header defines the CPT request-manager data model and inline DMA/scatter-gather setup helpers used by the VF crypto data path. It translates Crypto API request buffers into CPT instruction inputs, output scatter lists, completion memory, and per-request lifetime records.

## Important APIs and types
Core types are `struct otx2_cpt_req_info`, `struct otx2_cpt_inst_info`, `struct otx2_cpt_pending_entry`, `struct otx2_cpt_pending_queue`, `struct otx2_cpt_buf_ptr`, `struct otx2_cpt_iq_command`, and SG component formats `struct otx2_cpt_sglist_component` and `struct cn10kb_cpt_sglist_component`. Important helpers are `otx2_cpt_info_destroy()`, `setup_sgio_components()`, `sgv2io_components_setup()`, `cn10k_sgv2_info_create()`, and `otx2_sg_info_create()`. External functions declared here are `otx2_cpt_do_request()`, `otx2_cpt_post_process()`, and `otx2_cpt_get_eng_grp_num()`.

## Control flow
Algorithm code fills `otx2_cpt_req_info` with input/output buffers, context pointer, opcode, callback, and engine group. The selected hardware op calls either `otx2_sg_info_create()` or `cn10k_sgv2_info_create()` to allocate one aligned memory block containing `otx2_cpt_inst_info`, gather/scatter lists, and completion result space. Each SG setup maps caller buffers with `dma_map_single()`, writes hardware SG descriptors, maps descriptor memory, and records DMA addresses used by `otx2_cptvf_reqmgr.c` when building the CPT instruction.

## State and persistence
Per-request state persists until completion callback cleanup. `otx2_cpt_inst_info` owns DMA mappings for SG descriptors and points back to the original request. Individual `otx2_cpt_buf_ptr.dma_addr` fields are set during mapping and cleared only on partial setup failures; normal completion unmaps them in `otx2_cpt_info_destroy()`. No disk persistence exists.

## Dependencies and integration points
The header depends on `otx2_cpt_common.h`, hardware result layout from `otx2_cpt_hw_types.h`, and Linux DMA APIs. VF algorithms create requests, VF request manager submits and completes them, and LF hardware ops choose CN9K or CN10K SG formats.

## Risks and edge cases
Alignment math is security- and correctness-critical: DPTR/RPTR need 8-byte alignment and completion results need 32-byte alignment. SG v1 supports up to 50 input and 50 output buffers; v2 does not enforce the same explicit count in the helper, so callers must remain bounded by request arrays. DMA mapping failures must unwind all prior mappings. Zero or NULL virtual pointers are skipped, but descriptor counts still come from `buf_count`, so malformed sparse lists can create descriptors with zero addresses.

## Test signals
Signals include successful encryption/decryption over fragmented scatterlists, DMA API debug runs with no unbalanced mappings, CN10K SGv2 capability path coverage, allocation-failure injection through both SG builders, and completion cleanup that frees mappings under normal, hardware-error, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_reqmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptlf.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptlf.c

## Purpose
This file implements common CPT Local Function lifecycle and interrupt handling for both PF inline-IPsec use and VF kernel-crypto use. It initializes LF hardware queues, attaches resources through mailbox, programs engine-group masks and priority, registers MSI-X handlers, manages IRQ affinity, and tears LF state down.

## Important APIs and functions
Exported APIs include `otx2_cptlf_init()`, `otx2_cptlf_shutdown()`, `otx2_cptlf_register_misc_interrupts()`, `otx2_cptlf_register_done_interrupts()`, `otx2_cptlf_unregister_misc_interrupts()`, `otx2_cptlf_unregister_done_interrupts()`, `otx2_cptlf_set_irqs_affinity()`, and `otx2_cptlf_free_irqs_affinity()`. Local helpers configure done interrupt coalescing, AF LF priority and group mask, context input length, hardware queue init/cleanup, and interrupt enable bits.

## Control flow
`otx2_cptlf_init()` validates device/register pointers, initializes LF slots and MMIO/LMT addresses, attaches resources, allocates instruction queues, disables/configures/enables hardware queues, then sets priority and engine group masks. Optional context input length override is written through AF registers. Interrupt registration installs one misc and one done handler per LF; misc interrupts log and acknowledge hardware error bits, while done interrupts acknowledge completion counts and schedule the LF tasklet. Shutdown disables queues, frees queues, detaches resources, and clears `lfs_num`.

## State and persistence
LF state lives in `struct otx2_cptlfs_info` and its `lf[]` array: queue DMA memory, MSI-X offsets, registered IRQ flags, affinity masks, LMT line pointers, slot numbers, and optional tasklet pointers. Hardware queue state is MMIO state. There is no persistent storage.

## Dependencies and integration points
This file uses shared mailbox helpers for AF register reads/writes and resource attach/detach/reset. `otx2_cptlf.h` supplies inline queue operations. VF main owns tasklet and pending-queue allocation before registering done interrupts. PF mailbox code uses LF init for inline IPsec LFs.

## Risks and edge cases
Queue setup depends on mailbox response state and valid MSI-X offsets. Error unwinds must disable queues, free DMA memory, and detach resources in order. Misc interrupt handling uses an `else if` chain, so simultaneous bits are acknowledged one at a time. Done interrupts require `lf->wqe`; PF inline LFs register only misc interrupts, while VF LFs must create tasklet work before enabling done interrupts.

## Test signals
Expected signals are clean LF init/shutdown under PF and VF probes, correct IRQ registration/unregistration after partial failure, no pending/inflight timeout warnings during disable, tasklet scheduling on completed VF crypto requests, and affinity masks distributed across online CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptlf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptlf.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptlf.h

## Purpose
This header defines CPT LF queue sizing, LF state structures, hardware operation callbacks, instruction-queue allocation/configuration helpers, queue enable/disable helpers, and command-send primitives. It is the bridge between hardware register definitions and PF/VF LF lifecycle code.

## Important APIs and types
Important constants include `OTX2_CPT_USER_REQUESTED_QLEN_MSGS`, `OTX2_CPT_INST_QLEN_MSGS`, `OTX2_CPT_INST_QLEN_BYTES`, `OTX2_CPT_INST_GRP_QLEN_BYTES`, `OTX2_CPT_ALL_ENG_GRPS_MASK`, and `OTX2_CPT_MAX_LFS_NUM`. Key types are `struct otx2_cpt_inst_queue`, `struct otx2_cptlf_wqe`, `struct otx2_cptlf_info`, `struct cpt_hw_ops`, `struct otx2_lmt_info`, and `struct otx2_cptlfs_info`. Important inline APIs include `otx2_cpt_alloc_instruction_queues()`, `otx2_cpt_free_instruction_queues()`, `otx2_cptlf_disable_iqueues()`, `otx2_cptlf_enable_iqueues()`, `otx2_cpt_fill_inst()`, `otx2_cpt_send_cmd()`, and `otx2_cptlf_set_dev_info()`.

## Control flow
LF setup allocates coherent instruction queue memory with space for group queue and flow-control metadata, aligns queue base, writes `Q_BASE` and `Q_SIZE`, and enables execution/enqueue bits. Disable clears enqueue, marks execution disabled, waits for pending queue pointers and in-flight counters to drain, delays for queue write flushing, and requests LF reset through mailbox. `otx2_cpt_fill_inst()` maps software IQ command words into the 64-byte hardware instruction. `otx2_cpt_send_cmd()` writes instructions to the LMT line, uses `dma_wmb()`, and retries `otx2_lmt_flush()` until the store succeeds.

## State and persistence
`otx2_cptlfs_info` is the main shared LF state object, containing device pointers, mailbox, hardware ops, LF array, engine-group numbers, state atomics, block address, global slot, and context-length override. Queue memory is DMA coherent and transient. State is not persisted across driver removal.

## Dependencies and integration points
The header depends on Marvell LMT assembly helpers, RVU mailbox types, hardware-type unions, and request-manager declarations. PF/VF main files initialize `otx2_cptlfs_info`; request manager uses `ops->send_cmd()` and completion-code callbacks; CN10K support can override LMT and SG behavior.

## Risks and edge cases
Queue-size arithmetic includes a documented 320-entry workaround for LDWB behavior; changing it can expose hardware errata. Disable loops can timeout but continue after warnings, so higher layers must tolerate residual hardware conditions. `otx2_cpt_send_cmd()` spins until LMTST success, which assumes hardware eventually accepts the store. Correct memory barriers are essential before MMIO submission.

## Test signals
Signals include queue memory alignment checks, successful queue drain on reset/remove, LMTST submission under load, CN10KB context-flush programming, no DMA API complaints for coherent queues, and crypto throughput scaling with one LF per CPU up to configured limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptlf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf.h

## Purpose
This PF header defines the Physical Function driver state, VF bookkeeping, FLR work records, mailbox work entry points, and inline CPT LF setup/cleanup prototypes. It is the shared state contract between PF probe, PF mailbox handling, SR-IOV support, devlink, microcode management, and inline IPsec setup.

## Important APIs and types
`struct otx2_cptvf_info` tracks each enabled VF, including PF backpointer, mailbox work item, VF PCI device pointer, VF id, and interrupt index. `struct cptpf_flr_work` wraps per-VF FLR handling. `struct otx2_cptpf_dev` holds PF BAR mappings, AF/PF and VF/PF mailbox objects, workqueues, VF table, engine groups, LF state for CPT0 and CPT1, hardware capability cache, PF id, VF counts, sysfs-tunable limits, CPT1 presence, devlink handle, and serialization mutex. Prototypes expose AF/PF and VF/PF mailbox handlers plus `otx2_inline_cptlf_setup()` and `otx2_inline_cptlf_cleanup()`.

## Control flow
The header itself has no executable flow. `otx2_cptpf_main.c` allocates and populates `otx2_cptpf_dev` during probe, then SR-IOV enable fills the VF table and FLR work. `otx2_cptpf_mbox.c` consumes the same state to process AF responses, VF requests, and inline IPsec LF configuration.

## State and persistence
All fields are runtime kernel/device state. Engine groups and capability caches persist only while the PF driver is loaded. VF state exists only while SR-IOV is enabled. Sysfs attributes mutate fields such as `kvf_limits` and `sso_pf_func_ovrd`, but no file-backed persistence is implemented.

## Dependencies and integration points
The header depends on common CPT definitions, microcode engine-group types, and LF structures. It integrates PF core code with devlink, mailbox code, LF code, VF request forwarding, and CN10K LMTST support.

## Risks and edge cases
`otx2_cptpf_dev` centralizes many ownership domains, so cleanup order matters: VFs, inline LFs, devlink, sysfs, engine groups, interrupts, mailboxes, and LMT memory must be torn down in dependency order. The mutex serializes AF mailbox access and protects paths that forward VF requests; callers must avoid unprotected mailbox reuse.

## Test signals
PF probe/remove, SR-IOV enable/disable, VF FLR, VF mailbox forwarding, inline IPsec LF setup on CPT0/CPT1, devlink custom engine group operations, and sysfs `kvf_limits` updates are the main integration signals for this state definition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_main.c

## Purpose
This is the PCI PF driver entry point for Marvell RVU CPT hardware. It probes PF devices, maps registers, initializes AF/PF mailbox, discovers engine resources, initializes LMTST support, creates sysfs/devlink surfaces, manages SR-IOV VF enablement, and handles VF mailbox/FLR/ME interrupt setup.

## Important APIs and functions
Driver entry points are `otx2_cptpf_probe()`, `otx2_cptpf_remove()`, and `otx2_cptpf_sriov_configure()`. SR-IOV helpers are `cptpf_sriov_enable()` and `cptpf_sriov_disable()`. Mailbox setup helpers include `cptpf_afpf_mbox_init()`, `cptpf_register_afpf_mbox_intr()`, `cptpf_vfpf_mbox_init()`, and `cptpf_register_vfpf_intr()`. FLR and ME paths use `cptpf_vf_flr_intr()`, `cptpf_flr_wq_handler()`, and `cptpf_vf_me_intr()`. Sysfs attributes are `kvf_limits` and `sso_pf_func_ovrd`.

## Control flow
Probe allocates `otx2_cptpf_dev`, enables PCI and DMA, requests BARs, maps PF registers, verifies AF readiness, allocates MSI-X vectors, sets hardware capability flags, initializes AF mailbox, sends ready, reads PF resources, initializes LMTST and engine group structures, creates sysfs group, and registers devlink. SR-IOV enable initializes VF/PF mailbox memory and workqueues, initializes FLR work, registers VF mailbox/FLR/ME interrupts, discovers engine capabilities, creates default engine groups, then calls `pci_enable_sriov()`. Disable reverses those resources and drops the module reference.

## State and persistence
PF state is all in memory: mailbox objects, workqueues, VF table, engine groups, LFs, capabilities, sysfs values, and devlink registration. `kvf_limits` and `sso_pf_func_ovrd` can be changed via sysfs while loaded but are not persisted across reload. Engine group creation persists for the lifetime of the PF and enabled VFs.

## Dependencies and integration points
This file depends on PCI core, RVU registers, mailbox helpers, microcode manager, LF common code, devlink support, and CN10K LMTST helpers. It provides the PF service layer that VFs depend on for capability discovery and engine-group selection.

## Risks and edge cases
Probe defers if AF is not initialized or ready-message times out. Error unwinds must destroy mailboxes/workqueues and remove sysfs/devlink in exact reverse order. SR-IOV enable does engine discovery and microcode setup before `pci_enable_sriov()`; failures must not leave interrupts enabled. FLR handling relies on per-VF ordered work and re-enables interrupts only after AF confirms reset. `kvf_limits` is bounded by online CPUs but can affect later VF LF count.

## Test signals
Signals include successful PF bind/unbind, probe defer when AF is unavailable, SR-IOV enable/disable with different VF counts including over 64, VF FLR recovery, sysfs validation, devlink registration, microcode group creation, and no leaked IRQ/workqueue resources under failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_mbox.c

## Purpose
This file implements PF-side mailbox routing. It handles VF requests locally or forwards them to AF, processes AF responses for PF and VFs, supports PF-up messages for CPT instruction LMTST, and configures inline IPsec LFs requested by other RVU components.

## Important APIs and functions
Public handlers are `otx2_cptpf_vfpf_mbox_intr()`, `otx2_cptpf_vfpf_mbox_handler()`, `otx2_cptpf_afpf_mbox_intr()`, `otx2_cptpf_afpf_mbox_handler()`, and `otx2_cptpf_afpf_mbox_up_handler()`. Inline LF APIs exported through the PF header are `otx2_inline_cptlf_setup()` and `otx2_inline_cptlf_cleanup()`. Local handlers include `handle_msg_get_caps()`, `handle_msg_get_eng_grp_num()`, `handle_msg_kvf_limits()`, `handle_msg_rx_inline_ipsec_lf_cfg()`, `rx_inline_ipsec_lf_cfg()`, and `forward_to_af()`/`forward_to_vf()`.

## Control flow
VF mailbox interrupts identify the VF bit, queue its work item, clear the interrupt, then workqueue code reads all VF messages. Known PF-serviced messages return capabilities, engine group numbers, kernel VF LF limits, or inline IPsec LF configuration. Unknown valid VF messages are copied into the AF mailbox under `cptpf->lock`. AF response handling validates signatures, routes messages with VF pcifuncs back to VF mailbox memory, and processes PF responses locally to update PF id, LF MSI-X offsets, register read results, and attach/detach flags. AF-up `CPT_INST_LMTST` messages submit one instruction through the inline LF if configured.

## State and persistence
This file mutates `cptpf->pf_id`, LF MSI-X offsets, LF attach flags, inline LF state for CPT0/CPT1, VF mailbox response buffers, and capability responses. Inline LF setup attaches one high-priority LF per block and configures NIX/CPT inline IPsec via AF mailbox. No persistent storage is used.

## Dependencies and integration points
It depends on PF state from `otx2_cptpf.h`, mailbox helpers, LF lifecycle, engine-group lookup, RVU pcifunc helpers, and NIX/CPT mailbox message definitions. It is the integration point between VF driver requests and AF resource control.

## Risks and edge cases
Message size copying must preserve mailbox headers correctly; malformed signatures are rejected. `forward_to_af()` treats only `-EIO` as AF communication failure and forwards other AF result codes later. Inline IPsec setup must unwind CPT1 and CPT0 LFs if NIX/CPT configuration fails. AF response routing ignores `MBOX_MSG_VF_FLR` to VFs. The VF interrupt loop iterates two banks and must not schedule beyond `enabled_vfs`.

## Test signals
Test signals include VF capability and engine group mailbox exchanges, AF register read/write responses updating caller storage, invalid signature rejection, inline IPsec LF config and cleanup, AF-up LMTST command handling, VF counts above 64, and mailbox timeout/failure injection with no stuck mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_ucode.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_ucode.c

## Purpose
This file manages CPT microcode firmware and engine-group allocation for the PF. It loads firmware, validates revision/type, copies microcode to DMA memory, reserves engine cores, supports mirrored groups, enables/disables cores, discovers hardware capabilities through LOAD_FVC, and implements devlink custom engine-group create/delete operations.

## Important APIs and functions
Public APIs include `otx2_cpt_init_eng_grps()`, `otx2_cpt_cleanup_eng_grps()`, `otx2_cpt_create_eng_grps()`, `otx2_cpt_disable_all_cores()`, `otx2_cpt_get_eng_grp()`, `otx2_cpt_discover_eng_capabilities()`, `otx2_cpt_dl_custom_egrp_create()`, `otx2_cpt_dl_custom_egrp_delete()`, and `find_engines_by_type()`. Internal areas cover firmware load (`load_fw()`, `cpt_ucode_load_fw()`), engine reservation (`reserve_engines()`, `eng_grp_update_masks()`), group lifecycle (`create_engine_group()`, `delete_engine_group()`), mirroring, and core attach/disable paths.

## Control flow
Default group creation loads AE/SE/IE firmware matching `rid`, creates an SE group for symmetric crypto, an SE+IE group for IPsec, and an AE group for asymmetric crypto, then applies CN10K errata and context prefetch/RNM settings. Group creation copies firmware into coherent DMA memory, optionally mirrors an existing group with matching microcode, reserves engine counts, builds bitmaps, writes UCODE_BASE for unused engines, attaches cores to group masks, and enables cores. Deletion disables cores, unloads microcode, clears UCODE_BASE, releases engine counts, and removes mirror references.

## State and persistence
Engine state is held in `struct otx2_cpt_eng_grps`: availability counters, per-group engine reservations, bitmaps, microcode metadata, mirror references, and engine refcounts. Firmware images are requested from `/lib/firmware` through the kernel firmware API and copied into DMA memory for the hardware; no driver-managed disk persistence exists.

## Dependencies and integration points
The file depends on firmware loading, DMA coherent allocation, AF register mailbox helpers, LF init/request submission for capability discovery, RVU registers, and PF device state. VF capability responses and engine group number queries depend on state created here.

## Risks and edge cases
Firmware validation is strict on revision-prefixed version strings and microcode type. Engine refcounts and bitmaps must stay consistent across mirrored groups and dual CPT0/CPT1 programming. Capability discovery temporarily creates groups and an LF, sends LOAD_FVC commands, polls completion, and then deletes groups; failure must clean every resource. Devlink custom group changes are denied while VFs are enabled, reducing live reconfiguration risk.

## Test signals
Signals include firmware load success/failure by missing or mismatched files, default group layout, devlink create/delete parsing and rejection cases, VF capability discovery values, dual-block CPT1 programming, RNM/errata register writes on CN10K, and cleanup with no DMA or bitmap leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_ucode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_ucode.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_ucode.h

## Purpose
This header defines the firmware, engine, engine-group, bitmap, and mirroring data structures used by the CPT PF microcode manager. It also publishes the PF APIs used by probe, mailbox handlers, devlink, and VF capability services.

## Important APIs and types
Important constants include `OTX2_CPT_MAX_ETYPES_PER_GRP`, `OTX2_CPT_UCODE_SIGN_LEN`, `OTX2_CPT_UCODE_VER_STR_SZ`, `OTX2_CPT_MAX_ENGINES`, and `OTX2_CPT_UCODE_SZ`. Key types are `enum otx2_cpt_ucode_type`, `struct otx2_cpt_bitmap`, `struct otx2_cpt_engines`, `struct otx2_cpt_ucode_hdr`, `struct otx2_cpt_ucode`, `struct otx2_cpt_uc_info_t`, `struct otx2_cpt_engs_available`, `struct otx2_cpt_engs_rsvd`, `struct otx2_cpt_mirror_info`, `struct otx2_cpt_eng_grp_info`, and `struct otx2_cpt_eng_grps`. Public functions include group init/cleanup/create, all-core disable, group lookup, capability discovery, devlink custom create/delete, and engine lookup by type.

## Control flow
There is no executable code, but the structures encode the microcode lifecycle: firmware header parsing feeds `otx2_cpt_ucode`, groups own up to two engine-type reservations and up to two microcodes, groups can mirror another group to reuse microcode, and `otx2_cpt_eng_grps` tracks global availability and reference counts.

## State and persistence
The header models runtime state only. Firmware metadata includes filenames, version strings, DMA addresses, virtual addresses, sizes, and types. Engine reservations persist while the PF is loaded and groups are enabled. Firmware files are external dependencies, not persisted or modified by the driver.

## Dependencies and integration points
It depends on Linux PCI/module/types, hardware type constants, and common CPT definitions. PF main initializes these structures, PF mailbox answers VF group/capability requests from them, and devlink callbacks create/delete groups through the exposed APIs.

## Risks and edge cases
The maximum engine count and bitmap sizing must match hardware limits. `OTX2_CPT_MAX_ETYPES_PER_GRP` allows only two engine types, matching current SE+IE support; adding other combinations requires structural review. Mirroring refcounts must prevent deletion of groups still referenced by other groups.

## Test signals
Compile-time coverage should catch structure/API drift. Runtime signals include successful initialization for discovered engine counts, default group creation, custom devlink group parsing, group deletion with mirror refcount protection, and valid responses to VF engine-group queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_ucode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf.h

## Purpose
This VF header defines the Virtual Function device state and mailbox-facing APIs. It is the shared contract between VF probe/remove, PF/VF mailbox handling, LF setup, request submission, and Crypto API algorithm registration.

## Important APIs and types
`struct otx2_cptvf_dev` holds VF BAR mappings, PF/VF mailbox mapping, PCI device, attached LF state, VF id, mailbox workqueue/work item, selected CPT block address, bounce buffer, hardware capability flags, and engine capability words. Prototypes include `otx2_cptvf_pfvf_mbox_intr()`, `otx2_cptvf_pfvf_mbox_handler()`, `otx2_cptvf_send_eng_grp_num_msg()`, `otx2_cptvf_send_kvf_limits_msg()`, `otx2_cpt_mbox_bbuf_init()`, and `otx2_cptvf_send_caps_msg()`.

## Control flow
The header has no executable flow. VF main allocates and populates `otx2_cptvf_dev`, initializes mailbox and LFs, and later algorithm/request code retrieves it from `pci_get_drvdata()`. Mailbox code fills VF id, LF attach state, MSI-X offsets, kernel VF limits, and engine capabilities.

## State and persistence
All state is runtime-only and tied to the VF PCI device. The mailbox bounce buffer is device-managed memory. Engine capabilities and VF id are populated from PF responses during probe and are lost on remove.

## Dependencies and integration points
The header depends on RVU mailbox definitions and CPT LF structures. It integrates VF PCI probe with PF mailbox service, LF common setup, request manager, and crypto algorithms.

## Risks and edge cases
Because mailbox responses mutate fields consumed immediately by probe, ready/capability/order failures can leave incomplete state. `bbuf_base` changes the mailbox device base to a bounce buffer, so synchronization from hardware mailbox memory is required before response processing.

## Test signals
Signals include VF probe/remove, ready message setting a valid `vf_id`, capability response filling `eng_caps`, KVF limit response selecting LF count, valid MSI-X offsets, and mailbox bounce-buffer synchronization on both OTX2 and CN10K mailbox layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_algs.c

## Purpose
This file registers and implements the VF-facing Linux Crypto API algorithms backed by CPT hardware. It supports skcipher modes for AES/DES3, AEAD authenc HMAC+CBC AES, HMAC with null cipher, and RFC4106 GCM AES, with fallback software algorithms for unsupported sizes or conditions.

## Important APIs and functions
Public lifecycle functions are `otx2_cpt_crypto_init()` and `otx2_cpt_crypto_exit()`. Request paths include `otx2_cpt_skcipher_encrypt()`, `otx2_cpt_skcipher_decrypt()`, `otx2_cpt_aead_encrypt()`, `otx2_cpt_aead_decrypt()`, null-cipher AEAD variants, setkey functions, and init/exit callbacks. Important internal helpers build input/output lists (`create_input_list()`, `create_output_list()`, `create_aead_input_list()`, `create_aead_output_list()`), initialize HMAC pads (`aead_hmac_init()`), handle callbacks, and choose the device/LF with `get_se_device()`.

## Control flow
VF LF init calls `otx2_cpt_crypto_init()`, which records the PCI device and queue count, then registers skcipher and AEAD algorithms once the expected device count is present. Crypto requests allocate per-request context, validate length/alignment, build CPT context headers and scatter-gather lists, choose a queue based on CPU, set callback/request metadata, select the SE engine group, and call `otx2_cpt_do_request()`. Completion callbacks copy IVs or validate null-cipher HMACs, destroy CPT DMA state, and complete the Crypto API request.

## State and persistence
Global state is `se_devices`, protected by a mutex and atomic count, plus `is_crypto_registered`. Per-transform state stores keys, cipher/mac type, fallback tfm, hash state, HMAC pads, and CN10K hardware context. Per-request state is in DMA-aware request context and is transient until completion.

## Dependencies and integration points
This file depends on Linux Crypto API internals, scatterwalk helpers, request manager, LF engine-group lookup, CN10K errata context helpers, and PF-provided VF capabilities. It is the main consumer of CPT request submission.

## Risks and edge cases
Scatterlist handling uses `sg_virt()`, so callers must provide CPU-addressable SG entries. Large requests or zero authentication parameters fall back to software. CBC/DES alignment is enforced; XTS uses key layout with second key at `KEY2_OFFSET`. Null-cipher HMAC decrypt manually compares calculated/received tags. Error paths in init must release shash, pads, fallback tfms, and hardware contexts; current early returns after `get_se_device()` or hardware context init rely on transform cleanup for partially allocated members.

## Test signals
Crypto selftests should cover every registered driver name, setkey validation, fallback for large requests, fragmented SG input/output, in-place CBC decrypt IV copyback, null-cipher HMAC tag mismatch returning `-EBADMSG`, RFC4106 authsize validation, module refcount registration/unregistration, and CN10K errata hardware context setup/clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_algs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_algs.h

## Purpose
This header defines algorithm-level constants, operation enums, context layouts, and Crypto API lifecycle prototypes for the CPT VF algorithm implementation.

## Important APIs and types
Constants define maximum key sizes and request types. Enums cover request type, major opcodes, cipher types, MAC types, and AES key lengths. Hardware context/control types include `union otx2_cpt_encr_ctrl`, `struct otx2_cpt_fc_enc_ctx`, `union otx2_cpt_fc_hmac_ctx`, `struct otx2_cpt_fc_ctx`, and `union otx2_cpt_offset_ctrl`. Crypto transform contexts are `struct otx2_cpt_enc_ctx`, `struct otx2_cpt_req_ctx`, `struct otx2_cpt_sdesc`, and `struct otx2_cpt_aead_ctx`. Public functions are `otx2_cpt_crypto_init()` and `otx2_cpt_crypto_exit()`.

## Control flow
There is no executable control flow. The structures are filled by `otx2_cptvf_algs.c` during setkey and request construction, then passed through `otx2_cpt_reqmgr.h` and `otx2_cptvf_reqmgr.c` into CPT instructions.

## State and persistence
Transform contexts persist for the life of a Crypto API tfm and hold keys, fallback tfms, shash state, CN10K errata context, PCI device, and algorithm metadata. Request contexts are per-operation and contain request info, control word, hardware flexicrypto context, and fallback request storage.

## Dependencies and integration points
The header depends on Crypto API hash/skcipher/aead types, common CPT definitions, and CN10K CPT helper state. It is included by VF main for crypto registration and by algorithm implementation for all request construction.

## Risks and edge cases
Bitfield layout in `otx2_cpt_encr_ctrl` and `otx2_cpt_offset_ctrl` depends on endian configuration. Key buffers combine authentication and encryption key material, so setkey code must respect max lengths and offsets. `struct otx2_cpt_req_ctx` contains a union of fallback request types, so request-size setup must match the algorithm class.

## Test signals
Signals include successful build across endian configurations, correct setkey behavior for all supported key sizes, valid hardware context bytes in request dumps, AEAD HMAC pad generation, fallback request storage sizing, and crypto selftests for all declared algorithm modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_algs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_main.c

## Purpose
This file is the PCI VF driver entry point. It probes VF devices, initializes PF/VF mailbox and interrupts, receives capabilities from the PF, initializes CN10K LMTST support, attaches LFs for kernel crypto, allocates pending queues/tasklets, registers LF interrupts, and registers Crypto API algorithms.

## Important APIs and functions
Driver entry points are `otx2_cptvf_probe()` and `otx2_cptvf_remove()`. Mailbox setup uses `cptvf_pfvf_mbox_init()`, `cptvf_register_interrupts()`, and interrupt enable/disable helpers. LF setup and teardown are handled by `cptvf_lf_init()` and `cptvf_lf_shutdown()`. Software queue/tasklet helpers are `alloc_pending_queues()`, `free_pending_queues()`, `init_tasklet_work()`, `cleanup_tasklet_work()`, and `lf_sw_init()/lf_sw_cleanup()`.

## Control flow
Probe allocates VF state, enables PCI/DMA/BARs, maps registers, sets hardware capability flags, initializes PF/VF mailbox and bounce buffer, registers mailbox interrupt, sends ready, selects CPT block and hardware ops, requests capabilities, optionally switches to CN10K SGv2 builder, initializes LMTST, then calls `cptvf_lf_init()`. LF init queries SE and AE engine group numbers, reads kernel VF LF limit, attaches LFs with the combined group mask, gets MSI-X offsets, allocates pending queues and tasklets, registers misc/done interrupts, sets affinity, marks LFs started, and registers crypto algorithms. Remove reverses LF, mailbox, and LMTST resources.

## State and persistence
Runtime state includes VF mailbox, VF id, engine capabilities, LF queues, pending queues, tasklets, IRQ affinity, LMTST memory, and Crypto API registrations. The LF atomic state gates request submission. No persistent storage is used.

## Dependencies and integration points
This file depends on PF mailbox services for engine groups, KVF limits, and capabilities; LF common setup for hardware queues; request manager for tasklet completion; algorithm code for Crypto API registration; and CN10K helpers for hardware ops/LMTST.

## Risks and edge cases
Probe ordering is strict: capability messages require mailbox readiness, and crypto registration requires fully initialized LFs and interrupts. Error paths must avoid registering algorithms before tasklets/queues are ready and must unwind interrupts before freeing pending queues. `cptvf_lf_shutdown()` disables queues directly rather than calling full `otx2_cptlf_shutdown()` so it can unregister crypto and interrupts first.

## Test signals
Signals include VF probe/remove, PF unavailable probe defer, valid SE/AE group lookup, KVF LF count selection, pending queue allocation failure unwind, tasklet completion of crypto requests, IRQ affinity cleanup, CN10K SGv2 path selection from capability bit 35, and crypto unregister when the last VF exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_mbox.c

## Purpose
This file implements VF-side PF/VF mailbox handling. It creates a bounce buffer for safe message preparation, synchronizes hardware mailbox responses into that buffer, handles PF responses, and sends VF requests for engine group numbers, kernel VF limits, and hardware capabilities.

## Important APIs and functions
Public APIs are `otx2_cpt_mbox_bbuf_init()`, `otx2_cptvf_pfvf_mbox_intr()`, `otx2_cptvf_pfvf_mbox_handler()`, `otx2_cptvf_send_eng_grp_num_msg()`, `otx2_cptvf_send_kvf_limits_msg()`, and `otx2_cptvf_send_caps_msg()`. Local helpers include `otx2_cpt_sync_mbox_bbuf()` and `process_pfvf_mbox_mbox_msg()`.

## Control flow
Mailbox init allocates a device-managed bounce buffer and redirects `mdev->mbase` to it. On interrupt, the handler queues mailbox work and acknowledges the VF interrupt bit. The work handler uses `smp_rmb()`, copies response bytes from hardware mailbox memory into the bounce buffer, validates response headers/signatures, processes each message, increments `msgs_acked`, and resets the mailbox. Send helpers allocate request/response mailbox slots, fill IDs/signatures/pcifunc, and call the shared send/wait helper.

## State and persistence
Responses update `cptvf->vf_id`, LF attach state, LF MSI-X offsets, AF register readback storage, SE/AE engine group numbers, KVF LF limits, and engine capabilities. Bounce-buffer memory persists for the VF device lifetime. There is no disk persistence.

## Dependencies and integration points
This file depends on RVU mailbox internals, shared mailbox send helpers, VF device state, and LF state. VF probe and LF init call its send helpers synchronously and rely on response processing to populate fields.

## Risks and edge cases
`otx2_cpt_sync_mbox_bbuf()` bounds response copy size by mailbox receive size to avoid overflow, but still trusts mailbox header placement. Responses with wrong signatures or unknown IDs are logged and ignored. `pcifunc` construction for VF requests uses the current `vf_id`, so requests after ready message are safest; early messages must use accepted PF/VF conventions.

## Test signals
Signals include ready response setting `vf_id`, capability response filling all engine caps, LF attach/detach flags changing after resource messages, valid MSI-X offset propagation, bounced mailbox responses on CN10K and OTX2, and ignored malformed responses without corrupting state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_reqmgr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_reqmgr.c

## Purpose
This file implements VF request submission and completion processing for CPT crypto operations. It allocates pending entries, builds CPT instructions from request-manager metadata, submits commands to LF hardware, polls completion results in order, maps hardware/microcode completion codes to Crypto API statuses, and invokes callbacks.

## Important APIs and functions
Public APIs are `otx2_cpt_do_request()`, `otx2_cpt_post_process()`, and `otx2_cpt_get_eng_grp_num()`. Internal helpers include `process_request()`, `process_pending_queue()`, `cpt_process_ccode()`, `get_free_pending_entry()`, `free_pentry()`, `modulo_inc()`, and debug dumping through `otx2_cpt_dump_sg_list()`.

## Control flow
Algorithm code calls `otx2_cpt_do_request()` with a prepared `otx2_cpt_req_info` and CPU/LF number. `process_request()` checks LF started state, creates SG/DMA info through hardware ops, initializes the completion code, reserves a pending queue entry under lock with bounded retry, records callback/request metadata, builds big-endian IQ command words, fills `otx2_cpt_inst_s`, sends the command, and returns `-EINPROGRESS` or `-EBUSY` to throttle senders. Done interrupt tasklets call `otx2_cpt_post_process()`, which drains pending entries from the front until it finds an incomplete request.

## State and persistence
Pending queue state tracks ring front/rear, pending count, busy entries, callbacks, completion addresses, and resume-sender flags. Each `otx2_cpt_inst_info` owns DMA mappings and timing fields until callback cleanup. Completion state is DMA-written by hardware. No persistent storage is used.

## Dependencies and integration points
This file depends on VF device state from PCI drvdata, LF hardware ops, request-manager SG builders, hardware completion-code definitions, and algorithm callbacks. It is triggered by LF done interrupts scheduled in `otx2_cptlf.c` and tasklets created in VF main.

## Risks and edge cases
Completion processing is strictly in order; a stuck earlier entry blocks later completed entries. `CPT_COMP_E_NOTDONE` extends timeout a few times before repeatedly warning and returning for later polling. Queue throttling uses `resume_sender` entries and callback `-EINPROGRESS` to restart senders. Debug dumps can expose plaintext/key-adjacent data if dynamic debug is enabled. Error cases must still call callbacks and free DMA state.

## Test signals
Signals include async Crypto API completion, queue-full `-EBUSY` and resume behavior, timeout warnings on dropped completions, correct status mapping for fault/hwerr/insterr/software microcode errors, truncated-HMAC success handling for SG write length, DMA cleanup under every completion code, and CPU-to-LF queue selection under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_reqmgr.c -->
