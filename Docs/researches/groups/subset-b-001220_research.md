# subset-b-001220 research

This grouped report covers CAAM scatter/gather and register helpers plus Cavium Thunder CPT and NITROX crypto accelerator driver components. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/regs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/regs.h

Purpose: defines the register-level ABI for the Freescale/NXP CAAM block, including endian-aware MMIO helpers, DMA pointer conversions, job-ring entry layouts, and typed register overlays for controller, job ring, queue interface, RNG, RTIC, assurance, and DECO blocks.

Important APIs and types: exported globals `caam_little_end`, `caam_imx`, and `caam_ptr_sz` drive `caam{16,32,64}_to_cpu()`, `cpu_to_caam{16,32,64}()`, `wr_reg32()`, `rd_reg32()`, `wr_reg64()`, `rd_reg64()`, `cpu_to_caam_dma*()`, and `caam_dma*_to_cpu()`. Job-ring helpers `jr_outentry_get()`, `jr_outentry_desc()`, `jr_outentry_jrstatus()`, and `jr_inpentry_set()` abstract 32-bit versus 64-bit descriptor pointers. Major register structs include `version_regs`, `caam_perfmon`, `caam_ctrl`, `caam_job_ring`, `caam_queue_if`, and `caam_deco`, with many `JRSTA_*`, `JRINT_*`, `MCFGR_*`, `QICTL_*`, and RNG test masks.

Control flow and state: this header owns no allocator or persistent software state; it fixes how other CAAM files read and write persistent hardware state. The most delicate flow is 64-bit register access: big-endian and non-i.MX little-endian use native 64-bit helpers, while i.MX little-endian manually orders 32-bit halves because CAAM DMA-address registers are wired differently.

Dependencies and integration points: depends on Linux MMIO, endian, bitops, DMA-address-width configuration, and CAAM probe code that initializes the globals before users touch registers. Job ring, queue interface, RNG, blob, and descriptor debugging code consume these layouts directly.

Risks and test signals: risks include wrong global endian/platform detection corrupting register or DMA pointer programming, 32-bit/64-bit pointer-size mismatches in job rings, non-atomic 64-bit access races if used outside documented hardware semantics, and register-struct drift versus silicon revisions. Test signals include CAAM probe detecting correct endian mode, job rings handling both 32-bit and 64-bit DMA pointers, i.MX DMA addresses mapping correctly, reset and interrupt status bits decoding correctly, and RNG/job failure paths reporting expected `JRSTA_*` sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_qm.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_qm.h

Purpose: converts Linux DMA-mapped scatterlists into DPAA/QMan `struct qm_sg_entry` link-table entries used by CAAM queue-interface paths.

Important APIs: `__dma_to_qm_sg()` writes the DMA address, clears buffer-pool metadata, and stores an offset with `QM_SG_OFF_MASK`. `dma_to_qm_sg_one()`, `_last()`, `_ext()`, and `_last_ext()` build normal, final, extension, and final-extension entries. `sg_to_qm_sg()` walks a scatterlist for a requested byte length and returns the last generated entry; `sg_to_qm_sg_last()` then marks that entry final.

Control flow and state: the conversion loop repeatedly takes `min(sg_dma_len(sg), len)`, emits one hardware entry, advances `sg_next()`, and decrements the remaining length. No persistent state is kept; the caller owns DMA mapping, output table storage, and final hardware submission.

Dependencies and integration points: depends on `<soc/fsl/qman.h>`, `regs.h`, QMan byte-order helpers, Linux scatterlist DMA APIs, and CAAM QI users that include a hardware link table in frame descriptors.

Risks and test signals: risks include passing an unmapped or too-short scatterlist, output table under-allocation, offset truncation, and no explicit null guard if `len` exceeds the SG chain. Test signals include QMan SG entries with correct final/extension flags, exact byte coverage for partial last segments, and successful CAAM queue-interface requests with multi-entry input and output buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_qm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_qm2.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_qm2.h

Purpose: provides the DPAA2 variant of CAAM scatterlist-to-hardware scatter/gather conversion using `struct dpaa2_sg_entry`.

Important APIs: `dma_to_qm_sg_one()` programs address, single-entry format, non-final flag, length, BPID zero, and offset through DPAA2 accessors. `sg_to_qm_sg()` converts a mapped Linux scatterlist into a sequence of DPAA2 SG entries, and `sg_to_qm_sg_last()` sets the final bit on the last produced entry.

Control flow and state: the loop is the same contract as the DPAA1 helper: consume the requested byte count from `sg_dma_len()` chunks and return the last populated entry. The header stores no state; hardware-visible state is only the caller-provided SG table.

Dependencies and integration points: depends on `<soc/fsl/dpaa2-fd.h>` and Linux scatterlist DMA fields. It is also included by `sg_sw_sec4.h`, where DPAA2 CAAM can alias SEC4 entries onto DPAA2 SG entries when `caam_dpaa2` is active.

Risks and test signals: risks are incorrect final-bit handling, caller-provided offset semantics differing between DPAA2 and SEC4, table overflow, and undefined behavior if the SG chain ends before `len`. Test signals include DPAA2 frame descriptors completing with multi-segment data, final flag set only on the last entry, and matching lengths on requests split across several SG segments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_qm2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_sec4.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_sec4.h

Purpose: builds SEC4-format scatter/gather entries for CAAM descriptors, with a runtime branch that emits DPAA2 SG entries on DPAA2 CAAM platforms.

