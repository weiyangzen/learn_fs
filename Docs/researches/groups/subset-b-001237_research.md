# subset-b-001237 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/hash.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/hash.c

### Purpose
`hash.c` implements the Marvell CESA asynchronous hash provider for MD5, SHA1, SHA256, and HMAC variants. It supports both the older direct SRAM copy path and the TDMA path, translates Linux `ahash_request` state into CESA operation descriptors, handles hash padding, and registers the `mv-*` kernel-only async hash algorithms.

### Important APIs, Types, And Functions
The main request state is `struct mv_cesa_ahash_req`, with DMA-specific cache/padding state under `req.dma`, software/SRAM offset state under `req.std`, operation template `op_tmpl`, current digest state, total byte count, cached partial block length, source SG count, `last_req`, and digest endianness. Important helpers are `mv_cesa_ahash_init()`, `mv_cesa_ahash_update()`, `mv_cesa_ahash_final()`, `mv_cesa_ahash_finup()`, `mv_cesa_ahash_req_init()`, `mv_cesa_ahash_dma_req_init()`, `mv_cesa_ahash_std_step()`, `mv_cesa_ahash_dma_step()`, `mv_cesa_ahash_complete()`, export/import helpers, and HMAC key setup through `mv_cesa_ahmac_setkey()`. Exported algorithm descriptors are `mv_md5_alg`, `mv_sha1_alg`, `mv_sha256_alg`, `mv_ahmac_md5_alg`, `mv_ahmac_sha1_alg`, and `mv_ahmac_sha256_alg`.

### Control Flow, State, And Persistence
`init` seeds digest constants and a first-fragment CESA op template. `update` advances `creq->len`, caches data smaller than one block when possible, or maps SG entries and builds TDMA descriptors when TDMA is available. Non-DMA requests copy cached bytes and SG payload into engine SRAM, update fragment mode, append manual padding if hardware cannot use a total-length final operation, then starts accelerator channel 0. DMA requests assemble cache transfers, source transfers, operation descriptors, dummy launch/end descriptors, optional result copies, and padding buffers, then queue through the common CESA request engine. Completion either copies a DMA result from an op context or reads `CESA_IVDIG()` registers and writes final digest bytes in MD5 little-endian or SHA big-endian format. Export/import persists hash state as Linux hash state structures plus cached partial blocks.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on `cesa.h`, crypto ahash/HMAC APIs, DMA pools, SG mapping, `mv_cesa_queue_req()`, TDMA helpers in `tdma.c`, engine load accounting, and CESA SRAM/register helpers. Risks include digest corruption around cached partial blocks, final padding crossing the SRAM payload boundary, TDMA chain break semantics when state must be explicitly reloaded, DMA-map cleanup after partial descriptor construction, MD5/SHA endian conversion, and HMAC IV state byte order. Test signals include crypto manager vectors for md5/sha1/sha256/hmac variants, multi-update requests with sub-block boundaries, export/import continuation, zero-length final, large messages requiring manual padding, TDMA and non-TDMA builds, SG lists with offsets, and async backlog/error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/tdma.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/tdma.c

### Purpose
`tdma.c` provides CESA TDMA descriptor-chain helpers shared by cipher and hash implementations. It builds DMA descriptor lists, prepares SRAM-relative addresses for a selected engine, launches hardware TDMA execution, processes completed request boundaries, and frees descriptor resources.

### Important APIs, Types, And Functions
Key entry points are `mv_cesa_req_dma_iter_next_transfer()`, `mv_cesa_dma_step()`, `mv_cesa_dma_cleanup()`, `mv_cesa_dma_prepare()`, `mv_cesa_tdma_chain()`, `mv_cesa_tdma_process()`, `mv_cesa_dma_add_result_op()`, `mv_cesa_dma_add_op()`, `mv_cesa_dma_add_data_transfer()`, `mv_cesa_dma_add_dummy_launch()`, `mv_cesa_dma_add_dummy_end()`, `mv_cesa_dma_add_op_transfers()`, and `mv_cesa_sg_copy()`. It manipulates `struct mv_cesa_tdma_chain`, `struct mv_cesa_tdma_desc`, engine software/hardware chain pointers, TDMA flags such as `CESA_TDMA_OP`, `CESA_TDMA_DATA`, `CESA_TDMA_RESULT`, `CESA_TDMA_END_OF_REQ`, `CESA_TDMA_BREAK_CHAIN`, and SRAM source/destination markers.

### Control Flow, State, And Persistence
Descriptor builders append zeroed descriptors from the TDMA pool, link `next` and `next_dma`, and attach op contexts or data moves. `mv_cesa_dma_prepare()` converts SRAM-relative offsets to engine-specific DMA addresses and adjusts op contexts for the engine. `mv_cesa_tdma_chain()` appends a request to the engine software chain unless the next request must reload state or the previous request breaks the chain. `mv_cesa_dma_step()` promotes the prepared request to the hardware chain, programs TDMA control and next address registers, and starts CESA. `mv_cesa_tdma_process()` walks hardware descriptors until the current hardware pointer or an incomplete request, dequeues logical crypto requests at `END_OF_REQ`, invokes request-specific `process` and `complete`, queues completed requests, and preserves a failed request in `engine->req`.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on CESA DMA pools, engine locks, request queues, crypto async request completion, SG mapping iterators, and low-level CESA TDMA/SA registers. Risks include chain pointer races under `engine->lock`, freeing op DMA pools only for `CESA_TDMA_OP`, correctly re-chaining after each logical request, not missing the hardware current descriptor, and SG iterator offset math across scatterlist boundaries. Test signals include chained cipher/hash requests, state-reload chain breaks, result-copy descriptors, SG lists with more than one segment, forced descriptor allocation failure, TDMA interrupt processing with backlog completion, and noncoherent SRAM copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/tdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/Makefile -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/Makefile