Important APIs and types: `struct sec4_sg_entry` is the classic CAAM table entry containing a pointer, length, and BPID/offset word. `dma_to_sec4_sg_one()` emits either a DPAA2 entry via `dma_to_qm_sg_one()` or a SEC4 entry using `cpu_to_caam_dma64()` and `cpu_to_caam32()`. `sg_to_sec4_sg()`, `sg_to_sec4_set_last()`, and `sg_to_sec4_sg_last()` convert full scatterlists and mark the final entry.

Control flow and state: conversion consumes mapped scatterlist DMA addresses until `len` is exhausted. State is caller-owned output memory plus the global `caam_dpaa2` platform flag and CAAM endian/DMA conversion state from `regs.h`.

Dependencies and integration points: depends on `ctrl.h`, `regs.h`, DPAA2 FD helpers, Linux scatterlists, and descriptor-building code for CAAM symmetric/hash/AEAD operations.

Risks and test signals: risks include ABI aliasing between SEC4 and DPAA2 entries, missed final-bit conversion, wrong DMA-endian conversion on i.MX or 32-bit platforms, debug hex dumps exposing excessive log noise, and no SG-chain bounds check. Test signals include SEC4 and DPAA2 requests completing with identical buffer contents, final-entry bit validation, and successful partial-length conversions over longer scatterlists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_sec4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/Makefile

Purpose: selects Cavium crypto accelerator subdirectories for the kernel build.

Important APIs and control flow: `obj-$(CONFIG_CRYPTO_DEV_CPT) += cpt/` descends into the Thunder CPT PF/VF driver, and `obj-$(CONFIG_CRYPTO_DEV_NITROX) += nitrox/` descends into the CNN55XX NITROX driver. There is no runtime code or state.

Dependencies and integration points: depends on Kconfig symbols produced by child Kconfig files and the parent crypto driver build. It is the top-level integration point for Cavium accelerator objects under `drivers/crypto`.

Risks and test signals: risks are limited to symbol mismatch or stale child directory selection. Test signals are `CONFIG_CRYPTO_DEV_CPT` and `CONFIG_CRYPTO_DEV_NITROX` builds entering the correct subdirectories and disabled configurations producing no Cavium crypto objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/Kconfig

Purpose: defines configuration symbols for the Cavium Thunder CPT cryptographic accelerator driver.

Important APIs and control flow: hidden `CRYPTO_DEV_CPT` is selected by user-visible `CAVIUM_CPT`. `CAVIUM_CPT` is a tristate prompt gated by `ARCH_THUNDER || COMPILE_TEST`, `PCI_MSI`, and `64BIT`; selecting it enables compilation of the PF/VF driver modules.

State and dependencies: Kconfig has no runtime state. It declares platform, MSI-X, and 64-bit assumptions used by the driver’s 48-bit DMA, PCI SR-IOV, and MMIO code.

Integration points: integrates with the kernel crypto hardware menu and the CPT Makefile through `CONFIG_CAVIUM_CPT`.

Risks and test signals: risks include compile-test coverage without real Thunder hardware and missing crypto algorithm selects in this Kconfig, because algorithm dependencies are pulled by source includes or parent configs. Test signals include allmodconfig/allyesconfig builds, ARCH_THUNDER builds, and disabled PCI_MSI/32-bit configs hiding the prompt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/Makefile

Purpose: builds the Thunder CPT PF and VF composite objects.

Important APIs and control flow: `obj-$(CONFIG_CAVIUM_CPT) += cptpf.o cptvf.o` emits two modules or built-in objects. `cptpf-objs` links `cptpf_main.o` and `cptpf_mbox.o`; `cptvf-objs` links VF PCI setup, request manager, mailbox, and crypto algorithm registration files.

State and dependencies: no runtime state; it fixes link boundaries so PF and VF PCI drivers register separately but share common headers.

Integration points: selected by `CONFIG_CAVIUM_CPT`, with PF matching PCI device `0xa040` and VF matching `0xa041`.

Risks and test signals: risks include unresolved symbols if object membership drifts and missing algorithm support if `cptvf_algs.o` is omitted. Test signals are successful module link, separate `thunder-cpt` and `thunder-cptvf` PCI driver registration, and crypto algorithms appearing only when VF support initializes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cpt_common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cpt_common.h

Purpose: provides common Thunder CPT PF/VF constants, register address macros, mailbox opcodes, state flags, and 64-bit CSR accessors.

Important APIs and types: device IDs `CPT_81XX_PCI_PF_DEVICE_ID` and `CPT_81XX_PCI_VF_DEVICE_ID`, flags `CPT_FLAG_SRIOV_ENABLED`, `CPT_FLAG_VF_DRIVER`, and `CPT_FLAG_DEVICE_READY`, mailbox opcodes `CPT_MSG_*`, `struct cpt_mbox`, and `cpt_write_csr64()`/`cpt_read_csr64()`. Register macros cover PF global, mailbox, engine, queue, and VF queue spaces such as `CPTX_PF_QX_CTL()`, `CPTX_PF_VFX_MBOXX()`, `CPTX_VQX_*()`, and `CPTX_VFX_PF_MBOXX()`.

Control flow and state: this is a header-only ABI layer; state lives in hardware registers and in PF/VF structs. Register offsets encode CPT instance, queue/VF indices, and mailbox words.

Dependencies and integration points: depends on PCI, delay, byteorder, and `cpt_hw_types.h` bitfield overlays. Every CPT PF/VF source includes it for CSR and mailbox access.

Risks and test signals: risks include incorrect offset arithmetic causing PF/VF register aliasing, W1C/W1S misuse by callers, and flag checks being non-atomic. Test signals include mailbox round trips, PF queue programming visible to VFs, CSR reads matching hardware documentation, and no register access outside mapped BAR0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cpt_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cpt_hw_types.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cpt_hw_types.h

Purpose: describes the Thunder CPT instruction, result, and control/status register bit layouts used by PF and VF code.

Important APIs and types: `enum cpt_comp_e` defines completion codes. `union cpt_inst_s` is the 8-word hardware instruction, `union cpt_res_s` is the 16-byte completion record, and `union cptx_pf_*`/`union cptx_vqx_*` overlays BIST, constants, PF queue control, VF queue base, interrupt, doorbell, done count, coalescing, and enable registers.

Control flow and state: no functions run here; callers fill bitfields before `cpt_write_csr64()` or interpret values after `cpt_read_csr64()` and DMA completion writes. Endian-specific bitfield layouts are guarded by `__BIG_ENDIAN_BITFIELD`.

Dependencies and integration points: consumed by PF initialization, mailbox queue binding, VF queue setup, request submission, and interrupt handlers. It must align with the hardware little-endian instruction/result format unless queue control selects big-endian behavior.

Risks and test signals: risks include C bitfield layout dependency, accidental inclusion cycle with `cpt_common.h`, queue-control changes while inflight, and completion-code polling against stale DMA memory. Test signals include correct BIST and constants decoding, queue doorbell counts in multiples of 8 words, completion records changing from `NOTDONE` to `GOOD/FAULT/SWERR`, and builds on both endian configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cpt_hw_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf.h

Purpose: declares PF-side Thunder CPT device state, microcode metadata, VF bookkeeping, sizing limits, and mailbox handler entry point.

Important APIs and types: constants cover core groups, SE/AE core counts, maximum VFs, MSI-X vector mapping, and microcode version length. `struct microcode` tracks AE/SE firmware validity, group, core mask, DMA backing, and version. `struct cpt_vf_info` tracks VF state, priority, ID, and queue length. `struct cpt_device` stores flags, VF array, BAR mapping, PCI device, loaded microcode array, group index, and detected SE/AE core counts.

Control flow and state: persistent state is per-PF and mirrors hardware resources: loaded firmware groups, enabled core masks, and SR-IOV VF configuration. `cpt_mbox_intr_handler()` is exported to `cptpf_main.c` IRQ handling.

Dependencies and integration points: depends on `cpt_common.h`, PF main code, and PF mailbox code. It is the contract between PCI probe/remove, firmware loading, and VF mailbox requests.

Risks and test signals: risks include fixed core/VF limits drifting from hardware, loaded microcode state needing to match group programming, and non-atomic VF state updates from IRQ context. Test signals include firmware group allocation, VF queue binding to valid groups, SR-IOV enable count capping, and clean microcode DMA free on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf_main.c

Purpose: implements the Thunder CPT physical-function PCI driver, including reset, BIST checks, microcode loading, core-group programming, PF interrupts, SR-IOV enablement, and remove/shutdown cleanup.

Important APIs and control flow: `cpt_probe()` enables PCI, maps BAR0, sets a 48-bit DMA mask, initializes hardware through `cpt_device_init()`, registers mailbox MSI-X, loads `cpt8x-mc-ae.out` and `cpt8x-mc-se.out`, and enables SR-IOV. `cpt_ucode_load_fw()` requests firmware, allocates coherent DMA, byte-swaps microcode, and calls `do_cpt_init()`. `do_cpt_init()` disables interrupts, assigns a microcode group, programs `ENGX_UCODE_BASE`, group masks, and core enables, then marks the PF ready. Remove disables cores, unloads microcode, unregisters interrupts, disables SR-IOV, and releases PCI resources.

State and persistence: state is `struct cpt_device`, hardware reset state, loaded coherent firmware buffers, engine group masks, and SR-IOV VF enablement. Hardware firmware and core enables persist until removed or reset.

Dependencies and integration points: depends on Linux PCI, firmware loader, MSI-X, DMA coherent allocation, `cptpf_mbox.c`, and CPT CSR/bitfield headers. VFs cannot initialize until firmware groups and PF mailboxes are ready.

Risks and test signals: risks include `GENMASK(num_cores, 0)` enabling one more bit than a count-style name suggests, duplicated/unbraced `cpt->num_vf_en = total_vf_cnt`, error paths after VF software init not always cleaning VF queues, and firmware byte-swap assumptions. Test signals include BIST pass, firmware load messages, PF mailbox IRQ delivery, SR-IOV VFs appearing, VF group binding, and remove freeing all coherent microcode buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf_mbox.c

Purpose: handles PF-side mailbox protocol for Thunder CPT VFs, translating VF requests into queue length, group binding, priority, and lifecycle state changes.

Important APIs and control flow: `cpt_mbox_intr_handler()` reads pending VF bits from `CPTX_PF_MBOX_INTX`, calls `cpt_handle_mbox_intr()` per VF, and clears each bit. The handler reads mailbox words, handles `CPT_MSG_VF_UP`, `READY`, `VF_DOWN`, `QLEN`, `QBIND_GRP`, and `VQ_PRIORITY`, and responds through `cpt_send_msg_to_vf()` or `cpt_mbox_send_ack()`. Helpers program PF queue control fields through `cpt_cfg_qlen_for_vf()`, `cpt_cfg_vq_priority()`, and `cpt_bind_vq_to_grp()`.

State and persistence: updates `cpt->vfinfo[]` and PF queue registers. `try_module_get()` and `module_put()` pin the PF module while VFs are up.