### Purpose
This Makefile wires the OcteonTX CPT PF and VF drivers into the kernel build when `CONFIG_CRYPTO_DEV_OCTEONTX_CPT` is enabled.

### Important APIs, Types, And Functions
It builds two composite objects: `octeontx-cpt.o` from `otx_cptpf_main.o`, `otx_cptpf_mbox.o`, and `otx_cptpf_ucode.o`; and `octeontx-cptvf.o` from `otx_cptvf_main.o`, `otx_cptvf_mbox.o`, `otx_cptvf_reqmgr.o`, and `otx_cptvf_algs.o`.

### Control Flow, State, And Persistence
The PF object owns physical-function probing, SR-IOV, mailbox service, and microcode/engine-group management. The VF object owns virtual-function probing, PF mailbox handshakes, CPT instruction queues, completion processing, and crypto algorithm registration. Build composition persists only as link-time object membership controlled by the Kconfig symbol.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay aligned with symbols shared across PF/VF sources, especially mailbox definitions in `otx_cpt_common.h` and exported microcode helpers used by PF mailbox handling. Risks are unresolved symbols if object membership changes and accidentally building only PF or VF halves. Test signals are `CONFIG_CRYPTO_DEV_OCTEONTX_CPT=y/m` builds and module load/unload with both `octeontx-cpt` and `octeontx-cptvf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_common.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_common.h

### Purpose
`otx_cpt_common.h` defines the shared PF/VF mailbox contract and engine type identifiers for the OcteonTX CPT driver family.

### Important APIs, Types, And Functions
Important definitions are `OTX_CPT_MAX_MBOX_DATA_STR_SIZE`, `enum otx_cptpf_type`, `enum otx_cptvf_type`, `enum otx_cpt_mbox_opcode`, and `struct otx_cpt_mbox`. PF types distinguish AE and SE physical functions; VF types distinguish AE and SE engine-group assignments; mailbox opcodes cover VF up/down, readiness, queue length, group binding, priority, PF type query, ACK, and NACK.

### Control Flow, State, And Persistence
No executable state lives here. The definitions persist as ABI-like expectations between `otx_cptpf_mbox.c` and `otx_cptvf_mbox.c`: mailbox register word 0 carries `msg`, word 1 carries `data`, and both sides interpret values through the shared opcode enum.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends only on common Linux types and is included by PF, VF, algorithm, and request-manager code. Risks center on changing opcode numbers or type values, because PF and VF modules communicate through hardware registers rather than typed calls. Test signals include PF/VF readiness handshakes, group binding returning SE or AE type, NACK handling, mailbox debug dumps, and mixed PF/VF module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_hw_types.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_hw_types.h

### Purpose
`otx_cpt_hw_types.h` is the OcteonTX CPT hardware register and descriptor map. It provides PCI IDs, BAR indices, register offsets, interrupt masks, instruction/result layouts, queue-control bitfields, completion codes, and hardware error-code formats used by PF and VF drivers.

### Important APIs, Types, And Functions
Important constants include PF/VF PCI IDs, BAR selectors, PF/VF MSI-X vector counts, mailbox interrupt offsets, `OTX_CPT_MAX_ENGINE_GROUPS`, `OTX_CPT_INST_SIZE`, queue chunk pointer size, VF interrupt masks, and PF/VF register offset macros. Key enums and unions are `enum otx_cpt_ucode_error_code_e`, `enum otx_cpt_comp_e`, `enum otx_cpt_vf_int_vec_e`, `union otx_cpt_inst_s`, `union otx_cpt_res_s`, `union otx_cptx_pf_bist_status`, `union otx_cptx_pf_constants`, `union otx_cptx_pf_exe_bist_status`, `union otx_cptx_pf_qx_ctl`, `union otx_cptx_vqx_saddr`, interrupt enable/status unions, doorbell, done, done-wait, queue-control, and `union otx_cpt_error_code`.

### Control Flow, State, And Persistence
The header has no functions but dictates how runtime code programs hardware. PF probe reads BIST and constants, PF mailbox writes `PF_QX_CTL`, VF probe configures queue base, doorbell, done coalescing, and interrupts, and the request manager fills `CPT_INST_S` and parses `CPT_RES_S` plus microcode error codes. Bitfield definitions are endian-conditional and must match hardware wire layout.

### Dependencies, Integration Points, Risks, And Test Signals
All OcteonTX CPT C files depend on this header. Risks include incorrect bitfield layout on big-endian builds, queue size units in 64-bit words versus instruction count, doorbell units as eight 64-bit words per instruction, result alignment expectations, and stale register offsets. Test signals include PF BIST failure reporting, queue control programming from mailbox QLEN/group/priority, VF misc and done interrupts, request completion-code handling, doorbell overflow paths, and endian build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cpt_hw_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf.h

### Purpose
`otx_cptpf.h` defines the PF driver state container and PF-local cross-file APIs for OcteonTX CPT physical-function management.

### Important APIs, Types, And Functions
`struct otx_cpt_device` stores the MMIO register base, PCI device, engine-group manager, list node, PF type, maximum VF count, and enabled VF count. It declares `otx_cpt_mbox_intr_handler()` from the PF mailbox path and `otx_cpt_disable_all_cores()` from the microcode/engine management path.

### Control Flow, State, And Persistence
The PF probe allocates and stores this structure as PCI drvdata, initializes hardware capabilities and engine groups, and later uses the same state for SR-IOV enable/disable and mailbox handling. Engine-group state persists across VF mailbox requests while SR-IOV is active and is marked read-only during VF exposure.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on `otx_cptpf_ucode.h` for `struct otx_cpt_eng_grps`. Risks include stale `vfs_enabled` relative to PCI SR-IOV state, mailbox handlers seeing partially initialized engine groups, and PF teardown while VFs are still live. Test signals include PF probe/remove, SR-IOV sysfs configuration, mailbox interrupts after VF probe, engine disable on remove, and drvdata lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_main.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_main.c

### Purpose
`otx_cptpf_main.c` is the PCI physical-function driver for OcteonTX CPT. It probes the PF, resets and validates hardware, initializes engine-group management, services VF mailbox interrupts, and controls SR-IOV VF enablement.

### Important APIs, Types, And Functions
Important functions are `otx_cpt_probe()`, `otx_cpt_remove()`, `otx_cpt_sriov_configure()`, `otx_cpt_device_init()`, `otx_cpt_register_interrupts()`, `otx_cpt_unregister_interrupts()`, `otx_cpt_reset()`, `otx_cpt_find_max_enabled_cores()`, BIST readers, and mailbox interrupt wrapper `otx_cpt_mbx0_intr_handler()`. The PCI driver binds Cavium device `OTX_CPT_PCI_PF_DEVICE_ID` under name `octeontx-cpt`.

### Control Flow, State, And Persistence
Probe allocates `struct otx_cpt_device`, enables PCI, requests BAR regions, sets a 48-bit DMA mask, maps BAR0, resets CPT, waits 100 ms, checks RAM and engine BIST, reads PF constants to derive available SE/AE cores, determines PF type from subsystem ID and available cores, records total SR-IOV VFs, disables all cores, registers MSI-X mailbox interrupts, and initializes engine groups. `sriov_configure` creates default microcode-backed engine groups before enabling VFs, marks group configuration read-only while VFs are enabled, and pins the module; disabling VFs reverses read-only state and drops the module reference. Remove disables SR-IOV, cleans engine groups, unregisters interrupts, disables cores, unmaps BARs, releases regions, and clears drvdata.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates PCI core, MSI-X, DMA mask setup, SR-IOV, PF mailbox code, and microcode/engine-group management. Risks include reset/BIST timing, PF type inference when both SE and AE counts are present or absent, `module_put()` symmetry if SR-IOV disable is called without prior enable, interrupt registration rollback, and read-only engine groups while userspace attempts sysfs changes. Test signals include PF probe under hardware or emulation, BIST failure injection, SR-IOV enable with valid firmware tar, SR-IOV disable, mailbox IRQ receipt, module unload with VFs enabled, and DMA mask failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_mbox.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_mbox.c

### Purpose
`otx_cptpf_mbox.c` implements PF-side handling of mailbox messages from OcteonTX CPT VFs. It programs VF queue properties, binds VQs to engine groups, returns VF identity and type data, and ACKs or NACKs control requests.

### Important APIs, Types, And Functions
The public entry point is `otx_cpt_mbox_intr_handler()`. Important helpers are `otx_cpt_handle_mbox_intr()`, `otx_cpt_send_msg_to_vf()`, ACK/NACK helpers, `otx_cpt_clear_mbox_intr()`, `otx_cpt_cfg_qlen_for_vf()`, `otx_cpt_cfg_vq_priority()`, `otx_cpt_bind_vq_to_grp()`, and mailbox debug formatting helpers.

### Control Flow, State, And Persistence
The PF interrupt handler reads the mailbox interrupt bitmap and iterates VFs up to `cpt->max_vfs`. For each asserted bit it reads VF mailbox words, dispatches by opcode, writes responses through PF-to-VF mailbox registers, and clears the interrupt. QLEN updates `PF_QX_CTL.size` and `cont_err`; VQ priority updates `PF_QX_CTL.pri`; group binding validates queue and group bounds, verifies the target group is enabled, writes `PF_QX_CTL.grp`, examines the group or mirrored group's microcode support, and returns the VF engine type. READY returns the VF number, VF_UP returns enabled VF count, PF_TYPE returns PF type, and unsupported binding returns NACK.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on shared mailbox opcodes, PF hardware registers, engine-group state from `otx_cptpf_ucode.c`, and VF polling behavior in `otx_cptvf_mbox.c`. Risks include mailbox register ordering, VF IDs wider than the interrupt bitmap loop type, binding VFs to disabled or mirrored groups, queue-size unit mismatch, and no explicit locking around engine-group reads while SR-IOV state changes. Test signals include VF probe handshake, QLEN/priority/group sysfs changes from VF, invalid group NACK, PF_TYPE query, mailbox interrupt clearing, and debug dumps for each opcode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_ucode.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_ucode.c

### Purpose
`otx_cptpf_ucode.c` manages OcteonTX CPT microcode and engine groups for the PF driver. It parses firmware tar archives or direct firmware names, allocates DMA memory for microcode images, reserves SE/AE engines, configures hardware engine group registers, exposes sysfs controls, supports mirrored engine groups, and tears all of it down safely.

### Important APIs, Types, And Functions
Public APIs are `otx_cpt_init_eng_grps()`, `otx_cpt_cleanup_eng_grps()`, `otx_cpt_try_create_default_eng_grps()`, `otx_cpt_set_eng_grps_is_rdonly()`, `otx_cpt_disable_all_cores()`, and exported `otx_cpt_uc_supports_eng_type()`. Important internals include tar parsing (`load_tar_archive()`, `process_tar_file()`, `get_uc_from_tar_archive()`), microcode loading (`ucode_load()`, `copy_ucode_to_dma_mem()`, `ucode_unload()`), engine reservation/release (`reserve_engines()`, `release_engines()`, `eng_grp_update_masks()`), hardware programming (`cpt_set_ucode_base()`, `cpt_attach_and_enable_cores()`, `cpt_detach_and_disable_cores()`), group creation/deletion, mirroring helpers, and sysfs `ucode_load_store()` / `eng_grp_info_show()`.

### Control Flow, State, And Persistence
Initialization creates per-group bookkeeping, bitmaps, sysfs names, supported engine-type masks, and the `ucode_load` device attribute. Default creation, invoked before first SR-IOV enable, loads `cpt8x-mc.tar`, selects SE and AE microcode entries, and creates groups using all available engines of each supported type. Manual sysfs input can create groups from `engine_type:count:ucode` style fields or delete `engine_groupN:null`, subject to the read-only flag. Group creation loads microcode, validates engine support, optionally mirrors an existing group with the same version string, reserves engines, computes bitmaps and reference counts, creates group info sysfs, writes microcode base registers, and enables cores. Cleanup removes sysfs, deletes mirrored groups before source groups, unloads DMA firmware, releases engine references, and frees bitmaps.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on Linux firmware loading, tar header parsing, PCI device state, PF register definitions, DMA coherent allocation, sysfs device attributes, mutex protection in `eng_grps->lock`, and PF/VF mailbox binding through group state. Risks include firmware archive bounds parsing, microcode size and alignment validation, mirrored group reference accounting, partial group creation unwind, engine refcount mismatches, read-only enforcement while VFs are enabled, timeout behavior when cores remain busy, and invalid user sysfs strings. Test signals include valid and malformed `cpt8x-mc.tar`, missing firmware, default group creation for SE and AE PFs, sysfs group create/delete, mirrored microcode reuse, SR-IOV read-only blocking, cleanup after failed load, and VF group binding to created groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_ucode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_ucode.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_ucode.h

### Purpose
`otx_cptpf_ucode.h` defines the microcode, engine, engine-group, mirroring, and availability data model used by the OcteonTX CPT PF microcode manager.

### Important APIs, Types, And Functions
Important constants include microcode name, tar name, alignment, signature length, version string size, max engines, engine bitmap length, and `OTX_CPT_MAX_ETYPES_PER_GRP`. Important types are `enum otx_cpt_ucode_type`, `struct otx_cpt_bitmap`, `struct otx_cpt_engines`, `struct otx_cpt_ucode_ver_num`, `struct otx_cpt_ucode_hdr`, `struct otx_cpt_ucode`, `struct tar_ucode_info_t`, `struct otx_cpt_engs_available`, `struct otx_cpt_engs_rsvd`, `struct otx_cpt_mirror_info`, `struct otx_cpt_eng_grp_info`, and `struct otx_cpt_eng_grps`. It declares PF-facing lifecycle and query functions.

### Control Flow, State, And Persistence
The structures persist all PF engine-group state across SR-IOV enablement: available SE/AE counts, per-engine reference counts, per-group reserved bitmaps, microcode DMA addresses, sysfs attributes, mirror relationships, lock, read-only flag, and default-creation cursor. `struct otx_cpt_ucode_hdr` mirrors firmware image headers and is used to validate and classify loaded microcode.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on PCI, module, and OcteonTX hardware type definitions. Risks include fixed limits mismatching hardware capabilities, one-engine-type-per-group assumptions, bitmap sizing, and exposing internal structs to PF code that must respect the mutex. Test signals include compile coverage, default group creation with max engine counts, engine bitmap bounds, firmware header parsing, group info sysfs output, and PF mailbox `otx_cpt_uc_supports_eng_type()` decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_ucode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf.h

### Purpose
`otx_cptvf.h` defines the OcteonTX CPT virtual-function runtime state, queue structures, readiness flags, and VF-to-PF mailbox APIs used by the VF driver, request manager, and algorithm layer.

### Important APIs, Types, And Functions
Important macros include `OTX_CPT_FLAG_DEVICE_READY`, `otx_cpt_device_ready()`, command queue length/chunk size, and one queue per VF. Types include `struct otx_cpt_cmd_chunk`, `struct otx_cpt_cmd_queue`, `struct otx_cpt_cmd_qinfo`, `struct otx_cpt_pending_qinfo`, `struct otx_cptvf_wqe`, `struct otx_cptvf_wqe_info`, and `struct otx_cptvf`. Declared APIs send VF up/down, group, priority, queue-size, and ready mailbox messages; handle mailbox interrupts; and ring the VQ doorbell.

### Control Flow, State, And Persistence
The VF probe allocates `struct otx_cptvf`, configures command and pending queues, stores PF-assigned VF ID/type/group data from mailbox replies, and sets the ready flag after hardware queue initialization. Queue state persists while the PCI VF is bound and is consumed by request submission and completion tasklets. Mailbox `pf_acked` and `pf_nacked` fields are transient polling flags.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on interrupt, device, common mailbox, and request-manager definitions. Risks include fixed one-queue assumptions, using `u8` fields for VF and group counts, tasklet lifetime versus PCI remove, and `pf_acked` polling without stronger synchronization. Test signals include VF probe/remove, queue allocation/free, mailbox timeout and NACK paths, request submission only after ready flag, and sysfs reads of VF type and group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.c

### Purpose
`otx_cptvf_algs.c` registers and implements the Linux crypto API algorithms backed by OcteonTX CPT VFs. It formats skcipher and AEAD requests into CPT flexicrypto/HMAC command inputs, manages key material and HMAC pads, dispatches requests to an SE VF, and handles async callbacks.

### Important APIs, Types, And Functions
Public APIs are `otx_cpt_crypto_init()` and `otx_cpt_crypto_exit()`. Key internals include device tables `se_devices` and `ae_devices`, `get_se_device()`, callbacks `otx_cpt_skcipher_callback()` and `otx_cpt_aead_callback()`, skcipher formatting (`create_ctx_hdr()`, `create_input_list()`, `create_output_list()`, `cpt_enc_dec()`), key setters for AES/DES3/XTS, AEAD init/exit/authsize/setkey helpers, HMAC pad setup (`aead_hmac_init()`), AEAD list builders, null-cipher HMAC verification, and registration arrays `otx_cpt_skciphers` and `otx_cpt_aeads`.

### Control Flow, State, And Persistence
VF probe calls `otx_cpt_crypto_init()` after PF group binding; SE VFs are added to a sorted table, and algorithms register only after the expected number of devices is present. Each crypto request clears request context, builds control words, FC/HMAC context, input and output buffer pointer arrays, assigns callback and metadata, selects an SE device, and calls `otx_cpt_do_request()`. Completion callbacks clean DMA/request buffers and complete the original crypto async request; skcipher callbacks also copy back CBC IV state. Key setup persists cipher keys, auth keys, derived HMAC ipad/opad hash states, AES key type, auth size, and truncation flags in transform context. `crypto_exit` removes the VF from the device table and unregisters algorithms only when the last SE device disappears and algorithms are not in use.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on Linux skcipher/AEAD/authenc APIs, shash providers, scatterwalk, request-manager DMA cleanup, VF device registration, module refs, and crypto algorithm refcounts. Risks include scatterlist virtual-address assumptions via `sg_virt()`, request-size and SG-count limits, IV copyback for in-place CBC decrypt, null-cipher HMAC manual verification, truncated HMAC status handling, algorithm registration lifetime with multiple VFs, and refusing skcipher registration under `CONFIG_DM_CRYPT`. Test signals include AES CBC/ECB/XTS, 3DES CBC/ECB, authenc HMAC-SHA CBC-AES, null-cipher HMAC, RFC4106 GCM, truncated auth sizes, in-place and out-of-place SGs, request size > 65535, VF hot-unplug while algorithms are referenced, and crypto manager async tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.h

### Purpose
`otx_cptvf_algs.h` defines CPT crypto operation opcodes, cipher/MAC identifiers, control words, transform contexts, request contexts, and algorithm registration APIs for the OcteonTX VF crypto layer.

### Important APIs, Types, And Functions
Important enums define request types, major opcodes, AE/SE request classification, cipher types, MAC types, and AES key length encodings. Key structures and unions are `union otx_cpt_encr_ctrl`, `struct otx_cpt_enc_context`, `union otx_cpt_fchmac_ctx`, `struct otx_cpt_fc_ctx`, `struct otx_cpt_enc_ctx`, `struct otx_cpt_des3_ctx`, `union otx_cpt_offset_ctrl_word`, `struct otx_cpt_req_ctx`, `struct otx_cpt_sdesc`, and `struct otx_cpt_aead_ctx`. It declares `otx_cpt_crypto_init()` and `otx_cpt_crypto_exit()`.

### Control Flow, State, And Persistence
The structures are embedded in crypto transform and request contexts. Per-transform state holds keys, key types, hash algorithms, HMAC pads, and AEAD configuration. Per-request state combines a CPT request manager object, an offset control word, and flexicrypto context sent to hardware as gather-list inputs.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on crypto hash APIs, shared CPT type enums, and request-manager definitions. Risks include endian-sensitive control-word bitfields, max key size layout for combined auth/encryption keys, XTS second key offset assumptions, and mismatches between algorithm code and microcode opcode expectations. Test signals include compile coverage on endian variants, algorithm request context sizing, AES key length mapping, authenc key parsing, GCM salt/IV layout, and hardware command dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_algs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_main.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_main.c

### Purpose
`otx_cptvf_main.c` is the PCI VF driver for OcteonTX CPT. It allocates command and pending queues, initializes VF hardware registers, handles misc and done interrupts, manages sysfs VF controls, performs PF mailbox setup, and registers crypto algorithms.

### Important APIs, Types, And Functions
Important functions are `otx_cptvf_probe()`, `otx_cptvf_remove()`, `cptvf_sw_init()`, queue allocation/free helpers, tasklet setup, `cptvf_device_init()`, register writers for VQ control/doorbell/inflight/done wait/saddr, interrupt handlers `cptvf_misc_intr_handler()` and `cptvf_done_intr_handler()`, IRQ affinity helpers, and sysfs show/store functions for `vf_type`, `vf_engine_group`, `vf_coalesc_time_wait`, and `vf_coalesc_num_wait`.

### Control Flow, State, And Persistence
Probe enables PCI, requests BARs, sets a 48-bit DMA mask, maps VF BAR0, allocates MSI-X vectors, requests misc IRQ, enables mailbox and software-error interrupts, sends READY to PF, allocates command chunks as a circular DMA instruction queue, allocates pending queues, initializes tasklets, sends queue size to PF, programs VQ base/coalescing/doorbell/inflight registers, binds to an engine group, sets priority, requests done IRQ, enables done interrupts, sets affinity, sends VF_UP, registers crypto algorithms, and creates sysfs attributes. Done interrupts acknowledge completion count and schedule a high-priority tasklet to call request post-processing. Remove first sends VF_DOWN; on success it removes sysfs, unregisters crypto algorithms, frees IRQ affinity, IRQs, queues, BARs, regions, and drvdata.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on PCI/MSI-X, DMA coherent allocation, PF mailbox, request-manager post-processing, crypto algorithm registration, sysfs, tasklets, and hardware register definitions. Risks include command chunk circular pointer correctness, cleanup asymmetry when VF_DOWN times out, tasklet scheduling after queue teardown, coalescing bounds, IRQ affinity allocation failure handling, and `free_done_irq` label behavior after failed done IRQ request. Test signals include VF probe/remove with PF present and absent, mailbox timeout, queue allocation failure unwind, completion interrupt processing, misc error interrupts, sysfs group rebinding, coalescing writes at min/max bounds, and crypto request completion under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_mbox.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_mbox.c

### Purpose
`otx_cptvf_mbox.c` implements VF-side mailbox communication with the OcteonTX CPT PF. It sends synchronous control messages, handles PF replies in the misc interrupt path, and stores PF-provided VF identity, VF count, and engine type.

### Important APIs, Types, And Functions
Public functions are `otx_cptvf_handle_mbox_intr()`, `otx_cptvf_check_pf_ready()`, `otx_cptvf_send_vq_size_msg()`, `otx_cptvf_send_vf_to_grp_msg()`, `otx_cptvf_send_vf_priority_msg()`, `otx_cptvf_send_vf_up()`, and `otx_cptvf_send_vf_down()`. Internal helpers include `cptvf_send_msg_to_pf()`, `cptvf_send_msg_to_pf_timeout()`, and mailbox debug formatting.

### Control Flow, State, And Persistence
Sending clears `pf_acked` and `pf_nacked`, writes message and data to VF-to-PF mailbox registers, then polls up to two seconds in 10 ms sleeps for an interrupt handler to set either flag. The interrupt handler reads the PF mailbox words and updates state: READY stores `vfid`, QBIND_GRP stores `vftype`, VF_UP stores `num_vfs`, ACK sets `pf_acked`, and NACK sets `pf_nacked`. Group messages update `vfgrp` only after a successful PF response.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on PF mailbox opcode semantics, VF misc interrupts being enabled before synchronous waits, sleepable probe/sysfs contexts, and MMIO register ordering. Risks include polling flags without completions or barriers, timeout if interrupts are masked, no serialization around concurrent sysfs mailbox sends, and comments that misstate VF_DOWN as UP. Test signals include READY during probe, QLEN and priority ACK, group bind success and NACK, PF not responding, VF_DOWN during remove, and mailbox debug dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.c

### Purpose
`otx_cptvf_reqmgr.c` turns algorithm-layer CPT requests into DMA gather/scatter lists, hardware instructions, command queue entries, and pending completion records. It also scans completion status and invokes crypto callbacks.

### Important APIs, Types, And Functions
Public APIs are `otx_cpt_dump_sg_list()`, `otx_cpt_do_request()`, and `otx_cpt_post_process()`. Important internals include pending entry management, `setup_sgio_components()`, `setup_sgio_list()`, `cpt_fill_inst()`, `cpt_send_cmd()`, `process_request()`, `cpt_process_ccode()`, and `process_pending_queue()`.

### Control Flow, State, And Persistence
Submission validates VF readiness and SE/AE request compatibility, allocates a combined info/list/result/completion buffer, maps input and output buffers bidirectionally, writes SG component lists and header counts, maps the SG list buffer, initializes completion code, reserves a pending queue entry under lock, fills callback/request pointers, creates a CPT instruction with opcode/params/dlen and DPTR/RPTR/CPTR group, copies the instruction into the current command queue slot, advances circular chunk pointers, issues a write barrier, and rings the VF doorbell. Completion processing walks pending entries in FIFO order, checks hardware completion code and microcode error code, handles not-done timeout extension, treats truncated-HMAC scatter/gather write-length errors as success, wakes senders when the resume margin is reached, frees pending entries, and calls callbacks outside the queue lock.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on VF queue state, hardware instruction/result layouts, DMA mapping APIs, jiffies timeouts, algorithm callbacks, and cleanup helpers in the request-manager header. Risks include a cleanup typo in failed SG mapping that unmaps `list[i]` instead of `list[j]`, leaking mapped buffers after partial `setup_sgio_list()` failures, FIFO completion assumptions while hardware can complete out of order, busy-waiting for pending entries, bidirectional mappings for all buffers, and callback resume ordering. Test signals include DMA mapping failure injection, SG counts over 50, queue-full `-EBUSY`/resume behavior, CPT fault/SWERR/HWERR completion codes, not-done timeout warnings, truncated HMAC decrypt, and request cleanup after callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.h

### Purpose
`otx_cptvf_reqmgr.h` defines the OcteonTX VF request-manager ABI between crypto algorithms, the VF device, and hardware instruction submission.

### Important APIs, Types, And Functions
Important constants cover SG limits, DMA mode, context source, instruction queue alignment, max request size, command timeout, coalescing defaults and bounds. Key types include `union otx_cpt_opcode_info`, `struct otx_cptvf_request`, `struct otx_cpt_buf_ptr`, `union otx_cpt_ctrl_info`, CPT instruction command word unions, `struct otx_cpt_iq_cmd`, `struct otx_cpt_sglist_component`, `struct otx_cpt_pending_entry`, `struct otx_cpt_pending_queue`, `struct otx_cpt_req_info`, and `struct otx_cpt_info_buffer`. It defines inline `do_request_cleanup()` and declares request submission/post-process APIs.

### Control Flow, State, And Persistence
Per-request state persists from algorithm formatting through hardware completion and callback cleanup. `otx_cpt_req_info` holds input/output buffer arrays, opcode parameters, request type, encryption/truncated-HMAC flags, and callback. `otx_cpt_info_buffer` records DMA addresses and timing used by completion processing. `do_request_cleanup()` unmaps the SG list buffer plus all input/output DMA mappings and frees sensitive info memory.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on Linux crypto, PCI, and OcteonTX hardware types. Risks include endian-sensitive command/control bitfields, fixed SG array limits, cleanup relying on `info->req` being set, and all users obeying max request size. Test signals include build coverage for callers, cleanup after successful and failed requests, SG limit validation, coalescing sysfs bounds, command timeout behavior, and SE/AE group selection in CPTR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptvf_reqmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/Makefile -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/Makefile

### Purpose
This Makefile composes the OcteonTX2/CN10K CPT common, PF, and VF driver objects when `CONFIG_CRYPTO_DEV_OCTEONTX2_CPT` is enabled.

### Important APIs, Types, And Functions
It builds `rvu_cptcommon.o` from CN10K, LF, and mailbox common files; `rvu_cptpf.o` from PF main, PF mailbox, PF microcode, and devlink files; and `rvu_cptvf.o` from VF main, VF mailbox, VF request manager, and VF algorithms. It also adds the OcteonTX2 AF include path for `rvu.h` and `mbox.h`.

### Control Flow, State, And Persistence
The common object provides shared LF, mailbox, and CN10K hardware ops exported to PF/VF modules. PF and VF objects are built as separate driver units under the same Kconfig switch. Build state is limited to object membership and include path selection.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile integrates the crypto driver with the networking AF headers under `drivers/net/ethernet/marvell/octeontx2/af`. Risks include broken namespace exports if common objects are omitted, missing include path for AF mailbox definitions, and link errors from splitting shared CN10K helpers. Test signals include all built-in/module combinations for `CONFIG_CRYPTO_DEV_OCTEONTX2_CPT`, modpost namespace checks, and PF/VF module load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.c

### Purpose
`cn10k_cpt.c` adds CN10K-specific CPT command submission, LMTST setup, and hardware-context errata helpers while preserving fallback OcteonTX2 hardware operations.

### Important APIs, Types, And Functions
Important functions are CN10K `send_cmd`, `cn10k_cptpf_lmtst_init()`, `cn10k_cptvf_lmtst_init()`, `cn10k_cpt_lmtst_free()`, `cn10k_cpt_hw_ctx_init()`, `cn10k_cpt_hw_ctx_clear()`, `cn10k_cpt_hw_ctx_set()`, `cn10k_cpt_ctx_flush()`, and `cptvf_hw_ops_get()`. It defines hardware ops tables selecting either `otx2_cpt_send_cmd`/CN9K completion parsing or CN10K LMTST send/response parsing.

### Control Flow, State, And Persistence
PF/VF LMTST init checks capability flags; without CN10K LMTST the PF uses the OcteonTX2 ops table, while CN10K allocates force-contiguous LMTLINE DMA memory, aligns it to `LMTLINE_ALIGN`, registers it with firmware through `otx2_cpt_lmtst_tbl_setup_msg()`, and installs CN10K ops. Command submission copies instructions to the LF slot's LMTLINE after `dma_wmb()` and flushes through `cn10k_lmt_flush()`. Errata context init allocates and maps a 256-byte hardware context only for affected CN10KA revisions, sets the AOP-valid header, tags the DMA pointer with bit 60, and clear flushes/invalidate before unmapping.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on OcteonTX2 PF/VF/LF structs, AF mailbox setup, Marvell LMT assembly helpers, DMA attributes, hardware capability flags, and CN10K result formats from `cn10k_cpt.h`. Risks include pointer arithmetic on `void *` LMT bases, allocation alignment/unwind, using VF drvdata in `cn10k_cpt_ctx_flush()`, errata revision detection, and ensuring `dma_wmb()` precedes LMT flush. Test signals include CN10K and non-CN10K command submission, LMTST setup failure unwind, PF/VF LMT memory free, errata context init/clear on CN10KA A-step, context flush invalidation, and ops selection by capability bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.h

### Purpose
`cn10k_cpt.h` declares CN10K-specific CPT hardware context structures, completion-code accessors, LMTST lifecycle helpers, errata context helpers, context flush, and VF hardware-op selection.

### Important APIs, Types, And Functions
Important definitions are `CN10K_CPT_HW_CTX_SIZE`, `union cn10k_cpt_hw_ctx`, and `struct cn10k_cpt_errata_ctx`. Inline helpers read CN10K or CN9K completion and microcode completion codes from shared `union otx2_cpt_res_s`. Function declarations mirror the CN10K implementation in `cn10k_cpt.c`.

### Control Flow, State, And Persistence
The hardware context union stores the CN10K context header fields persisted in DMA memory for affected devices. The errata context stores both the CPU pointer and tagged DMA CPTR. Completion-code helpers are selected through hardware ops tables and allow common request-manager code to parse different result layouts.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on common, PF, and VF OcteonTX2 structures plus CN9K/CN10K result structs from hardware-type headers. Risks include casting a shared result union to the wrong generation-specific layout, context-size bitfield limits, and the stale closing comment name. Test signals include compile coverage for common/PF/VF objects, CN9K versus CN10K completion-code parsing, errata context setup, and namespace-export consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/cn10k_cpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_common.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_common.h

### Purpose
`otx2_cpt_common.h` centralizes OcteonTX2/CN10K CPT shared constants, AF/RVU addressing helpers, capability flags, PF/VF mailbox message structures, engine capability formats, device-generation predicates, feature gates, and common mailbox function declarations.

### Important APIs, Types, And Functions
Important constants include max VF count, RVU function address macro, invalid group, DMA alignment, CN10K capability bit indices, engine types, and private mailbox message IDs. It defines inline `otx2_cpt_write64()` / `otx2_cpt_read64()`, generation predicates (`is_dev_otx2()`, `is_dev_cn10ka()`, `is_dev_cn10ka_ax()`, `is_dev_cn10kb()`, `is_dev_cn10ka_b0()`), `otx2_cpt_set_hw_caps()`, errata and SGV2 feature gates, mailbox request/response structs for inline IPsec LF config, engine group lookup, kernel VF limits, and capabilities, plus declarations for AF register and LF resource mailbox helpers.

### Control Flow, State, And Persistence
The header has mostly inline logic. Runtime code uses the device predicates at probe to set capability bits and choose CN10K mailbox/LMTST behavior, errata workarounds, and SG format. Read/write helpers compute RVU block/slot offsets over a mapped register base. Mailbox structs persist request payload layouts exchanged between PF, VF, and AF.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on PCI, crypto, devlink, OcteonTX2 hardware types, `rvu.h`, and `mbox.h` from the AF networking driver. Risks include subsystem/revision checks going stale, capability bits being inverted for non-OTX2 devices, private mailbox IDs colliding with AF range assumptions, and register offset macro misuse. Test signals include PF/VF probes across OTX2/CN10KA/CN10KB, capability replies, kernel VF limit mailbox, SGV2 feature selection, errata 38550 path, AF register read/write helpers, and include-path build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.c -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.c

### Purpose
`otx2_cpt_devlink.c` exposes OcteonTX2 CPT PF runtime controls and firmware-version reporting through devlink. It lets users create/delete custom engine groups, toggle a hardware `t106_mode` bit when safe, and report running AE/SE/IE microcode versions.

### Important APIs, Types, And Functions
Public APIs are `otx2_cpt_register_dl()` and `otx2_cpt_unregister_dl()`. Devlink parameter handlers include `otx2_cpt_dl_egrp_create()`, `otx2_cpt_dl_egrp_delete()`, `otx2_cpt_dl_uc_info()`, `otx2_cpt_dl_t106_mode_get()`, and `otx2_cpt_dl_t106_mode_set()`. Info reporting uses `otx2_cpt_dl_info_firmware_version_put()` and `otx2_cpt_devlink_info_get()`. Driver params are `egrp_create`, `egrp_delete`, and `t106_mode`.

### Control Flow, State, And Persistence
Registration allocates a devlink instance with private `struct otx2_cpt_devlink`, links it to the PF state, registers driver params, and registers the devlink object. Engine-group create/delete params forward string contexts to PF microcode helpers. `t106_mode_get` reads `CPT_AF_CTL` through the AF/PF mailbox; `set` refuses changes when VFs are enabled or engine groups exist, then updates bit 18 only on devices with SGV2 support. Info-get scans engine groups for reserved engines of each type and emits running firmware versions as `fw.ae`, `fw.se`, and `fw.ie`. Unregister reverses devlink and parameter registration.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on devlink, PF state, PF microcode helpers, AF register mailbox functions, engine group data, and SGV2 feature gating. Risks include devlink parameter side effects using string set operations, missing extack messages on failures, reading AF registers without checking return in get, ensuring `t106_mode` is immutable once VFs/groups exist, and firmware-version reporting when groups are mirrored or absent. Test signals include devlink param registration, create/delete custom groups, t106 get/set before and after VF enable, devlink info reporting with AE/SE/IE firmware, register failure injection, and unregister on PF remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.h

### Purpose
`otx2_cpt_devlink.h` declares the small devlink integration surface for the OcteonTX2 CPT PF driver.

### Important APIs, Types, And Functions
`struct otx2_cpt_devlink` stores the devlink handle and owning `struct otx2_cptpf_dev`. It declares `otx2_cpt_register_dl()` and `otx2_cpt_unregister_dl()`.

### Control Flow, State, And Persistence
The PF driver creates a devlink object during probe/setup and stores the pointer in PF state; unregister consumes the same PF pointer during teardown. The private struct ties devlink callbacks back to the PF's engine-group and AF mailbox state.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on common CPT definitions and PF state. Risks are mostly lifetime-related: callbacks must not outlive the PF and `cptpf->dl` must be cleared or treated carefully by teardown code. Test signals include PF probe/remove with devlink enabled, devlink command execution after registration, and no callbacks after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cpt_devlink.h -->