Dependencies and integration points: depends on PF microcode group state from `cptpf_main.c`, CPT queue control bitfields, and VF mailbox code waiting for ACKs.

Risks and test signals: risks include no explicit NACK for invalid default messages, VF number loops across maximum rather than enabled VF count, unprotected VF state updates, and queue binding failure leaving VF waiters without a typed response. Test signals include READY returning VF ID, QLEN changing PF queue size, group binding returning AE/SE type, priority programming, and module refcount balancing after VF down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptpf_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf.h

Purpose: declares VF-side Thunder CPT state, command/pending queue layouts, interrupt constants, DMA modes, mailbox function prototypes, and crypto/request integration hooks.

Important APIs and types: constants define default command queue length/chunking, timeout, MSI-X vector count, interrupt masks, and DMA modes. `struct command_chunk`, `command_queue`, and `command_qinfo` describe circular coherent instruction chunks. `struct pending_entry`, `pending_queue`, and `pending_qinfo` track submitted requests and completions. `struct cpt_vf` stores PCI/BAR state, VF identity/type/group, queue resources, IRQ affinity masks, and mailbox ACK flags.

Control flow and state: the VF driver allocates command queues, pending queues, tasklets, and MSI-X vectors, then transitions to device-ready after PF mailbox negotiation and VQ programming. Pending entries persist until request completion or timeout cleanup.

Dependencies and integration points: shared by VF main, mailbox, request manager, and crypto algorithm files. It depends on `cpt_common.h`, Linux lists, PCI, DMA, and tasklet/IRQ code.

Risks and test signals: risks include fixed one-queue-per-VF assumptions, typo-prone mailbox ACK booleans without locking, pending queue wrap-around bugs, and cleanup needing to quiesce tasklets before queue memory free. Test signals include VF probe, two MSI-X handlers registered, PF negotiation setting `vfid` and `vftype`, queue doorbells incrementing, and request completions draining pending entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_algs.c

Purpose: registers Linux skcipher algorithms backed by the CPT VF SE engine and translates skcipher requests into CPT flexi-crypto requests.

Important APIs and control flow: `cvm_encrypt()` and `cvm_decrypt()` call `cvm_enc_dec()`, which initializes request context, builds input/output buffer lists, stores callback data, selects a VF handle by `smp_processor_id()`, and submits through `cptvf_do_request()`. Setkey handlers validate AES, XTS, and 3DES keys and populate `struct cvm_enc_ctx`. `cvm_crypto_init()` adds a VF to a global device array and registers algorithms when `dev_count == 3`; `cvm_crypto_exit()` unregisters when the last device exits. Algorithms include `xts(aes)`, `cbc(aes)`, `ecb(aes)`, `cbc(des3_ede)`, and `ecb(des3_ede)`.

State and persistence: per-transform state is key/cipher metadata in the crypto context; per-request state is DMA-capable request context; global state is `dev_handle`.

Dependencies and integration points: depends on crypto skcipher API, AES/XTS/DES helpers, scatterlists, `cptvf_algs.h`, and request manager submission.

Risks and test signals: risks include direct `sg_virt()` use, global device selection by CPU without bounds against `dev_count`, algorithm registration hard-coded to the fourth VF, and 3DES context type differing from AES while common setkey writes `cvm_enc_ctx`. Test signals include `cryptomgr` self-tests for all registered modes, request completion callback status handling, XTS key verification, and multi-VF hotplug/unload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_algs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_algs.h

Purpose: defines CPT VF crypto algorithm constants, flexi-crypto control bitfields, key/context structures, and the VF request submission prototype.

Important APIs and types: `MAJOR_OP_FC`, `DMA_MODE_FLAG()`, `enum req_type`, `enum cipher_type`, and `enum aes_type` encode microcode request selections. `union encr_ctrl` is the hardware flexi-crypto encryption control word. `struct enc_context`, `fchmac_context`, and `fc_context` form the context passed to firmware. `struct cvm_enc_ctx`, `cvm_des3_ctx`, and `cvm_req_ctx` are Linux crypto transform/request-private contexts.

Control flow and state: the header has no executable flow but fixes the binary layout that `cptvf_algs.c` copies into input lists and `cptvf_reqmanager.c` DMA maps to hardware.

Dependencies and integration points: depends on `request_manager.h` and indirectly on CPT common hardware structures. Crypto algorithm callbacks and request manager share these structures.

Risks and test signals: risks include endian-sensitive bitfield layout, fixed key offsets such as `KEY2_OFFSET`, mismatch between DES3 and AES context structs, and not covering all declared cipher enum values. Test signals include correct control-word bytes in DMA input, AES key-length encoding, XTS key placement, and firmware accepting generated flexi-crypto contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_algs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_main.c

Purpose: implements the Thunder CPT virtual-function PCI driver, including queue allocation, MSI-X setup, PF mailbox negotiation, hardware queue programming, interrupt handling, tasklet completion processing, and crypto algorithm initialization.

Important APIs and control flow: `cptvf_probe()` enables PCI, maps BAR0, allocates two MSI-X vectors, enables mailbox/software-error interrupts, checks PF readiness, allocates command/pending queues and tasklets, sends QLEN/group/priority mailbox messages, registers DONE IRQ, sends VF_UP, and calls `cvm_crypto_init()`. Queue helpers allocate circular coherent command chunks and pending arrays. `cptvf_device_init()` disables the VQ, clears doorbell/inflight, writes queue base, sets coalescing, enables the VQ, and marks ready. Misc and done IRQ handlers clear errors, handle mailbox messages, ACK done counts, and schedule response tasklets.

State and persistence: per-VF persistent state includes coherent command rings, pending queues, tasklets, IRQ affinity masks, PF-negotiated VF identity/type, VQ registers, and crypto registration reference state.

Dependencies and integration points: depends on PCI/MSI-X, DMA coherent memory, PF mailbox protocol, request manager `vq_post_process()`, and crypto algorithm registration.

Risks and test signals: risks include cleanup labels after mid-probe failures not always freeing software queues or DONE IRQ state, duplicated `return NULL` line in WQE lookup, no inflight drain on remove, and fixed VF group/priority values. Test signals include VF probe after PF SR-IOV enable, mailbox ACKs, queue base alignment, DONE interrupts scheduling tasklets, crypto self-tests completing, and remove sending VF_DOWN and freeing queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_mbox.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_mbox.c

Purpose: implements VF-side synchronous mailbox communication with the CPT PF.

Important APIs and control flow: `cptvf_send_msg_to_pf()` writes mailbox words to trigger a PF interrupt. `cptvf_handle_mbox_intr()` reads PF responses and updates `pf_acked`, `pf_nacked`, `vfid`, and `vftype`. `cptvf_send_msg_to_pf_timeout()` sends a message then polls up to `CPT_MBOX_MSG_TIMEOUT`, returning `-EINVAL` on NACK and `-EBUSY` on timeout. Public wrappers send READY, QLEN, group binding, priority, VF_UP, and VF_DOWN messages.

State and persistence: mailbox state is two booleans and negotiated VF identity/type in `struct cpt_vf`; persistent hardware state is PF-programmed queue config in response to messages.

Dependencies and integration points: used by `cptvf_main.c` during probe/remove and by the misc interrupt handler for responses. It depends on PF response behavior from `cptpf_mbox.c`.

Risks and test signals: risks include polling shared ACK flags without locks or completions, fixed 10 ms sleep granularity, ambiguous error logging labels, and possible stale ACK if interrupts are delayed around consecutive messages. Test signals include PF READY returning VF ID, group binding returning SE/AE type, timeout behavior when PF is absent, and orderly VF_DOWN on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_reqmanager.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_reqmanager.c

Purpose: converts high-level CPT VF crypto requests into DMA scatter/gather tables and hardware instructions, posts them to a VF command queue, and reaps completions from pending queues.

Important APIs and control flow: `process_request()` allocates `struct cpt_info_buffer`, builds gather/scatter lists through `setup_sgio_list()`, maps completion/result buffers, fills `struct cpt_vq_command` and `union cpt_inst_s`, reserves a pending entry, posts through `send_cpt_command()`, and returns asynchronously. `process_pending_queue()` scans pending entries, checks completion codes and timeout windows, cleans DMA resources, and calls request callbacks. `cptvf_do_request()` verifies device readiness and SE/AE type compatibility before submission.

State and persistence: state is coherent command ring contents, pending queue entries, mapped input/output buffers, completion DMA memory, and per-request timeout metadata. Hardware advances doorbells and writes completion structures.

Dependencies and integration points: depends on VF queue setup in `cptvf_main.c`, crypto request structures in `cptvf_algs.h`, CPT instruction/result layouts, Linux DMA mapping, jiffies, and callbacks into the crypto API.

Risks and test signals: risks include a cleanup bug unmapping `list[i]` instead of `list[j]` after partial DMA-map failure, callbacks called after `pentry` fields are cleared, possible busy queue deadlocks under lock nesting, direct DMA mapping of virtual buffers, and timeout handling that may free resources while hardware later writes completion. Test signals include multi-buffer SG map/unmap balance, pending threshold draining, fault/SWERR completion cleanup, request timeout tests, and crypto self-tests under queue pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/cptvf_reqmanager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/request_manager.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/request_manager.h

Purpose: declares the software request, scatter/gather component, completion-buffer, and command-word structures shared by CPT VF algorithm code and the request manager.

Important APIs and types: constants define completion-code size, pending threshold, maximum SG counts, SG header size, and buffer count. `union ctrl_info` carries group, DMA mode, and SE/AE request type. `union opcode_info`, `struct cptvf_request`, `buf_ptr`, and `cpt_request_info` describe caller-visible requests. `struct sglist_component`, `cpt_info_buffer`, `vq_cmd_word0`, `vq_cmd_word3`, and `cpt_vq_command` describe DMA tables and hardware EI words.

Control flow and state: no functions execute here except declarations for `vq_post_process()` and `process_request()`. The layout controls how `cptvf_reqmanager.c` builds DPTR/RPTR/CPTR data.

Dependencies and integration points: depends on `cpt_common.h`, CPT VF queue code, and crypto algorithm request assembly.

Risks and test signals: risks include endian-sensitive bitfields, hard-coded maximum SG counts lower than some scatterwalk outputs, and `volatile` completion pointers not replacing proper DMA synchronization. Test signals include SG component byte order, control-word group/type matching PF queue binding, max-SG rejection behavior, and completion buffer alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/request_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/Kconfig

Purpose: defines Kconfig symbols for Cavium/Marvell NITROX CNN55XX crypto accelerator support.

Important APIs and control flow: hidden `CRYPTO_DEV_NITROX` selects core crypto dependencies `CRYPTO_SKCIPHER`, `CRYPTO_AES`, `CRYPTO_LIB_DES`, and `FW_LOADER`. User-visible `CRYPTO_DEV_NITROX_CNN55XX` is a tristate requiring `PCI_MSI && 64BIT` and selecting the hidden symbol.

State and dependencies: Kconfig has no runtime state; it encodes assumptions used by driver PCI, MSI-X, firmware, and DMA code.

Integration points: selected symbol drives the `nitrox/Makefile` to build `n5pf`.

Risks and test signals: risks include missing explicit `PCI` dependency if inherited elsewhere is absent, and no prompt gating on actual platform family. Test signals include build visibility only with 64-bit MSI-capable configs, firmware loader availability, and crypto dependencies enabled for skcipher and AEAD algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/Makefile

Purpose: links the NITROX CNN55XX PF driver composite object.

Important APIs and control flow: `obj-$(CONFIG_CRYPTO_DEV_NITROX_CNN55XX) += n5pf.o` builds the driver. Core members include main PCI code, ISR, lib, HAL, request manager, algorithm registration, mailbox, skcipher, and AEAD. `nitrox_sriov.o` is conditional on `CONFIG_PCI_IOV`; `nitrox_debugfs.o` is conditional on `CONFIG_DEBUG_FS`.

State and dependencies: no runtime state; object membership controls which exported helpers exist for SR-IOV and debugfs paths.

Integration points: links the module named `n5pf`, matching Kconfig help.

Risks and test signals: risks include optional SR-IOV/debugfs symbols needing stub headers and object omission causing unresolved references. Test signals include links with PCI_IOV on/off, DEBUG_FS on/off, and module exposing both skcipher and AEAD registrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_aead.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_aead.c

Purpose: implements NITROX AEAD algorithms for `gcm(aes)` and `rfc4106(gcm(aes))`, translating Linux AEAD requests into SE flexi-crypto requests.

Important APIs and control flow: setkey/authsize callbacks populate `struct flexi_crypto_context`. `nitrox_aes_gcm_enc()` and `_dec()` validate AAD length, set salt/IV pointers, compute source/destination lengths, allocate SG lists through `nitrox_set_creq()`, and submit via `nitrox_process_se_request()`. RFC4106 paths reshape associated data and payload scatterlists with `scatterwalk_ffwd()`, use RFC IV sizing, and complete through `nitrox_rfc4106_callback()`. Init allocates a device context with `nitrox_get_first_device()` and `crypto_alloc_context()`.

State and persistence: per-transform state is a DMA-backed context in the device pool plus a device reference; per-request state includes allocated source/destination SG buffers and a `se_crypto_request` embedded in request context. Hardware writes completion via the request manager.

Dependencies and integration points: depends on crypto AEAD/GCM helpers, scatterwalk, `nitrox_req.h` layouts, common device allocation, and request submission.

Risks and test signals: risks include `nitrox_rfc4106_dec()` using `crypto_aead_ctx_dma(aead)` while other paths use `crypto_aead_ctx()`, strict GCM AAD limit of 512 bytes, resource leaks if `nitrox_set_creq()` fails after destination allocation in RFC paths, and scatterlist chaining subtleties for in-place versus out-of-place requests. Test signals include cryptomgr AEAD self-tests, RFC4106 authsize/key salt validation, large AAD rejection, async completion freeing SG buffers, and transform exit zeroing keys and dropping device references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_algs.c

Purpose: provides the aggregate crypto algorithm registration entry points for the NITROX driver.

Important APIs and control flow: `nitrox_crypto_register()` first calls `nitrox_register_skciphers()`, then `nitrox_register_aeads()`, unregistering skciphers if AEAD registration fails. `nitrox_crypto_unregister()` unregisters AEADs before skciphers.

State and persistence: no independent state; it coordinates global algorithm registration state held by the Linux crypto API.

Dependencies and integration points: depends on `nitrox_common.h`, `nitrox_skcipher.c`, and `nitrox_aead.c`. Main driver code calls these once devices are available and removes them during teardown.

Risks and test signals: risks include global registration while no usable device exists if caller ordering is wrong, and unregister ordering assumptions if partial registration changes. Test signals include algorithm list entries appearing once, AEAD registration failure rolling back skciphers, and clean removal with active transform references rejected or drained by higher layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_common.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_common.h

Purpose: declares shared NITROX driver interfaces across PCI main, algorithm, request manager, software resource, and device-reference code.

Important APIs: algorithm registration functions, context pool functions `crypto_alloc_context()`/`crypto_free_context()`, device reference helpers `nitrox_get_first_device()`/`nitrox_put_device()`, software init/cleanup, response tasklet `pkt_slc_resp_tasklet()`, request submission `nitrox_process_se_request()`, and backlog work `backlog_qflush_work()`.

Control flow and state: this header has no state but defines the cross-module contract: transforms acquire a device and context, algorithms submit SE requests, interrupts schedule response processing, and backlog work drains queued commands.

Dependencies and integration points: includes `nitrox_dev.h` and `nitrox_req.h`, so it couples public helpers to both device and request layouts. It is the common include for HAL/lib/ISR/algorithm modules.

Risks and test signals: risks include broad include coupling, exported request-manager helpers requiring matching object membership, and callers needing clear lifetime/refcount ordering. Test signals include successful module link, algorithm init acquiring devices only when ready, and interrupt tasklets resolving to request-manager response processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_csr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_csr.h

Purpose: defines the NITROX CNN55XX CSR address map and bitfield overlays for engine clusters, microcode loader, AQM queues, NPS packet/core units, POM/BMI/BMO/EFL/LBC, reset/fuse registers, and interrupt status/enable registers.

Important APIs and types: register macros include EMU, UCD, AQM/AQMQ, NPS_CORE, NPS_PKT input/solicit/mailbox, POM, BMI, EFL, BMO, LBC, `RST_BOOT`, and `FUS_DAT1`. Union overlays include queue doorbells/sizes/completions/enables, fuse maps, core enables, interrupt masks, NPS packet counters, NPS core active/status, mailbox interrupt state, RNG, BMI/BMO/POM/LBC controls, invalidation status, reset boot frequency, and fuse data.

Control flow and state: no executable code; the header maps persistent hardware state into C fields consumed by HAL, ISR, SR-IOV, mailbox, and request manager code. Endian-specific bitfields control how values are assembled for `readq()`/`writeq()`.

Dependencies and integration points: depends on Linux types and byteorder. HAL uses it to initialize hardware units, ISR uses it to clear errors and re-enable rings, and debug/device info code uses fuse and reset fields.

Risks and test signals: risks include bitfield layout portability, register-offset drift across NITROX revisions, W1C/W1S fields being accessed with read-modify-write where write-only semantics matter, and large all-ones interrupt enables exposing noisy error storms. Test signals include hardware info decoding, queue enable/doorbell programming, NPS interrupt clearing, LBC invalidation completion, mailbox interrupt bits, and builds on endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_debugfs.c

Purpose: exposes NITROX firmware, device, and request-statistics information through debugfs.

Important APIs and control flow: `firmware_show()` prints two firmware version strings; `device_show()` prints device index, part name, frequency, IDs, revision, and core counts; `stats_show()` prints posted/completed/dropped counters. `nitrox_debugfs_init()` creates a top-level directory named `KBUILD_MODNAME` and files `firmware`, `device`, and `stats`; `nitrox_debugfs_exit()` removes the tree.

State and persistence: debugfs files read live fields from `struct nitrox_device`; no extra persistent state beyond `ndev->debugfs_dir`.

Dependencies and integration points: depends on debugfs, seq_file, `nitrox_dev.h`, and hardware info/stats populated elsewhere.

Risks and test signals: risks include one top-level directory name per device causing collisions on multiple devices, ignoring debugfs creation errors, and firmware array printing only the first two entries despite larger firmware storage. Test signals include debugfs files present with CONFIG_DEBUG_FS, correct removal on device teardown, stats changing during requests, and behavior with multiple NITROX devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_debugfs.h

Purpose: declares or stubs NITROX debugfs lifecycle helpers.

Important APIs and control flow: when `CONFIG_DEBUG_FS` is enabled, `nitrox_debugfs_init()` and `nitrox_debugfs_exit()` are external functions. Otherwise, static inline no-op stubs preserve caller code without conditional compilation.

State and dependencies: owns no state; it depends on `nitrox_dev.h` for the device type and on build-time `CONFIG_DEBUG_FS`.

Integration points: main PCI/device code can call debugfs init/exit unconditionally.

Risks and test signals: risks are low but include callers assuming debugfs files exist when stubs are compiled. Test signals include builds with DEBUG_FS on/off and teardown paths invoking exit safely in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_dev.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_dev.h

Purpose: defines the central NITROX device model, queue structures, hardware-info structures, SR-IOV mailbox/VF state, device states, and CSR access helpers.

Important APIs and types: `struct nitrox_cmdq` represents command rings with response/backlog lists, doorbell/completion CSR addresses, DMA base, work item, counters, indices, and locks. `struct nitrox_hw`, `nitrox_stats`, `nitrox_q_vector`, `nitrox_vfdev`, `nitrox_iov`, and `nitrox_device` hold hardware identity, statistics, MSI-X vector/tasklet data, VF mailbox state, SR-IOV config, DMA pool, packet/AQM queues, and debugfs state. Inline helpers are `nitrox_read_csr()`, `nitrox_write_csr()`, `nitrox_ready()`, and `nitrox_vfdev_ready()`.

Control flow and state: state persists per PCI device and is mutated by probe, HAL config, request manager, ISR, SR-IOV, and crypto transform reference code.

Dependencies and integration points: depends on DMA, interrupt, PCI, networking-size constants, and all NITROX modules using `struct nitrox_device`.

Risks and test signals: risks include many locks/counters sharing one queue object, refcount/state ordering around device removal, SR-IOV mode changes while queues exist, and direct `readq()`/`writeq()` without accessors for barriers beyond MMIO semantics. Test signals include queue allocation on the correct NUMA node, atomic stats updates, device ready gating, VF state transitions, and no use-after-free with active crypto contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_hal.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_hal.c

Purpose: programs NITROX hardware units after software queues and BAR mappings exist, and extracts hardware identity from fuses/reset registers.

Important APIs and control flow: configuration functions enable EMU SE/AE cores, reset and configure packet input rings and solicit ports, program NPS core PF/VF mode, enable NPS packet/core interrupts, configure AQM rings and interrupt enables, set POM/BMI/BMO thresholds, enable RNG, enable EFL and LBC interrupts, invalidate LBC, and toggle PF-to-VF mailbox interrupts. `nitrox_get_hwinfo()` computes frequency, enabled core counts, ZIP availability, and part name.

State and persistence: writes persistent hardware registers for rings, queues, interrupts, core enables, LBC cache state, RNG, and SR-IOV mode. It reads fuse/reset state into `ndev->hw`.

Dependencies and integration points: depends on `nitrox_csr.h`, `nitrox_dev.h`, queue DMA addresses from `nitrox_lib.c`, ISR recovery helpers, and SR-IOV code for mode/mailbox changes.

Risks and test signals: risks include bounded polling that does not report timeout failure, enabling all fused-off cores before relying on fuse counts, all-ones interrupt masks, and queue reconfiguration without external quiesce guarantees. Test signals include rings becoming enabled, doorbell/count registers reset, interrupts firing on completions/errors, LBC invalidation done bit, RNG enabled, and debugfs part name/frequency matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_hal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_hal.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_hal.h

Purpose: declares the NITROX hardware-configuration and recovery helpers implemented by `nitrox_hal.c`.

Important APIs: exported declarations cover AQM rings/unit, EMU, packet input rings, packet solicit ports, NPS core/packet, POM, RNG, EFL, BMI, BMO, LBC, LBC invalidation, individual queue/port enable helpers, PF/VF mode programming, hardware info discovery, and PF-to-VF mailbox interrupt enable/disable.

Control flow and state: no state is stored here; it exposes functions that mutate persistent device CSRs and `ndev->hw`.

Dependencies and integration points: included by main device initialization, ISR recovery paths, mailbox/SR-IOV code, and any path needing to re-enable rings after errors.

Risks and test signals: risks include broad public surface making ordering requirements implicit and the misspelling of interrupt helper names elsewhere needing exact prototype matches. Test signals are clean compilation and callers invoking configuration after queue allocation and before request submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_isr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_isr.c

Purpose: registers MSI-X interrupt handlers for NITROX PF queues and non-ring errors/mailboxes, handles completion interrupts, clears hardware error sources, and supports a reduced SR-IOV PF interrupt mode.

Important APIs and control flow: `nitrox_register_interrupts()` allocates all MSI-X vectors, registers per-packet-ring `nps_pkt_slc_isr()` handlers that schedule response tasklets, and registers vector 192 for `nps_core_int_isr()`. The core ISR reads `NPS_CORE_INT_ACTIVE`, clears NPS core/packet/POM/PEM/LBC/EFL/BMI errors, invokes `nitrox_pf2vf_mbox_handler()` on mailbox interrupts, and requests resend. `nitrox_unregister_interrupts()` frees vectors and kills tasklets. SR-IOV register/unregister variants allocate only the non-ring vector.

State and persistence: persistent state is `ndev->qvec`, tasklets, IRQ affinity hints, and hardware interrupt status cleared by W1C writes. Completion tasklets drain response lists in request-manager code.

Dependencies and integration points: depends on PCI MSI-X, `nitrox_hal.h` re-enable helpers, mailbox code, and request manager `pkt_slc_resp_tasklet()`.

Risks and test signals: risks include assuming vector 192 exists in `qvec` allocation, using `get_cpu_mask(num_online_cpus())` for non-ring affinity, empty recovery work for NPS core tasklet, and SR-IOV unregister freeing the same vector in a loop if more than one qvec became valid. Test signals include packet completion IRQ scheduling response processing, error interrupts clearing and re-enabling affected rings/ports, mailbox ISR dispatch, IRQ affinity set/cleared, and clean unregister after partial registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_isr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_isr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_isr.h

Purpose: declares NITROX interrupt registration helpers and the optional SR-IOV configure callback.

Important APIs: `nitrox_register_interrupts()`, `nitrox_unregister_interrupts()`, `nitrox_sriov_register_interupts()`, and `nitrox_sriov_unregister_interrupts()` manage normal and SR-IOV PF interrupt modes. With `CONFIG_PCI_IOV`, `nitrox_sriov_configure()` is external; otherwise an inline stub returns success.

State and dependencies: owns no state, depends on `nitrox_dev.h` and PCI types. It hides `CONFIG_PCI_IOV` from callers.

Integration points: main PCI driver can wire `sriov_configure` and interrupt setup without conditional code.

Risks and test signals: risks include misspelled `interupts` being part of the API, and the no-op SR-IOV stub making enable requests appear successful when IOV support is compiled out if callers do not gate them. Test signals include builds with PCI_IOV on/off and correct function resolution for normal and SR-IOV interrupt modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_isr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_lib.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_lib.c

Purpose: allocates and frees NITROX software resources shared by crypto algorithms and hardware queue submission, including command rings and DMA-backed crypto contexts.

Important APIs and control flow: `nitrox_common_sw_init()` creates the context DMA pool, packet input queues, and AQM queues; cleanup reverses this. `nitrox_cmdq_init()` allocates aligned coherent queue memory, initializes locks/lists/work, counters, and indices. Packet input and AQM queue allocation assign CSR doorbell/completion addresses and instruction sizes. `crypto_alloc_context()` allocates a metadata wrapper and DMA pool object, stores DMA addresses in both wrapper and embedded `ctx_hdr`, and returns a context handle; `crypto_free_context()` releases it.

State and persistence: state is coherent command ring memory, `struct nitrox_cmdq` arrays, DMA pool objects, response/backlog lists, and per-context DMA handles. These resources persist for the device lifetime or crypto transform lifetime.

Dependencies and integration points: depends on DMA coherent allocation, DMA pools, NUMA node allocation, `nitrox_req.h` command sizes, `nitrox_csr.h` offsets, and request-manager backlog work.

Risks and test signals: risks include `nitrox_common_sw_init()` continuing to allocate AQM queues even after packet queue allocation failed unless error flow is read carefully, contexts allocated with GFP_KERNEL only, queue memory alignment relying on pointer arithmetic from DMA address alignment, and pending response/backlog lists needing to be empty before cleanup. Test signals include queue DMA alignment, successful HAL ring programming from allocated addresses, context pool allocation/free under crypto self-tests, and cleanup after partial allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_lib.c -->
