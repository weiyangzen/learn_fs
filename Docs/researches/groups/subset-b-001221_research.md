# subset-b-001221 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_main.c

## Purpose

`nitrox_main.c` is the PCI physical-function entry point for the Cavium CNN55XX Nitrox crypto accelerator. It binds the `CNN55XX` PCI device, performs function-level reset and BAR mapping, initializes software queues/interrupts, programs hardware units, loads SE and AE firmware, registers debugfs and Crypto API algorithms, and exposes `nitrox_get_first_device()`/`nitrox_put_device()` for algorithm front ends to borrow a ready device.

## Important APIs, Types, And Functions

- `nitrox_pci_tbl`, `nitrox_driver`, `module_pci_driver()` define the PCI match/driver object and connect `.probe`, `.remove`, `.shutdown`, and `.sriov_configure`.
- `qlen` is a module parameter controlling packet command queue length; the probed device stores it in `ndev->qlen`.
- `struct ucode` describes the firmware blob header: id, version, big-endian code size, padding, and 64-bit code payload.
- `write_to_ucd_unit()` writes firmware data into a selected UCD microcode load block by programming `UCD_UCODE_LOAD_BLOCK_NUM` and `UCD_UCODE_LOAD_IDX_DATAX()`.
- `nitrox_load_fw()` requests `cavium/cnn55xx_se.fw` and `cavium/cnn55xx_ae.fw`, validates firmware sizes, copies version strings, writes firmware blocks 0 and 2, and maps SE/AE cores to default groups.
- `nitrox_add_to_devlist()`, `nitrox_remove_from_devlist()`, `nitrox_get_first_device()`, and `nitrox_put_device()` manage the global ready-device list and reference counts.
- `nitrox_device_flr()` saves PCI config state, performs FLR, and restores state.
- `nitrox_pf_sw_init()`/`nitrox_pf_sw_cleanup()` wrap common queue allocation and interrupt registration.
- `nitrox_bist_check()` aggregates many BIST CSR values and fails initialization if any are nonzero.
- `nitrox_pf_hw_init()` sequences unit configuration, firmware load, and EMU setup.
- `nitrox_probe()`, `nitrox_remove()`, and `nitrox_shutdown()` implement lifecycle and cleanup.

## Control Flow

Probe starts with `pci_enable_device_mem()`, FLR, DMA mask setup, PCI region request, bus mastering, `struct nitrox_device` allocation, driver data installation, and global device-list insertion. The probe then records PCI IDs, timeout, NUMA node, maps BAR0, selects `min(MAX_PF_QUEUES, num_online_cpus())` queues, and applies the `qlen` module parameter.

Software setup calls `nitrox_common_sw_init()` then `nitrox_register_interrupts()`. Hardware setup first reads BIST registers, then calls the HAL configuration sequence: `nitrox_get_hwinfo()`, NPS core, AQM, packet, POM, EFL, BMI, BMO, LBC, random, firmware load, and EMU configuration. After hardware is usable, debugfs is initialized, statistics are zeroed, `__NDEV_READY` is published with an atomic barrier, and `nitrox_crypto_register()` exposes algorithms.

Removal requires the device reference count to reach zero. It marks the device not ready, removes it from the global list, disables SR-IOV, unregisters crypto algorithms and debugfs, tears down interrupts/common queues, unmaps BAR0, frees `ndev`, releases PCI regions, and disables the PCI device.

## State And Persistence Behavior

Persistent runtime state lives in the kernel driver object and hardware registers, not on disk. Global `ndevlist`, `devlist_lock`, and `num_devices` track available Nitrox devices. Each `ndev` stores hardware IDs, firmware names, queue count/length, timeout, mapped BAR, state atomics, stats, and refcount. Firmware load persists in device UCD blocks until reset. `nitrox_get_first_device()` increments `refcnt` only for a ready device; algorithm contexts later drop it through `nitrox_put_device()`.

## Dependencies And Integration Points

This file depends on Linux PCI, DMA, firmware loader, module, list/mutex/refcount APIs, and Nitrox internals from `nitrox_dev.h`, `nitrox_common.h`, `nitrox_csr.h`, `nitrox_hal.h`, `nitrox_isr.h`, and `nitrox_debugfs.h`. It integrates downward with CSR/HAL configuration and upward with the Crypto API registration layer. The firmware names are declared with `MODULE_FIRMWARE()`, so userspace firmware loading must provide the SE/AE blobs.

## Risks And Edge Cases

- Firmware validation only checks nonzero and maximum code size; malformed headers with short blobs or odd alignment can still stress firmware parsing assumptions.
- `nitrox_remove()` returns early if external references remain, leaving a partially bound device if consumers leak refs.
- `nitrox_shutdown()` is much lighter than remove and does not explicitly unregister crypto/debugfs or interrupts.
- `nitrox_load_fw()` multiplies big-endian `code_size` by two; the firmware contract must match this unit convention.
- Global list numbering decrements `num_devices` on removal, so indices can be reused across hotplug.

## Test Signals

Useful signals include successful PCI bind/unbind, firmware request/load messages, nonzero BIST failure handling, queue count and debugfs visibility, Crypto API algorithm registration, request processing through skcipher/AEAD paths, SR-IOV enable/disable transitions, and clean hot-unplug with no leaked references or IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_mbx.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_mbx.c

## Purpose

`nitrox_mbx.c` implements the PF-to-VF mailbox handling used when Nitrox SR-IOV is enabled. The physical function receives VF mailbox interrupts, decodes per-ring VF requests from NPS mailbox CSRs, and replies asynchronously from a workqueue with VF mode, VF up/down state, chip/VF IDs, and microcode information.

## Important APIs, Types, And Functions

- `enum mbx_msg_type` defines NOP, request, ACK, and NACK message types.
- `enum mbx_msg_opcode` defines supported VF requests: `MSG_OP_VF_MODE`, `MSG_OP_VF_UP`, `MSG_OP_VF_DOWN`, `MSG_OP_CHIPID_VFID`, and `MSG_OP_MCODE_INFO`.
- `struct pf2vf_work` packages a VF device, PF device, and `work_struct` for deferred response handling.
- `pf2vf_read_mbox()` reads `NPS_PKT_MBOX_VF_PF_PFDATAX(ring)`.
- `pf2vf_write_mbox()` writes `NPS_PKT_MBOX_PF_VF_PFDATAX(ring)`.
- `pf2vf_send_response()` transforms a VF request into an ACK response and updates `nitrox_vfdev` state.
- `pf2vf_resp_handler()` runs workqueue processing for one mailbox request.
- `nitrox_pf2vf_mbox_handler()` is called from the PF SR-IOV interrupt path and fans out work for set interrupt bits in low/high mailbox interrupt registers.
- `nitrox_mbox_init()` allocates per-VF state, initializes VF numbers, creates the `nitrox_pf2vf` workqueue, and enables mailbox interrupts.
- `nitrox_mbox_cleanup()` disables interrupts, destroys the workqueue, and frees VF state.

## Control Flow

SR-IOV setup calls `nitrox_mbox_init()` after PF SR-IOV interrupt registration. When mailbox interrupts arrive, `nitrox_pf2vf_mbox_handler()` reads `NPS_PKT_MBOX_INT_LO` for rings 0-63 and `NPS_PKT_MBOX_INT_HI` for rings 64-127. For each set bit it computes the VF number using `ring / ndev->iov.max_vf_queues`, stores the ring and request message into the corresponding `nitrox_vfdev`, allocates `pf2vf_work` with `GFP_ATOMIC`, queues the work item, and clears the interrupt bit by writing `BIT_ULL(i)`.

The worker handles only request-type messages. `MSG_OP_VF_MODE` returns `ndev->mode`; `MSG_OP_VF_UP` records VF queue count from message data and marks the VF ready; `MSG_OP_CHIPID_VFID` returns PF device index and VF number; `MSG_OP_VF_DOWN` clears VF queue count and marks it not ready; `MSG_OP_MCODE_INFO` reports two microcode types. Non-supported opcodes become NOP and do not produce a response.

## State And Persistence Behavior

Per-VF mutable state is stored in `ndev->iov.vfdev[]`: VF number, current ring, last message, queue count, readiness, and mailbox response counter. The PF workqueue is stored at `ndev->iov.pf2vf_wq`. Hardware state is the pair of VF-to-PF and PF-to-VF mailbox CSRs and interrupt bits. State persists while SR-IOV remains enabled; cleanup zeros the workqueue and VF array pointers.

## Dependencies And Integration Points

This code depends on Nitrox CSR definitions, mailbox message layout in `union mbox_msg`, VF state in `struct nitrox_vfdev`, HAL interrupt toggles `enable_pf2vf_mbox_interrupts()`/`disable_pf2vf_mbox_interrupts()`, and the SR-IOV lifecycle in `nitrox_sriov.c`. It integrates with interrupt dispatch from the Nitrox ISR code, which calls `nitrox_pf2vf_mbox_handler()`.

## Risks And Edge Cases

- If `kzalloc_obj(..., GFP_ATOMIC)` fails in the interrupt handler, the request is skipped but the interrupt bit is still cleared, so the VF may need retry logic.
- Ring-to-VF mapping assumes `max_vf_queues` is nonzero and matches hardware mode.
- `vfdev->msg` and `vfdev->ring` are written in interrupt context and read in workqueue context without an explicit per-VF lock; repeated requests for the same VF can overwrite state before prior work runs.
- Cleanup destroys the workqueue after disabling interrupts, which drains queued work, but caller ordering must prevent new mailbox handler invocations.

## Test Signals

Signals include successful VF queries for mode, chip/VF ID, and microcode info; VF up/down state changes; mailbox response counters increasing; no lost interrupt bits under low/high register coverage; SR-IOV teardown without queued work use-after-free; and VF retry behavior when PF allocation pressure drops a response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_mbx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_mbx.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_mbx.h

## Purpose

`nitrox_mbx.h` is the small public header for Nitrox PF/VF mailbox support. It exposes initialization, cleanup, and interrupt-handler entry points used by SR-IOV setup and ISR code.

## Important APIs, Types, And Functions

- Include guard `__NITROX_MBX_H` prevents duplicate declarations.
- `int nitrox_mbox_init(struct nitrox_device *ndev)` allocates VF mailbox state and enables PF-to-VF mailbox interrupt handling.
- `void nitrox_mbox_cleanup(struct nitrox_device *ndev)` disables mailbox interrupts and releases mailbox workqueue/VF state.
- `void nitrox_pf2vf_mbox_handler(struct nitrox_device *ndev)` processes pending VF mailbox interrupt bits and queues responses.

## Control Flow

`nitrox_sriov_init()` calls `nitrox_mbox_init()` after registering SR-IOV interrupts. The ISR path calls `nitrox_pf2vf_mbox_handler()` when mailbox interrupts are signaled. SR-IOV cleanup and disable call `nitrox_mbox_cleanup()`.

## State And Persistence Behavior

The header declares functions that manipulate `ndev->iov` state but owns no state itself. Persistence is entirely in the Nitrox device object and mailbox hardware CSRs.

## Dependencies And Integration Points

The declarations require `struct nitrox_device` to be visible from including files such as `nitrox_sriov.c` and ISR code. This header is the boundary between SR-IOV lifecycle and mailbox implementation.

## Risks And Edge Cases

The header has no compile-time include of `nitrox_dev.h`, so include order must provide the forward type. API callers must obey lifecycle ordering: initialize after `iov.num_vfs`/queue mode are set and clean up before VF state is freed.

## Test Signals

Build coverage should catch declaration mismatches. Runtime signals are mailbox init/cleanup during SR-IOV enable/disable and ISR dispatch to `nitrox_pf2vf_mbox_handler()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_mbx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_req.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_req.h

## Purpose

`nitrox_req.h` defines the Nitrox SE request ABI shared between Crypto API front ends and the request manager. It contains firmware/hardware descriptor formats, crypto context layout, request context structures for skcipher/AEAD variants, scatter-gather component formats, completion markers, and helper routines that build request-local source/destination SG arrays with IV, output response header, and completion bytes.

## Important APIs, Types, And Functions

- `PENDING_SIG` is written to ORH/completion memory before submission and later polled by completion handling.
- `PRIO` is the Crypto API priority used by Nitrox algorithms.
- `struct gphdr`, `union se_req_ctrl`, and `struct se_crypto_request` describe the logical SE firmware request.
- `enum flexi_cipher`, `enum flexi_auth`, `union fc_ctx_flags`, and `struct flexi_crypto_context` define firmware context fields for cipher/auth choices, AES key length, IV source, MAC length, and keys.
- `struct crypto_ctx_hdr`, `struct ctx_hdr`, and `struct nitrox_crypto_ctx` bridge software context memory to DMA context handles.
- `struct nitrox_kcrypt_request`, `struct nitrox_aead_rctx`, and `struct nitrox_rfc4106_rctx` are per-request contexts used by algorithm implementations.
- `union pkt_instr_hdr`, `union pkt_hdr`, `union slc_store_info`, `struct nps_pkt_instr`, and `struct aqmq_command_s` model packet and AQM hardware command words with endian-specific bitfields.
- `struct nitrox_sgcomp` stores four DMA pointer/length pairs per component; `struct nitrox_sgtable` tracks mapped SG state and component DMA address.
- `struct resp_hdr` and `struct nitrox_softreq` are request-manager state for posted commands, response/backlog lists, DMA mappings, timestamps, and callbacks.
- Helpers such as `flexi_aes_keylen()`, `alloc_req_buf()`, `create_single_sg()`, `create_multi_sg()`, `set_orh_value()`, `set_comp_value()`, `alloc_src_req_buf()`, `nitrox_creq_set_src_sg()`, `alloc_dst_req_buf()`, `nitrox_creq_set_orh()`, `nitrox_creq_set_comp()`, and `nitrox_creq_set_dst_sg()` are used by skcipher/AEAD request preparation.

## Control Flow

Algorithm front ends allocate request-local buffers using `alloc_src_req_buf()` and `alloc_dst_req_buf()`. Source layout is IV bytes followed by source SG entries; destination layout is ORH, IV, destination SG entries, and completion bytes. The front end fills `se_crypto_request` fields, including opcode, GP header offsets, context handle, control flags, and source/destination SG pointers. `nitrox_reqmgr.c` then maps those SG lists, converts them into Nitrox SG components, constructs a 64-byte `nps_pkt_instr`, posts it to a packet input queue, and later polls ORH/completion bytes.

## State And Persistence Behavior

Most data defined here is transient request or transform state. Transform state includes DMA-backed flexi crypto context memory and key material; exit paths must clear it. Request state includes dynamically allocated SG arrays, ORH/completion markers, and soft request mappings. Hardware-visible state is stored in big-endian descriptor fields and DMA memory. The helpers set `PENDING_SIG` via `WRITE_ONCE()` so completion polling can observe hardware writes reliably.

## Dependencies And Integration Points

The header depends on Linux DMA mapping, scatterlist, Crypto API AES constants, and Nitrox device definitions. It integrates with `nitrox_skcipher.c`, `nitrox_aead.c`, and `nitrox_reqmgr.c`. Endian-specific bitfields are part of the hardware ABI, so CPU endian definitions must match descriptor construction.

## Risks And Edge Cases

- Request buffers combine raw byte headers and `struct scatterlist` arrays; alignment and size assumptions must remain valid.
- `create_multi_sg()` uses `sg_virt()` from source SG entries, so callers must provide CPU-addressable SGs for this synthetic SG construction stage.
- `u16 total_bytes` in `nitrox_sgtable` can represent only limited input length; large requests need scrutiny.
- Bitfield layouts are compile-time endian-dependent and fragile if moved across architectures or changed without matching hardware docs.
- `PENDING_SIG` collision with a legitimate ORH/completion value would confuse completion polling, though the all-ones marker is chosen as a sentinel.

## Test Signals

Test signals include correct descriptor bytes under big/little endian builds, skcipher and AEAD known-answer tests, SG layouts with fragmented input/output, in-place and out-of-place CBC IV handling, timeout behavior when completion markers are not updated, and KASAN/KMSAN coverage for request buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_req.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_reqmgr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_reqmgr.c

## Purpose

`nitrox_reqmgr.c` turns a prepared `se_crypto_request` into DMA mappings, Nitrox SG components, packet input instructions, command-queue entries, and asynchronous completions. It also enforces queue length, backlogs eligible requests, processes response lists from solicited packet completions, and handles timeout/error propagation.

## Important APIs, Types, And Functions

- `incr_index()` wraps command queue ring indices.
- `softreq_unmap_sgbufs()` and `softreq_destroy()` undo DMA mappings, free SG component arrays, and release the soft request.
- `create_sg_component()` converts DMA-mapped Linux SG entries into Nitrox four-entry `nitrox_sgcomp` arrays and maps that component array for device access.
- `dma_map_inbufs()`/`dma_map_outbufs()` map request SG lists and create component lists.
- `backlog_list_add()`, `response_list_add()`, `response_list_del()`, and `get_first_response_entry()` maintain command queue lists.
- `cmdq_full()` atomically reserves pending slots and rolls back if over `ndev->qlen`.
- `post_se_instr()` copies a 64-byte instruction to the packet input ring, adds the request to the response list, records a timestamp, executes `dma_wmb()`, and rings the doorbell.
- `post_backlog_cmds()` drains queued backlog entries while space exists.
- `nitrox_enqueue_request()` posts immediately or backlogs/drops based on `CRYPTO_TFM_REQ_MAY_BACKLOG`.
- `nitrox_process_se_request()` is the exported submission entry point used by algorithm code.
- `sr_completed()`, `process_response_list()`, and `pkt_slc_resp_tasklet()` detect hardware completions and invoke request callbacks.
- `backlog_qflush_work()` retries backlog posting from workqueue context.

## Control Flow

`nitrox_process_se_request()` rejects non-ready devices, allocates `nitrox_softreq`, records callback state and response marker pointers, maps input and output SGs, extracts a DMA context handle if a crypto context is present, picks `smp_processor_id() % ndev->nr_queues`, and fills the packet instruction. The instruction points `dptr0` at input SG components, sets gather and scatter counts, sets front-data size, total length, destination solicit port, context length/pointer, opcode/arg, output SG component pointer, and GP header front data.

Submission calls `nitrox_enqueue_request()`, which first tries to flush old backlog requests, then uses `cmdq_full()` to decide whether to post, backlog, or reject. Posted requests are copied into `cmdq->base[write_idx]`, added to the response list, published with `dma_wmb()`, and submitted by writing `1` to the queue doorbell.

Completions arrive through `pkt_slc_resp_tasklet()`. It reads completion counts, asks `process_response_list()` to walk up to the current pending budget, checks ORH/completion markers, handles timeout if markers remain pending past `ndev->timeout`, decrements pending counts, removes completed requests, maps the low ORH byte to an error status, destroys request DMA resources, and calls the algorithm callback. The tasklet then clears/resends the interrupt and schedules backlog flush work if needed.

## State And Persistence Behavior

State is per-device command queue state: pending counts, backlog counts/list, response list, write index, MMIO doorbell/completion addresses, and stats counters (`posted`, `completed`, `dropped`). Per-request state persists from submission until callback and contains DMA mappings, SG component arrays, timestamp, callback, and response markers. Hardware-visible command descriptors and SG components persist in DMA memory until unmapped.

## Dependencies And Integration Points

This file depends on Nitrox common/device/CSR headers, Linux DMA mapping, workqueues, spinlocks, atomics, jiffies, and Crypto API request flags. It integrates with `nitrox_skcipher.c` and AEAD providers through `nitrox_process_se_request()`, with ISR setup through `pkt_slc_resp_tasklet()`, and with common queue allocation structures from `nitrox_dev.h`.

## Risks And Edge Cases

- `cmdq_full()` increments `pending_count` as a reservation; every failure/completion path must balance it.
- `post_backlog_cmds()` holds `backlog_qlock` while calling `post_se_instr()`, which takes `cmd_qlock` and response lock; lock ordering must remain consistent.
- `sr_completed()` waits up to about 1 ms for completion bytes after ORH status appears; slow memory visibility can produce false incomplete reports.
- Timeout handling still calls callbacks with the low ORH byte, which may remain `0xff` from `PENDING_SIG`, causing generic error mapping upstream.
- DMA maps both source and destination as bidirectional; this is conservative but can hide direction-specific cache bugs.
- `smp_processor_id()` queue selection assumes stable CPU context and can be skewed under softirq/preemption behavior.

## Test Signals

Signals include Crypto API async success, backlog behavior under full queues, dropped counters when backlog is disallowed, timeout logging, DMA mapping error handling, SG fragmentation coverage, stats increments, response-list ordering, and interrupt resend behavior when completion count remains over threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_reqmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_skcipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_skcipher.c

## Purpose

`nitrox_skcipher.c` registers and implements asynchronous skcipher algorithms backed by Nitrox SE firmware. It supports AES CBC/ECB/XTS/RFC3686 CTR/CTS-CBC and 3DES CBC/ECB, prepares firmware flexi crypto contexts, builds request-local SG layouts with IV and completion metadata, submits requests through `nitrox_process_se_request()`, and updates IVs on completion.

## Important APIs, Types, And Functions

- `struct nitrox_cipher` and `flexi_cipher_table[]` map Crypto API algorithm names to firmware `enum flexi_cipher` values.
- `nitrox_skcipher_init()` gets the first ready Nitrox device, allocates a DMA crypto context, stores a context handle, sets default callback, and extends request size by `struct nitrox_kcrypt_request`.
- `nitrox_cbc_init()` swaps in a CBC-specific callback for IV preservation.
- `nitrox_skcipher_exit()` zeroes key/auth context material, frees the crypto context, and drops the device reference.
- `nitrox_skcipher_setkey()`, `nitrox_aes_setkey()`, `nitrox_3des_setkey()`, `nitrox_aes_xts_setkey()`, and `nitrox_aes_ctr_rfc3686_setkey()` validate and store key/context data.
- `alloc_src_sglist()` and `alloc_dst_sglist()` build synthetic source/destination SG lists using helpers from `nitrox_req.h`.
- `nitrox_skcipher_crypt()` fills `se_crypto_request` opcode, GP header offsets, context handle, and submits the request.
- `nitrox_cbc_decrypt()` preserves the previous ciphertext block for in-place CBC decrypt IV update.
- `nitrox_register_skciphers()`/`nitrox_unregister_skciphers()` register/unregister the algorithm array.

## Control Flow

When a transform is created, init obtains a ready PF device and allocates a firmware context. `setkey` chooses a firmware cipher type from the algorithm name, fills flexi context flags, stores AES key length encoding, sets IV source to input data, converts flags to big endian, and copies key material. XTS additionally copies key2 into the auth key area; RFC3686 stores the nonce in `fctx->crypto.iv` and then stores the AES key.

Encryption/decryption calls `nitrox_skcipher_crypt()`. It sets request allocation flags from Crypto API sleep flags, opcode `FLEXI_CRYPTO_ENCRYPT_HMAC`, encrypt/decrypt arg, GP header data length and encryption offset, context length, then allocates source and destination request buffers. It submits through `nitrox_process_se_request()` and returns the async status.

Completion frees source/destination SG buffers, converts nonzero firmware status to `-EINVAL`, and completes the Crypto API request. CBC completion additionally updates `skreq->iv`: encrypt uses the final destination block; out-of-place decrypt uses the final source block; in-place decrypt uses a saved copy from before submission.

## State And Persistence Behavior

Transform state contains a `nitrox_crypto_ctx`, device reference, DMA context header, firmware context flags, and key material. Request state contains `nitrox_kcrypt_request`, allocated synthetic SG arrays, and optional saved CBC IV block. Device request state persists in the request manager until hardware completion. Key material is explicitly zeroed during transform exit.

## Dependencies And Integration Points

This file depends on Linux Crypto API skcipher, AES, DES3 verification, XTS verification, CTR RFC3686 constants, scatterwalk, Nitrox common/device/request headers, and `nitrox_process_se_request()`. It is registered by the higher Nitrox crypto registration layer called from `nitrox_main.c`.

## Risks And Edge Cases

- ECB algorithms still declare an IV size equal to the block size in this file, and request construction always prepends IV data; this matches firmware input expectations but differs from common ECB API intuition.
- CBC decrypt with `cryptlen < ivsize` computes an unsigned underflow for the IV-copy offset; blocksize enforcement by the Crypto API should prevent this but local checks are limited.
- `nitrox_skcipher_setkey()` chooses firmware cipher by name string; driver-name changes must keep names synchronized.
- RFC3686 nonce is stored in context, while per-request IV is still placed in request data; incorrect firmware interpretation would break counter construction.
- `crypto_skcipher_set_reqsize(tfm, existing + sizeof(...))` assumes any previous reqsize should be preserved.

## Test Signals

Use skcipher known-answer tests for AES CBC/ECB/XTS/RFC3686 CTR/CTS and 3DES CBC/ECB, in-place and out-of-place CBC decrypt IV update tests, invalid AES/3DES/XTS key tests, fragmented SG tests, async backlog tests, request allocation under atomic flags, and key zeroization checks under memory debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_skcipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_sriov.c

## Purpose

`nitrox_sriov.c` manages Nitrox PF transitions between normal PF crypto mode and SR-IOV mode. It validates VF counts, maps VF counts to hardware modes and queue allocation, disables PF crypto resources before VF enablement, initializes SR-IOV interrupts/mailbox support, configures hardware VF mode, and restores PF queues/crypto registration when SR-IOV is disabled.

## Important APIs, Types, And Functions

- `num_vfs_valid()` allows only 16, 32, 64, or 128 VFs.
- `num_vfs_to_mode()` maps 0/16/32/64/128 to `__NDEV_MODE_PF`, `__NDEV_MODE_VF16`, `__NDEV_MODE_VF32`, `__NDEV_MODE_VF64`, or `__NDEV_MODE_VF128`.
- `vf_mode_to_nr_queues()` maps PF mode to 64 queues and VF modes to 8/4/2/1 queue per VF.
- `nitrox_pf_cleanup()` marks PF not ready, unregisters crypto algorithms, interrupts, and common PF resources.
- `nitrox_pf_reinit()` reallocates PF resources, registers interrupts, configures AQM and packet rings/ports, marks ready, and re-registers crypto algorithms.
- `nitrox_sriov_init()`/`nitrox_sriov_cleanup()` manage SR-IOV PF interrupts and mailbox state.
- `nitrox_sriov_enable()` and `nitrox_sriov_disable()` implement the PCI SR-IOV callbacks.
- `nitrox_sriov_configure()` dispatches enable or disable based on `num_vfs`.

## Control Flow

Enabling checks VF count validity and returns early if already configured to that exact count. It calls `pci_enable_sriov()`, stores the mode, VF count, and per-VF queue count, sets the SR-IOV flag, then calls `nitrox_pf_cleanup()` because the PF has no queues in SR-IOV mode. It registers PF SR-IOV interrupts and mailbox support, then writes the NPS core VF configuration mode. If mailbox/interrupt init fails, it disables PCI SR-IOV, clears flags/counts/mode, and attempts `nitrox_pf_reinit()`.

Disabling first checks the SR-IOV flag. If VFs are assigned to VMs, it refuses with `-EPERM`. Otherwise it disables PCI SR-IOV, clears flags and VF queue state, returns to PF mode, cleans up SR-IOV mailbox/interrupt resources, writes PF hardware mode, and reinitializes PF crypto resources.

## State And Persistence Behavior

The driver mutates `ndev->mode`, `ndev->iov.num_vfs`, `ndev->iov.max_vf_queues`, `ndev->flags`, and `ndev->state`. Hardware state changes through PCI SR-IOV enable/disable and `config_nps_core_vfcfg_mode()`. PF Crypto API availability is deliberately removed during SR-IOV mode and restored on disable.

## Dependencies And Integration Points

This file depends on Linux PCI SR-IOV APIs, Nitrox HAL configuration, common queue/interrupt setup, crypto algorithm registration, SR-IOV interrupt registration, and mailbox functions from `nitrox_mbx.h`. It is wired into the PCI driver through `.sriov_configure` in `nitrox_main.c`.

## Risks And Edge Cases

- If `nitrox_pf_reinit()` fails during rollback or disable, the PF may remain not ready after SR-IOV teardown.
- Enabling only supports fixed VF counts; arbitrary counts are rejected even if PCI core would permit them.
- PF cleanup unregisters crypto algorithms globally; multi-device behavior depends on the broader Nitrox crypto registration layer tolerating repeated unregister/register.
- `pci_vfs_assigned()` prevents disabling assigned VFs, but callers must surface `-EPERM` properly to administrators.

## Test Signals

Signals include sysfs SR-IOV enable for 16/32/64/128 VFs, rejection for unsupported counts, VF mailbox functionality, PF algorithms disappearing during SR-IOV and returning after disable, refusal while VFs are assigned, hardware VF mode register changes, and rollback from simulated interrupt/mailbox init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/Kconfig

## Purpose

`Kconfig` defines build-time options for the AMD Secure Processor/CCP driver family: the base Secure Processor device driver, the CCP cryptographic coprocessor device, the Crypto API offload module, the Platform Security Processor, and optional CCP debugfs exposure.

## Important APIs, Types, And Functions

- `CRYPTO_DEV_CCP_DD` builds the base `ccp` module and depends on AMD CPU support or ARM64.
- `CRYPTO_DEV_SP_CCP` enables the CCP device under the base driver, depends on `CRYPTO_DEV_CCP_DD && DMADEVICES`, and selects RNG, DMA engine, SHA1, and SHA256 support.
- `CRYPTO_DEV_CCP_CRYPTO` builds the `ccp_crypto` module, depends on the base and CCP device options, and selects hash/skcipher/authenc/RSA/AES library support.
- `CRYPTO_DEV_SP_PSP` enables PSP support on x86_64 with AMD IOMMU and selects `PCI_TSM` when PCI is enabled.
- `CRYPTO_DEV_CCP_DEBUGFS` gates debugfs internals and depends on CCP device support.

## Control Flow

There is no runtime control flow. Kconfig dependencies decide which objects are compiled by the Makefile and which kernel subsystems are selected automatically.

## State And Persistence Behavior

The file contributes persistent kernel configuration state through `.config` symbols. Those symbols determine compiled modules and runtime availability of CCP, PSP, crypto offload, DMAengine, hwrng, and debugfs functionality.

## Dependencies And Integration Points

This file integrates with `drivers/crypto/ccp/Makefile`, kernel Crypto API configuration, DMAengine, hwrng, AMD IOMMU, PCI TSM, and debugfs. Its selected symbols ensure core algorithms needed by CCP wrappers are available.

## Risks And Edge Cases

- `CRYPTO_DEV_SP_CCP` defaults to `y` once the base driver and DMA devices are enabled, so platform builds can include hardware code by default.
- `CRYPTO_DEV_CCP_CRYPTO` depends on CCP device support; disabling the device disables Crypto API offload even if the base Secure Processor module remains.
- Debugfs exposure is optional and should remain off by default for minimal introspection surface.

## Test Signals

Build matrix signals include `ccp.o` without crypto offload, `ccp_crypto.o` with offload, debugfs-enabled builds, PSP-only/base-only combinations, ARM64 platform builds, x86_64 PSP builds, and module load ordering under `m` defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/Makefile

## Purpose

The CCP `Makefile` maps Kconfig symbols to object composition for the AMD Secure Processor/CCP driver. It builds the base `ccp` module from SP bus/platform code plus optional CCP, PCI, PSP, debugfs, and TSM pieces, and builds the separate `ccp-crypto` module from Crypto API algorithm providers.

## Important APIs, Types, And Functions

- `obj-$(CONFIG_CRYPTO_DEV_CCP_DD) += ccp.o` creates the base module.
- `ccp-objs := sp-dev.o sp-platform.o` are always part of the base module.
- `ccp-$(CONFIG_CRYPTO_DEV_SP_CCP)` adds CCP device, operation, v3/v5, and DMAengine files.
- `ccp-$(CONFIG_CRYPTO_DEV_CCP_DEBUGFS)` adds `ccp-debugfs.o`.
- `ccp-$(CONFIG_PCI)` adds `sp-pci.o`.
- `ccp-$(CONFIG_CRYPTO_DEV_SP_PSP)` adds PSP/SEV/TEE/platform-access/DBC/HSTI/SFS objects.
- `ccp-$(CONFIG_CRYPTO_DEV_SP_PSP)` additionally adds SEV TSM/TIO files when `CONFIG_PCI_TSM=y`.
- `obj-$(CONFIG_CRYPTO_DEV_CCP_CRYPTO) += ccp-crypto.o` creates the Crypto API module.
- `ccp-crypto-objs` lists AES, CMAC, XTS, GCM, DES3, RSA, and SHA providers plus the crypto main queue.

## Control Flow

There is no runtime control flow. Kbuild evaluates configuration symbols and composes linked modules from the selected object lists.

## State And Persistence Behavior

Build output state is the generated `ccp.ko` and `ccp_crypto.ko` modules or built-in objects. The split means hardware device support can exist independently from Crypto API offload registration.

## Dependencies And Integration Points

The file integrates Kconfig with Kbuild and ensures `ccp-crypto-main.c` is linked with all algorithm provider implementations. It also keeps PSP and CCP device code in one base module, sharing SP bus infrastructure.

## Risks And Edge Cases

- The base module can grow substantially when PSP and CCP are both enabled; object-level dependencies must avoid unresolved symbols for disabled features.
- `ccp-crypto` assumes exported core APIs such as `ccp_present()`, `ccp_version()`, and `ccp_enqueue_cmd()` are available from the base driver.
- Conditional TSM objects are tied to both PSP and `PCI_TSM=y`; module/built-in combinations need build coverage.

## Test Signals

Signals include `make M=drivers/crypto/ccp` for combinations of CCP, PSP, PCI, debugfs, and crypto offload; module dependency checks showing `ccp_crypto` depending on `ccp`; and boot/module-load tests for each built object set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-cmac.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-cmac.c

## Purpose

`ccp-crypto-aes-cmac.c` implements the Crypto API `cmac(aes)` asynchronous hash algorithm using CCP AES-CMAC hardware support. It manages CMAC buffering, final-block padding, K1/K2 subkey generation, export/import state, and command submission through the shared CCP crypto queue.

## Important APIs, Types, And Functions

- `ccp_aes_cmac_complete()` handles hardware completion, preserves leftover data for non-final updates, copies final digest, and frees the temporary SG table.
- `ccp_do_cmac_update()` is the main update/final/finup path. It builds a composite SG table from buffered data, request data, and padding, selects K1 or K2 for final blocks, and submits an AES CMAC command.
- `ccp_aes_cmac_init()`, `update()`, `final()`, `finup()`, and `digest()` implement the ahash operation set.
- `ccp_aes_cmac_export()`/`ccp_aes_cmac_import()` serialize and restore partial CMAC state.
- `ccp_aes_cmac_setkey()` validates AES key length, computes K1/K2 by AES-encrypting zero and doubling in GF(2^128), stores the supplied key, and initializes SGs.
- `ccp_aes_cmac_cra_init()` sets completion handler and DMA request size.
- `ccp_register_aes_cmac_algs()` allocates/registers the `cmac(aes)` ahash algorithm.

## Control Flow

Init clears the request context and marks a null message. Updates that are not final and do not exceed one block are buffered locally. Otherwise, the code computes the number of full bytes to hash and the remainder to retain. For final operations, it pads null or partial blocks with `0x80` followed by zeroes, chooses K2 if padded or K1 if complete, and includes that subkey in the CCP command. Completion saves any remainder for later updates or copies the digest from the IV/context buffer when final.

`setkey()` derives CMAC subkeys synchronously using the software AES helper, then stores the actual AES key for CCP hardware commands. Registration creates an async ahash with `CRYPTO_ALG_NEED_FALLBACK`, DMA padding, priority 300, 16-byte digest, and export state size.

## State And Persistence Behavior

Transform state stores AES type/mode/key, K1/K2 and SG wrappers. Request state stores null/final flags, source/nbytes, hash counts, temporary SG table, IV/output buffer, buffered partial block, padding block, and `struct ccp_cmd`. Export/import persists null flag, IV, buffered count, and buffered block.

## Dependencies And Integration Points

This file depends on Crypto API ahash, AES software helpers for subkey generation, scatterwalk, `ccp_crypto_sg_table_add()`, and `ccp_crypto_enqueue_request()`. It is registered by `ccp_register_algs()` when AES offload is enabled.

## Risks And Edge Cases

- The temporary SG table must be freed on every completion/error path; missing callback would leak it.
- CMAC final padding and K1/K2 selection are security-sensitive and easy to regress for null or exact-block messages.
- `ccp_do_cmac_update()` keeps one block buffered for non-final exact-block updates because the hardware cannot do a zero-length final; this behavior must stay aligned with Crypto API streaming semantics.
- `ctx->u.aes.key_len` remains zero until subkeys and key are fully initialized, preventing use of partial key state.

## Test Signals

Use CMAC known-answer tests for AES-128/192/256, empty message, one-block, partial-block, multi-update, finup/digest paths, export/import resume, non-sleeping allocation paths, and error unwinding for SG allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-cmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-galois.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-galois.c

## Purpose

`ccp-crypto-aes-galois.c` registers AES-GCM AEAD offload for CCP v5-capable hardware. It validates GCM keys and authentication tag sizes, builds the 16-byte GCM initial counter block, describes AAD and crypt text lengths to the CCP AES command, and registers `gcm(aes)` with the Crypto API.

## Important APIs, Types, And Functions

- `ccp_aes_gcm_complete()` currently just returns the hardware status.
- `ccp_aes_gcm_setkey()` validates AES key size, sets type/mode `CCP_AES_MODE_GCM`, stores the key, and initializes `key_sg`.
- `ccp_aes_gcm_setauthsize()` accepts tag sizes 16, 15, 14, 13, 12, 8, and 4.
- `ccp_aes_gcm_crypt()` validates key/mode/IV, builds `J0 = IV || 0x00000001`, fills a `CCP_ENGINE_AES` command with auth size, action, key, IV, source length, AAD length, and destination.
- `ccp_aes_gcm_encrypt()`/`ccp_aes_gcm_decrypt()` select action.
- `ccp_aes_gcm_cra_init()` sets completion and AEAD request DMA size.
- `ccp_register_aes_aeads()` registers version-gated AEAD definitions, currently `gcm(aes)` for CCP v5 and later.

## Control Flow

After setkey, each AEAD request copies the 12-byte nonce IV into a request-local 16-byte buffer, zeroes bytes 12-14, sets byte 15 to 1, and wraps that buffer in a scatterlist. The command treats `req->src` as AAD concatenated with plaintext/ciphertext and `req->dst` as ciphertext/plaintext plus tag, with `req->assoclen` identifying AAD length and `req->cryptlen` identifying crypt data/tag length as expected by the lower CCP operation layer.

Registration copies defaults into an allocated `ccp_crypto_aead`, overwrites algorithm names and blocksize, and calls `crypto_register_aead()` only if `ccp_version()` meets the version requirement.

## State And Persistence Behavior

Transform state stores AES type, mode, key length, key bytes, and key scatterlist. Request state stores IV buffer/scatterlist and `struct ccp_cmd` in `ccp_aes_req_ctx`. There is no additional persistent AEAD state beyond Crypto API transform lifetime.

## Dependencies And Integration Points

This file depends on Crypto API AEAD/GCM constants, AES constants, CCP shared crypto context/request structures, and the shared enqueue queue. It is linked into `ccp-crypto.o` and registered through `ccp-crypto-main.c`.

## Risks And Edge Cases

- GCM IV handling assumes the standard 96-bit IV path only; non-12-byte IV forms are not supported by the registered `ivsize`.
- The completion callback does not adjust output lengths or verify tags itself; correctness depends on lower CCP operation code.
- `def->mode` is set to `CCP_AES_MODE_GHASH` in the registration metadata while setkey uses `CCP_AES_MODE_GCM`; current metadata is not consumed by request construction but may confuse future refactors.
- AEAD source/destination layout assumptions must match the generic Crypto API GCM convention and CCP operation layer.

## Test Signals

Signals include AES-GCM known-answer encrypt/decrypt tests for all accepted tag sizes, authentication failure tests, fragmented AAD/data SGs, in-place and out-of-place buffers, rejection of unsupported tag/key sizes, and version gating on v3 versus v5 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-galois.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-xts.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-xts.c

## Purpose

`ccp-crypto-aes-xts.c` provides the Crypto API `xts(aes)` skcipher backed by CCP XTS-AES hardware when the request fits hardware constraints, with a software fallback for unsupported unit sizes or key sizes. It registers the algorithm, manages fallback transform lifetime, validates XTS keys, and updates IV/tweak output on hardware completion.

## Important APIs, Types, And Functions

- `aes_xts_algs[]` names the registered algorithm and driver.
- `xts_unit_sizes[]` maps supported request lengths 16, 512, 1024, 2048, and 4096 to CCP unit-size encodings.
- `ccp_aes_xts_complete()` copies the updated IV/tweak from request context to `req->iv`.
- `ccp_aes_xts_setkey()` validates XTS keys, stores supported key material, sets hardware key length, initializes key SG, and sets the fallback transform key.
- `ccp_aes_xts_crypt()` chooses hardware or fallback path, fills a `CCP_ENGINE_XTS_AES_128` command for supported requests, and submits it.
- `ccp_aes_xts_init_tfm()` allocates fallback `xts(aes)` with `CRYPTO_ALG_NEED_FALLBACK` and sizes request context to include fallback request storage.
- `ccp_aes_xts_exit_tfm()` frees the fallback transform.
- `ccp_register_aes_xts_algs()` registers the algorithm.

## Control Flow

Requests first validate that a key has been set and an IV is present. The code searches for an exact request-length match in `xts_unit_sizes[]`. It forces fallback if no unit size matches, if v3 hardware is asked to use a non-AES-128 XTS key, or if the key half length is neither 128 nor 256 bits. Fallback requests reuse the caller callback/data and call the software skcipher directly. Hardware requests copy the IV, initialize its SG, populate the XTS command with action, unit size, key, IV, source/destination, and enqueue through the shared CCP crypto queue.

## State And Persistence Behavior

Transform state stores the fallback skcipher pointer, hardware key bytes, key length, and key SG. Request state stores IV, IV SG, CCP command, and embedded fallback request. The fallback transform persists for the tfm lifetime and is freed in exit.

## Dependencies And Integration Points

This file depends on Crypto API skcipher/XTS helpers, scatterwalk, CCP shared crypto header, `ccp_version()`, and `ccp_crypto_enqueue_request()`. It is registered as part of AES algorithm registration in `ccp-crypto-main.c`.

## Risks And Edge Cases

- Hardware is used only when `cryptlen` exactly equals a supported unit size, even though hardware may support multiples; larger valid XTS requests fall back.
- `ccp_aes_xts_setkey()` sets `key_len` even if AES-256 on v3 did not copy hardware key material; later v3 requests should fallback because of version/key checks.
- Fallback request storage must remain last in `ccp_aes_req_ctx`; the header comments rely on that for variable request size.
- The source comment says "bug" where it means "but"; maintainers should read the block as a hardware/software limitation note, not a known defect marker.

## Test Signals

Signals include XTS known-answer tests for 16/512/1024/2048/4096-byte requests on v5 hardware, fallback coverage for odd sizes and unsupported v3 AES-256, key verification failures for weak/equal halves, IV update correctness, and module unload freeing fallback tfms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-xts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes.c

## Purpose

`ccp-crypto-aes.c` implements standard AES skcipher offload for ECB, CBC, CTR, and RFC3686 CTR modes using the CCP AES engine. It validates keys and block sizes, stores key/nonce state, builds `struct ccp_cmd` requests, updates IVs on completion, and registers version-gated algorithms.

## Important APIs, Types, And Functions

- `ccp_aes_complete()` copies the updated IV from request context back to the request for non-ECB modes.
- `ccp_aes_setkey()` maps AES key lengths to CCP AES types, stores mode from the registered algorithm wrapper, copies key bytes, and initializes `key_sg`.
- `ccp_aes_crypt()` validates key, block alignment for ECB/CBC, IV presence for non-ECB, fills a `CCP_ENGINE_AES` command, and enqueues it.
- `ccp_aes_init_tfm()` sets completion and request size.
- `ccp_aes_rfc3686_setkey()` separates trailing nonce from key material.
- `ccp_aes_rfc3686_crypt()` constructs a full 16-byte RFC3686 counter block from nonce, per-request IV, and counter value 1, temporarily replaces `req->iv`, and delegates to `ccp_aes_crypt()`.
- `ccp_aes_rfc3686_complete()` restores the original IV pointer before normal completion handling.
- `ccp_register_aes_algs()` registers ECB/CBC/CTR/RFC3686 definitions when `ccp_version()` is sufficient.

## Control Flow

Registration allocates a `ccp_crypto_skcipher_alg` per mode, copies default skcipher ops, sets `ccp_alg->mode`, overrides names/blocksize/ivsize, and calls `crypto_register_skcipher()`. Runtime crypt operations use the algorithm wrapper to set `ctx->u.aes.mode` at key setup. Each request populates command engine, AES type/mode/action, key SG, IV SG when needed, source length, and destination. The shared queue handles async ordering and hardware dispatch.

## State And Persistence Behavior

Transform state stores AES mode/type, key bytes, key length, key SG, and RFC3686 nonce. Request state stores IV buffer, IV SG, optional original RFC3686 IV pointer, constructed counter block, and CCP command. No state is written outside kernel memory and hardware command queues.

## Dependencies And Integration Points

This file depends on Crypto API skcipher, AES/CTR constants, Linux scatterlists, `ccp-crypto.h`, `ccp_version()`, and `ccp_crypto_enqueue_request()`. It integrates with the lower operation layer through `CCP_ENGINE_AES` command fields.

## Risks And Edge Cases

- ECB and CBC reject non-block-multiple lengths; CTR modes allow byte granularity.
- RFC3686 temporarily mutates `req->iv`; completion must always restore it, including error paths through `ccp_aes_rfc3686_complete()`.
- `CRYPTO_ALG_NEED_FALLBACK` is set, but this file itself does not allocate a fallback transform for standard AES modes; fallback handling is left to the crypto stack/provider selection.
- Key material is stored in context and should be cleared by broader transform teardown if added in future.

## Test Signals

Signals include AES ECB/CBC/CTR/RFC3686 known-answer tests, invalid key lengths, CBC/ECB unaligned length rejection, IV update checks, RFC3686 nonce/counter construction, fragmented SG coverage, and v3 registration gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-des3.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-des3.c

## Purpose

`ccp-crypto-des3.c` implements CCP-backed 3DES ECB and CBC skcipher algorithms for v5 hardware. It validates DES3 keys, builds DES3 CCP commands, updates CBC IVs on completion, and registers mode-specific skcipher algorithms.

## Important APIs, Types, And Functions

- `ccp_des3_complete()` copies updated IV back to the request for non-ECB modes.
- `ccp_des3_setkey()` uses `verify_skcipher_des3_key()`, sets type `CCP_DES3_TYPE_168`, records mode from algorithm metadata, stores key bytes, and initializes key SG.
- `ccp_des3_crypt()` validates key and block alignment, prepares IV SG for CBC, fills `CCP_ENGINE_DES3` command fields, and enqueues.
- `ccp_des3_init_tfm()` sets completion and DMA request size.
- `des3_algs[]` defines v5-only ECB and CBC registrations.
- `ccp_register_des3_algs()` version-gates and registers algorithms.

## Control Flow

At registration, each definition copies common defaults into an allocated wrapper, records mode, sets names/blocksize/ivsize, and registers with Crypto API. At runtime, setkey stores the mode chosen by that wrapper. Encrypt/decrypt calls share `ccp_des3_crypt()`, which rejects missing keys and invalid block lengths for ECB/CBC, optionally copies IV into request context, fills key/source/destination fields, and submits through `ccp_crypto_enqueue_request()`.

## State And Persistence Behavior

Transform state stores DES3 type/mode/key/key SG/key length. Request state stores IV buffer, IV SG, and command. Hardware-visible state is transient command queue and DMA SG references.

## Dependencies And Integration Points

This file depends on Crypto API skcipher, DES3 key verification, CCP shared crypto structures, `ccp_version()`, and the shared CCP enqueue path. It integrates with v5 operation code through `CCP_ENGINE_DES3`; v3 `ccp_actions` has no DES3 handler, so registration is v5-gated.

## Risks And Edge Cases

- Only 168-bit 3DES keys are supported; 112-bit behavior is intentionally left to callers making K1 equal K3.
- CBC/ECB reject non-block-aligned request lengths.
- DES3 is legacy crypto; deployments may disable it with the module parameter in `ccp-crypto-main.c`.

## Test Signals

Signals include DES3 ECB/CBC known-answer tests on v5 hardware, absence on v3, weak-key rejection, IV update correctness, unaligned length rejection, and `des3_disable` module parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-des3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-main.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-main.c

## Purpose

`ccp-crypto-main.c` is the module entry point and shared scheduler for CCP Crypto API algorithms. It verifies that a CCP device is present, registers enabled algorithms, maintains lists for cleanup, and wraps lower `ccp_enqueue_cmd()` with a global queue that preserves request ordering per Crypto API transform while allowing commands for different transforms to run concurrently.

## Important APIs, Types, And Functions

- Module parameters `aes_disable`, `sha_disable`, `des3_disable`, and `rsa_disable` selectively skip algorithm families.
- `hash_algs`, `skcipher_algs`, `aead_algs`, and `akcipher_algs` track registered algorithm wrappers.
- `struct ccp_crypto_queue` stores pending commands, backlog pointer, and command count.
- `struct ccp_crypto_cmd` wraps a `ccp_cmd`, original async request, transform pointer, and return state.
- `ccp_crypto_success()` normalizes `0`, `-EINPROGRESS`, and `-EBUSY` as successful enqueue outcomes.
- `ccp_crypto_enqueue_request()` allocates the wrapper, sets lower callback/data, maps Crypto API backlog flags to `CCP_CMD_MAY_BACKLOG`, and calls `ccp_crypto_enqueue_cmd()`.
- `ccp_crypto_complete()` handles lower command progress/completion, advances backlog notifications, runs algorithm-specific completion fixups, completes the original request, and submits held same-tfm commands.
- `ccp_crypto_sg_table_add()` copies SG entries into a preallocated SG table.
- `ccp_register_algs()` and `ccp_unregister_algs()` manage algorithm family registration/unregistration.
- `ccp_crypto_init()`/`ccp_crypto_exit()` are module init/exit.

## Control Flow

Module init calls `ccp_present()` and refuses to load when no CCP exists. It initializes the global queue and registers algorithm families unless disabled. Each algorithm request is wrapped in `ccp_crypto_cmd`. The enqueue path rejects or backlogs at `CCP_CRYPTO_MAX_QLEN`, then scans for an existing command with the same `tfm`. If none exists, it submits immediately to `ccp_enqueue_cmd()`; if one exists, it only queues locally to preserve per-transform ordering.

On lower completion, `ccp_crypto_complete()` removes the completed wrapper, sends `-EINPROGRESS` notifications to backlog entries as they advance, runs the transform-specific `ctx->complete()` callback, completes the Crypto API request, then attempts to submit the next held command for the same transform. If held submission fails, it completes that request with the error and continues scanning.

## State And Persistence Behavior

The module stores registered algorithm lists and a global queue protected by `req_queue_lock`. `req_queue.backlog` is a cursor into the command list. Each queued request stores a stable `tfm` pointer separately from the request because the async request may become invalid after completion callback invocation.

## Dependencies And Integration Points

This file depends on exported CCP core APIs from the base driver (`ccp_present()`, `ccp_enqueue_cmd()`, `ccp_version()` via providers), Linux Crypto API registration, and provider registration functions from the other `ccp-crypto-*` files. It integrates lower completion semantics from the CCP device scheduler with upper Crypto API async/backlog semantics.

## Risks And Edge Cases

- The global queue is capped at 100 commands; high concurrency can return `-ENOSPC` or `-EBUSY` depending on caller backlog flags.
- Ordering is per `tfm`, not per algorithm family; shared transforms serialize while different transforms may run out of order relative to each other.
- Completion invokes callbacks outside the queue lock, but uses stored `tfm` to avoid dereferencing freed request memory after callback.
- Partial registration failure calls unregister for already registered algorithms; providers must add list entries only after successful registration.

## Test Signals

Signals include module load refusal without CCP, algorithm list registration with disable parameters, async ordering tests issuing multiple requests on one tfm, backlog notification behavior, unregister cleanup after injected registration failure, and stress tests across multiple transforms and hardware queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-rsa.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-rsa.c

## Purpose

`ccp-crypto-rsa.c` implements Crypto API `rsa` akcipher offload using the CCP RSA engine. It parses public/private keys, stores modulus/exponent/private exponent in scatterlists, builds RSA commands for encrypt/decrypt operations, updates output length on completion, and registers version-gated RSA support.

## Important APIs, Types, And Functions

- `akcipher_request_cast()` converts async requests to akcipher requests.
- `ccp_copy_and_save_keypart()` strips leading zero bytes from key parts, records resulting length, and duplicates the data.
- `ccp_rsa_complete()` sets `req->dst_len` from hardware key size on success.
- `ccp_rsa_maxsize()` returns modulus length.
- `ccp_rsa_crypt()` fills a `CCP_ENGINE_RSA` command using public exponent for encrypt or private exponent for decrypt.
- `ccp_check_key_length()` restricts modulus size to 8..4096 bits at this layer.
- `ccp_rsa_free_key_bufs()` frees sensitive key buffers and clears pointers/lengths.
- `ccp_rsa_setkey()` parses ASN.1 public/private keys, stores n/e/d, initializes SGs, and validates key length.
- `ccp_rsa_init_tfm()` and `ccp_rsa_exit_tfm()` set request size/completion and free key material.
- `ccp_register_rsa_algs()` registers `rsa` for CCP v3 and later.

## Control Flow

Setting a key first frees any old key material. It parses either private or public RSA key data using shared kernel RSA parsers, strips leading zeroes from modulus and exponent parts, initializes scatterlists, computes bit length, and validates it. Private-key setup additionally stores `d`.

Encrypt/decrypt requests create a command with key size in bits, exponent SG selected by operation, modulus SG, source length, and destination SG, then enqueue through the shared CCP crypto queue. Completion sets the destination length to the key size in bytes if the lower command succeeded.

## State And Persistence Behavior

Transform state stores allocated sensitive buffers for `n`, `e`, and optional `d`, their SG wrappers, byte lengths, and key length in bits. Buffers are freed with `kfree_sensitive()` on replacement and transform exit. Request state contains only the command wrapper.

## Dependencies And Integration Points

This file depends on Crypto API akcipher/RSA parsers, scatterlists, `ccp-crypto.h`, `ccp_version()`, and `ccp_crypto_enqueue_request()`. Lower CCP operation code must implement `CCP_ENGINE_RSA` for the active hardware version.

## Risks And Edge Cases

- The local key length limit is 4096 bits even though v5 device data exposes a wider `CCP5_RSA_MAX_WIDTH`; this provider does not use that larger limit.
- Public-key transforms lack `d`; calling decrypt without a private key would submit an uninitialized/empty private exponent unless higher layers prevent that usage.
- RSA here is raw modular exponentiation exposed through akcipher; padding schemes are handled elsewhere or by callers.
- Leading-zero stripping changes buffer lengths; hardware key-size handling must still align source/destination widths correctly.

## Test Signals

Signals include RSA encrypt/decrypt known-answer tests, public/private key parsing, leading-zero modulus/exponent keys, key size boundary rejection, max output length reporting, sensitive buffer cleanup on key replacement, and v3/v5 registration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-rsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-sha.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-sha.c

## Purpose

`ccp-crypto-sha.c` implements CCP-backed asynchronous SHA and HMAC-SHA hash algorithms. It handles streaming buffering, first/final flags, message bit counts, HMAC ipad/opad setup, export/import state, version-gated registration of SHA1/SHA224/SHA256/SHA384/SHA512, and paired HMAC registrations.

## Important APIs, Types, And Functions

- `ccp_sha_complete()` saves remainder data after non-final updates, copies final digest, and frees temporary SG tables.
- `ccp_do_sha_update()` is the shared update/final/finup path. It combines buffered and new data, keeps one block for later non-final operations when needed, updates `msg_bits`, fills a `CCP_ENGINE_SHA` command, and enqueues it.
- `ccp_sha_init()`, `update()`, `final()`, `finup()`, and `digest()` implement ahash operations.
- `ccp_sha_export()`/`ccp_sha_import()` serialize/restore hash type, bit count, first flag, context, and buffered data.
- `ccp_sha_setkey()` implements HMAC key handling: hash oversized keys with a child shash, zero-pad, and compute ipad/opad.
- `ccp_sha_cra_init()` and `ccp_hmac_sha_cra_init()` initialize plain and HMAC transforms; HMAC allocates the child shash named in `child_alg`.
- `ccp_register_sha_alg()` registers each SHA and then its HMAC wrapper.
- `ccp_register_sha_algs()` version-gates algorithms: SHA1/SHA224/SHA256 on v3+, SHA384/SHA512 on v5+.

## Control Flow

Plain SHA init clears request state, sets the type from algorithm metadata, and marks first block. HMAC init additionally preloads the request buffer with ipad for the first update when a key is set. Updates that do not exceed one block and are not final are buffered. Otherwise, the code builds either a combined SG table of prior buffer plus new SG data or uses a single buffer/request SG, computes the count to send, updates total bits, fills context SG and SHA command fields, and submits. Completion copies the digest when final and saves any remainder for streaming.

Registration allocates an algorithm wrapper for each version-supported SHA. After registering the plain hash, it clones the base wrapper, adds `setkey`, changes names to `hmac(<sha>)`, sets HMAC init/exit, and registers the HMAC ahash.

## State And Persistence Behavior

Transform state stores HMAC key length, key/ipad/opad blocks, opad SG/count, and optional child shash. Request state stores hash type, total bits, first/final flags, source/nbytes, hash counts, temporary SG table, hardware context buffer, partial block buffer, and command. Export/import preserves enough state for suspend/resume of hash operations.

## Dependencies And Integration Points

This file depends on Crypto API ahash/HMAC/shash helpers, SHA constants, scatterwalk, `ccp_crypto_sg_table_add()`, and `ccp_crypto_enqueue_request()`. It integrates with v3/v5 SHA hardware operations and Crypto API fallback selection.

## Risks And Edge Cases

- `msg_bits` is incremented before hardware completion; if a command fails, request state is already advanced.
- HMAC relies on a child software shash for oversized key hashing; missing child algorithm causes HMAC transform init failure.
- The "keep one block" behavior for non-final exact-block updates is required because CCP cannot do zero-length final; regressions affect streaming hashes.
- Temporary SG table allocation depends on request sleep flags and must be freed exactly once.

## Test Signals

Signals include SHA and HMAC known-answer tests for all registered variants, streaming update/final/finup/digest combinations, export/import resume, oversized HMAC keys, exact-block and empty-message cases, v3/v5 version gating, and allocation failure/error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-sha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto.h

## Purpose

`ccp-crypto.h` is the shared internal header for CCP Crypto API providers. It defines algorithm wrapper types, per-transform contexts, per-request contexts, export/import state layouts, common priorities, helper accessors, and provider registration prototypes.

## Important APIs, Types, And Functions

- `CCP_CRA_PRIORITY` sets Crypto API priority 300.
- `struct ccp_crypto_skcipher_alg`, `ccp_crypto_aead`, `ccp_crypto_ahash_alg`, and `ccp_crypto_akcipher_alg` wrap registered Crypto API algorithms with list entries and CCP metadata.
- `ccp_crypto_skcipher_alg()` and `ccp_crypto_ahash_alg()` recover wrappers from Crypto API transform/algorithm pointers.
- `struct ccp_aes_ctx` stores AES mode/type/key, nonce, fallback XTS tfm, and CMAC subkeys.
- `struct ccp_aes_req_ctx` stores IV/tag buffers, RFC3686 state, command, and embedded fallback skcipher request.
- `struct ccp_aes_cmac_req_ctx` and `ccp_aes_cmac_exp_ctx` store CMAC streaming/export state.
- `struct ccp_des3_ctx`/`ccp_des3_req_ctx`, `struct ccp_sha_ctx`/`ccp_sha_req_ctx`/`ccp_sha_exp_ctx`, and `struct ccp_rsa_ctx`/`ccp_rsa_req_ctx` define family-specific state.
- `struct ccp_ctx` is the common transform context with a completion hook and a union of algorithm family contexts.
- Function prototypes expose shared enqueue, SG table helper, and family registration functions.

## Control Flow

There is no executable control flow except small accessors. Provider files include this header, allocate `struct ccp_ctx` as transform context, set the `complete` function during transform init, and place a `struct ccp_cmd` in each request context before calling `ccp_crypto_enqueue_request()`.

## State And Persistence Behavior

The header defines all long-lived crypto transform state for keys, HMAC pads, fallback transforms, and RSA key buffers, plus request-scoped state for IVs, hash buffers, temporary SG tables, and commands. It also defines export/import state for SHA and CMAC so partial hash operations can persist across Crypto API export/import calls.

## Dependencies And Integration Points

It depends on Linux lists/wait queues, `linux/ccp.h` command definitions, Crypto API headers for AES/AEAD/hash/SHA/RSA/skcipher, and provider files in the same module. It is the type contract between `ccp-crypto-main.c` and every algorithm implementation.

## Risks And Edge Cases

- `struct ccp_aes_req_ctx` keeps `skcipher_request fallback_req` at the end; XTS init sizes request memory to append fallback request private data after it.
- Context structs store sensitive key material; provider exit paths must clear or free sensitive data appropriately.
- Wrapper recovery helpers depend on Crypto API internal container layout and must match the algorithm type.
- DMA padding in `cra_ctxsize`/request sizing must stay consistent with `*_ctx_dma()` accessors.

## Test Signals

Compile coverage across all provider files is the primary signal. Runtime signals include no DMA alignment warnings, correct request-size handling for XTS fallback, export/import state compatibility, and memory-sanitizer checks for context/request overrun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-debugfs.c

## Purpose

`ccp-debugfs.c` exposes CCP v5 device information and per-device/per-queue statistics through debugfs when `CONFIG_CRYPTO_DEV_CCP_DEBUGFS` is enabled. It provides readouts for version, available engines, queue counts, LSB entries, interrupts, and operation counters, and allows stats reset by writing to debugfs files.

## Important APIs, Types, And Functions

- Register-info masks such as `RI_AES_PRESENT`, `RI_NUM_VQM`, and `RI_LSB_ENTRIES` decode `CMD5_PSP_CCP_VERSION`.
- `ccp5_debugfs_info_read()` formats device name, RNG name, queue/command counts, version, engine presence, hardware queue count, and LSB entries.
- `ccp5_debugfs_stats_read()` aggregates operation counters across queues.
- `ccp5_debugfs_reset_queue_stats()` clears one queue's counters.
- `ccp5_debugfs_stats_write()` clears all queue counters and total interrupts.
- `ccp5_debugfs_queue_read()` formats per-queue counters and enabled interrupt names.
- `ccp5_debugfs_queue_write()` resets one queue.
- `ccp5_debugfs_setup()` creates the root/module/device/queue debugfs hierarchy.
- `ccp5_debugfs_destroy()` removes the entire CCP debugfs tree.

## Control Flow

During v5 device init, `ccp5_debugfs_setup()` checks `debugfs_initialized()`, lazily creates the module root under a mutex, creates a per-device directory, adds `info` and `stats`, then creates `q<id>/stats` for every command queue. Reads allocate a small temporary buffer, format a snapshot with `scnprintf()`, return it through `simple_read_from_buffer()`, and free the buffer. Writes ignore user content and reset counters. Driver teardown calls `ccp5_debugfs_destroy()` when the last device is being removed.

## State And Persistence Behavior

Debugfs state consists of dentries and live counter values in `struct ccp_device`/`struct ccp_cmd_queue`. Counter resets mutate in-memory statistics only. There is no persistence across driver unload or reboot.

## Dependencies And Integration Points

This file depends on Linux debugfs, `simple_open`, `simple_read_from_buffer`, CCP v5 register offsets, and queue/device statistics maintained by v5 operation code. It is only compiled when debugfs support is enabled and called from `ccp-dev-v5.c`.

## Risks And Edge Cases

- Stats output labels include duplicate `SHA` lines, one of which prints `total_3des_ops`; this is likely a label bug and can mislead diagnostics.
- Reads snapshot counters without locking, so values can be slightly inconsistent during active operation.
- The destroy helper removes the whole root, so multi-device teardown ordering must ensure it is only called when appropriate.
- Debugfs exposes hardware feature and usage data; keeping it optional limits information exposure.

## Test Signals

Signals include debugfs tree creation under module root, correct info/version/engine fields on v5 hardware, stats counters increasing after AES/SHA/RSA/DMA workloads, reset-on-write behavior, per-queue files for all queues, and clean removal on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev-v3.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev-v3.c

## Purpose

`ccp-dev-v3.c` implements version 3 CCP hardware operations and device initialization. It allocates key storage blocks, converts generic `ccp_op` objects into v3 command request registers, handles queue interrupts, starts one kthread per hardware queue, registers the device/RNG/DMAengine, and tears all resources down on destroy.

## Important APIs, Types, And Functions

- `ccp_alloc_ksb()`/`ccp_free_ksb()` allocate/free contiguous key storage block entries from the global KSB bitmap.
- `ccp_get_free_slots()` reads queue depth from `CMD_Q_STATUS`.
- `ccp_do_cmd()` writes `CMD_REQ1..6`, then `CMD_REQ0`, waits for interrupts when needed, logs errors, deletes failed/stopped jobs, and refreshes free slots.
- `ccp_perform_aes()`, `ccp_perform_xts_aes()`, `ccp_perform_sha()`, `ccp_perform_rsa()`, `ccp_perform_passthru()`, and `ccp_perform_ecc()` fill v3 register command words for each engine.
- `ccp_irq_bh()` reads global IRQ status, updates per-queue status/error fields, acknowledges bits, and wakes queue waiters.
- `ccp_irq_handler()` disables interrupts and dispatches bottom-half work.
- `ccp_init()` discovers queues, allocates per-queue DMA pools, reserves per-queue KSBs, configures queue registers and interrupts, starts kthreads, registers the device, hwrng, and DMAengine.
- `ccp_destroy()` unregisters DMA/RNG/device, disables interrupts, stops kthreads, frees IRQ/pools, and completes queued commands with `-ENODEV`.
- `ccp3_actions`, `ccpv3_platform`, and `ccpv3` expose the v3 operation table and platform/PCI data.

## Control Flow

Device init reads the queue mask, allocates a DMA pool per available queue up to `max_q_count`, reserves two KSBs per queue for key/context use, programs per-queue status register addresses and interrupt masks, clears stale status, requests a CCP IRQ, starts queue kthreads, enables interrupts, adds the device to the global CCP list, registers hwrng, then registers DMAengine. Queue kthreads come from generic `ccp_cmd_queue_thread()` and call `ccp_run_cmd()`, which uses the vdata action table here.

For each operation, `ccp_perform_*()` encodes engine-specific fields into six request registers. `ccp_do_cmd()` serializes request-register access with `ccp->req_mutex`, writes request words, starts the command, and waits on `cmd_q->int_queue` when interrupt-on-completion is set. IRQ bottom-half records command errors and wakes waiters.

## State And Persistence Behavior

Persistent driver state includes per-queue DMA pools, KSB reservations, free slot counts, interrupt masks/status, command errors, wait queues, kthreads, and global KSB bitmap/wait queue. Hardware state is command request registers, delete-job register, IRQ mask/status, queue status, and optional ARM64 queue cache settings.

## Dependencies And Integration Points

This file depends on generic CCP device scheduling in `ccp-dev.c`, operation conversion in `ccp-ops.c`, SP IRQ helpers, DMA pools, hwrng and DMAengine registration. It integrates through `struct ccp_actions` selected by platform/PCI vdata.

## Risks And Edge Cases

- KSB allocation returns 0 on interrupted wait, which also represents "no allocation"; callers must treat 0 as failure.
- Register command submission is protected by one mutex because request registers are shared across queues.
- Reading queue depth resets some status information according to comments, so free-slot refresh is deliberately limited.
- Destroy completes queued and backlog commands with `-ENODEV`; active hardware commands are stopped by kthread/IRQ teardown ordering.
- DES3 is not supported in v3 action table, so higher-level registration must gate DES3 by version.

## Test Signals

Signals include v3 queue discovery, KSB allocation/free under concurrent AES/SHA/RSA workloads, IRQ wakeups, command error logging and delete-job behavior, suspend/resume through generic queue suspension, hwrng reads, DMAengine memcpy, and clean teardown with queued command callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev-v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev-v5.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev-v5.c

## Purpose

`ccp-dev-v5.c` implements version 5 CCP hardware operations. It replaces v3 request-register submission with DMA-backed descriptor queues, manages private/shared local storage block allocation, assigns LSB regions to hardware queues, handles v5 per-queue interrupts, initializes queue memory/registers, configures v5 variants, and registers device services.

## Important APIs, Types, And Functions

- `ccp_lsb_alloc()`/`ccp_lsb_free()` allocate contiguous LSB slots from a queue-private region first, then shared regions.
- `union ccp_function` and descriptor field macros encode v5 command function and `struct ccp5_desc` fields.
- `low_address()`, `high_address()`, and `ccp5_get_free_slots()` support descriptor queue addressing.
- `ccp5_do_cmd()` copies a descriptor into the queue ring, advances tail, starts the queue, and waits for completion/error interrupts when requested.
- `ccp5_perform_aes()`, `ccp5_perform_xts_aes()`, `ccp5_perform_sha()`, `ccp5_perform_des3()`, `ccp5_perform_rsa()`, `ccp5_perform_passthru()`, and `ccp5_perform_ecc()` fill v5 descriptors and update per-engine stats.
- `ccp_find_lsb_regions()`, `ccp_find_and_assign_lsb_to_q()`, and `ccp_assign_lsbs()` derive private/shared LSB allocation from hardware masks.
- `ccp5_irq_bh()` and `ccp5_irq_handler()` handle per-queue interrupt status.
- `ccp5_init()` performs v5 device initialization.
- `ccp5_destroy()` tears down v5 services and fails queued commands.
- `ccp5_config()` and `ccp5other_config()` configure public and NTB/other variants.
- `ccp5_actions`, `ccpv5a`, and `ccpv5b` expose v5 operation tables and vdata.

## Control Flow

Init reads `Q_MASK_REG` and treats `0xffffffff` as inaccessible hardware, often due to firmware/BIOS restrictions. For each available queue, it creates a DMA pool, initializes a mutex, allocates coherent descriptor ring memory, computes per-queue register pointers, and clears interrupts. It requests IRQ, optionally initializes a tasklet, copies private LSB masks to public registers, programs queue ring base/tail/head/control, discovers queue LSB access, assigns private/shared LSBs, preallocates key/context LSB slots, starts queue kthreads, enables interrupts, adds the device to the global list, registers RNG and DMAengine, and creates debugfs entries when configured.

Each operation builds a zeroed 8-dword descriptor, fills SOC/IOC/INIT/EOM/protection bits, engine and function fields, source/destination/key addresses and memory types, and optional LSB context ID. `ccp5_do_cmd()` endian-converts descriptor words into coherent ring memory, advances `qidx`, uses `wmb()`, writes the new tail, sets the run bit, and waits for an interrupt if IOC is set. On error it logs the CCP error and flushes by moving the head pointer to the submitted tail.

## State And Persistence Behavior

Driver state includes coherent descriptor queues, per-queue `qidx`, cached `qcontrol`, private LSB assignment, queue-private and device-shared LSB bitmaps, preallocated key/context slots, interrupt status/error fields, kthreads, DMA pools, statistics, and debugfs dentries. Hardware state includes queue control/head/tail/interrupt registers, LSB masks, queue masks/priorities, TRNG/AES mask configuration for v5b, and clock gating settings.

## Dependencies And Integration Points

This file depends on generic CCP scheduling in `ccp-dev.c`, SP IRQ helpers, hwrng/DMAengine registration, debugfs helpers, coherent DMA allocation, and operation setup from `ccp-ops.c`. It provides DES3 and SHA384/SHA512 capability used by crypto provider version gating.

## Risks And Edge Cases

- `ccp_lsb_free()` checks `cmd_q->lsb == start`, but allocated private slots are returned as `start + lsb * LSB_SIZE`; freeing private offsets other than the region base may follow the shared path.
- The LSB assignment algorithm is intentionally brute force and must handle constrained queue masks; bad masks can fail init.
- `ccp5_destroy()` calls `ccp5_debugfs_destroy()` when `ccp_present()` returns nonzero after deletion, which corresponds to no devices present; the condition is subtle.
- Descriptor queue uses one unused slot; free-slot math and qidx/head synchronization are critical under high concurrency.
- BIOS/device inaccessibility returns positive `1`, which the generic init treats as quiet nonfatal failure for the CCP portion.

## Test Signals

Signals include v5 queue discovery and descriptor ring operation, LSB private/shared allocation under concurrent AES/XTS/SHA/DES3/RSA/passthrough/ECC workloads, interrupt/error handling, debugfs stats increments, v5b setup register programming, inaccessible-device quiet failure, DMAengine registration, and clean teardown with queued callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev-v5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev.c

## Purpose

`ccp-dev.c` is the generic CCP device core. It maintains the global list of CCP devices, exports presence/version/enqueue APIs, schedules commands onto hardware queue kthreads, handles backlog and suspend/resume, allocates base device state, registers hwrng reads, and dispatches to version-specific vdata init/destroy operations.

## Important APIs, Types, And Functions

- Module parameters `nqueues` and `max_devs` limit queues per device and number of CCP devices initialized.
- `ccp_log_error()` maps hardware error codes to readable messages.
- `ccp_add_device()`/`ccp_del_device()` maintain the global device list and round-robin pointer.
- `ccp_present()` and `ccp_version()` are exported for crypto module feature gating.
- `ccp_enqueue_cmd()` chooses a device, applies queue/backlog limits, adds commands to active/backlog lists, and wakes idle queue threads.
- `ccp_do_cmd_backlog()` moves a backlogged command into the active queue and notifies it with `-EINPROGRESS`.
- `ccp_dequeue_cmd()` is used by queue threads to fetch work or enter suspended state.
- `ccp_cmd_queue_thread()` sleeps until woken, runs `ccp_run_cmd()`, and schedules callback completion via a tasklet.
- `ccp_alloc_struct()` allocates and initializes `struct ccp_device`.
- `ccp_trng_read()` implements hwrng reads from `TRNG_OUT_REG`.
- `ccp_queues_suspended()`, `ccp_dev_suspend()`, and `ccp_dev_resume()` coordinate queue thread suspension.
- `ccp_dev_init()` and `ccp_dev_destroy()` are SP-device lifecycle hooks.

## Control Flow

Generic init enforces `max_devs`, allocates a `ccp_device`, decides max queue count from module parameter, obtains vdata from the SP device, applies vdata setup, and calls the version-specific `perform->init()`. That version-specific init starts queue threads and adds the device to the global list. Commands submitted through `ccp_enqueue_cmd()` use a specific `cmd->ccp` if provided or a round-robin device otherwise. The command is either rejected, placed on backlog, or appended to the active command list. If a queue is idle and the device is not suspending, its kthread is woken.

Queue threads dequeue commands, call `ccp_run_cmd()` to translate and execute the command via vdata operations, then invoke the command callback from a tasklet and wait for that callback to finish before processing more work. Backlogged commands are moved to active via scheduled work so the caller first receives an `-EINPROGRESS` transition.

## State And Persistence Behavior

Global state includes `ccp_units`, `ccp_unit_lock`, `ccp_rr`, `ccp_rr_lock`, and `dev_count`. Per-device state includes active/backlog command lists, command count, queue threads, hwrng state, storage block state, suspend flags, and vdata. This is all runtime kernel state. `ccp_trng_read()` keeps a retry counter to distinguish temporary zero reads from persistent entropy failure.

## Dependencies And Integration Points

This file depends on SP-device bus glue, version-specific action tables, `linux/ccp.h` exported command structures, hwrng, kthreads, tasklets, and the lower `ccp_run_cmd()` operation converter from `ccp-ops.c`. It is consumed by `ccp_crypto` and DMAengine clients through exported command enqueue APIs.

## Risks And Edge Cases

- `max_devs=0` causes `ccp_dev_init()` to return success without initializing devices; consumers then see no present CCP.
- Queue callbacks are invoked from tasklet context; callbacks must respect atomic-context constraints unless the lower stack changes this behavior.
- Round-robin device selection uses locks correctly, but commands pinned to removed devices require external lifetime guarantees.
- Suspend waits for all queue threads to mark suspended; active long-running commands can delay suspend.
- Backlog movement uses work_struct embedded in `struct ccp_cmd`, so command memory must remain valid while backlogged.

## Test Signals

Signals include exported `ccp_present()`/`ccp_version()` behavior, round-robin distribution across devices, queue cap and backlog semantics, command callbacks on success/error/removal, suspend/resume under active load, hwrng zero retry handling, and module parameters `nqueues`/`max_devs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev.h

## Purpose

`ccp-dev.h` is the internal device-layer contract for AMD CCP hardware. It defines register offsets, bit encodings, queue/storage constants, software device/queue/DMA structures, workarea abstractions used by operation conversion, generic `ccp_op` fields, v5 descriptor layout, helper address accessors, lifecycle prototypes, and version action tables.

## Important APIs, Types, And Functions

- Register constants cover generic, v3, and v5 queue/control/TRNG/interrupt/LSB registers.
- Storage constants define v3 KSB and v5 LSB dimensions, per-operation storage block counts, RSA/ECC/PASSTHRU sizes, and DMA pool limits.
- `struct ccp_dma_cmd`, `ccp_dma_desc`, and `ccp_dma_chan` model DMAengine provider state.
- `struct ccp_cmd_queue` models one hardware queue, including v5 ring memory, storage block assignments, IRQ state, kthread state, MMIO register pointers, and per-engine stats.
- `struct ccp_device` is the top-level device state: SP device, IO registers, command/backlog lists, queues, hwrng, DMAengine, storage block bitmaps, suspend state, axcache, stats, and debugfs.
- `struct ccp_dma_info`, `ccp_dm_workarea`, `ccp_sg_workarea`, `ccp_data`, and `ccp_mem` describe DMA buffers and workareas used by operation setup.
- `struct ccp_aes_op`, `ccp_xts_aes_op`, `ccp_des3_op`, `ccp_sha_op`, `ccp_rsa_op`, `ccp_passthru_op`, `ccp_ecc_op`, and `ccp_op` are normalized operation descriptions consumed by v3/v5 action tables.
- `struct ccp5_desc` and nested dword structs describe the v5 8-dword command descriptor.
- `struct ccp_actions` is the version-specific operation table.

## Control Flow

The header has no main control flow. It enables the generic scheduler to hold `struct ccp_cmd_queue` and `struct ccp_device`, the operation layer to build `struct ccp_op`, and v3/v5 files to implement the `ccp_actions` callbacks. Inline `ccp_addr_lo()` and `ccp_addr_hi()` convert DMA workarea addresses plus offsets into hardware command fields.

## State And Persistence Behavior

The definitions in this header describe nearly all persistent runtime CCP device state: command queues, lists, bitmaps, wait queues, kthreads, tasklets, DMA caches, hwrng state, suspend state, and debugfs handles. Hardware-visible descriptor and command state is represented by `ccp5_desc` and `ccp_op`.

## Dependencies And Integration Points

This header depends on Linux device, locking, list, wait, DMA, dmaengine, hwrng, interrupt, bitops, and SP-device definitions. It is included by generic device, v3/v5 device, debugfs, DMAengine, and operation conversion code.

## Risks And Edge Cases

- The macro `#define CCP_MEMTYPE_LSB CCP_MEMTYPE_KSB` references `CCP_MEMTYPE_KSB`, which is not an enum member in the visible code; this looks stale or typo-prone unless defined elsewhere before use.
- v5 descriptor bitfields assume compiler layout compatible with the hardware command format after explicit little-endian word conversion.
- Queue and device structures are cacheline-aligned in places; moving fields can affect contention.
- The header exposes many constants used across files; changing storage block sizes or register offsets has broad blast radius.

## Test Signals

Signals include full driver build across v3/v5/debugfs/DMAengine configs, sparse/endian checks for descriptors, operation tests for every engine, stress tests for storage block allocation, and ABI review against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dmaengine.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dmaengine.c

## Purpose

`ccp-dmaengine.c` exposes CCP passthrough operations as a DMAengine memcpy/interrupt provider. It creates one DMA channel per CCP command queue, converts DMA memcpy descriptors into one or more passthrough no-DMA-map CCP commands, manages DMAengine descriptor lifecycle/cookies/status, supports pause/resume/terminate, and registers/unregisters the DMA device.

## Important APIs, Types, And Functions

- Module parameters `dma_chan_attr` and `dmaengine` control channel visibility and whether DMAengine registration occurs.
- `ccp_get_dma_chan_attr()` resolves public/private channel flags from module parameter or vdata default.
- `ccp_free_cmd_resources()`, `ccp_free_desc_resources()`, and `ccp_free_chan_resources()` release command/descriptor lists.
- `ccp_cleanup_desc_resources()` and `ccp_do_cleanup()` free acknowledged completed descriptors from a tasklet.
- `ccp_issue_next_cmd()` submits the first pending CCP command for a DMA descriptor.
- `ccp_handle_active_desc()` advances command and descriptor completion, completes cookies, unmaps descriptors, invokes callbacks, and runs dependencies.
- `__ccp_pending_to_active()` moves submitted DMA descriptors into active state.
- `ccp_cmd_callback()` handles CCP command completion and issues the next command/descriptor.
- `ccp_tx_submit()`, `ccp_prep_dma_memcpy()`, `ccp_prep_dma_interrupt()`, `ccp_issue_pending()`, `ccp_tx_status()`, `ccp_pause()`, `ccp_resume()`, and `ccp_terminate_all()` implement DMAengine channel operations.
- `ccp_dmaengine_register()` allocates channels/caches, configures `struct dma_device`, and calls `dma_async_device_register()`.
- `ccp_dmaengine_unregister()` releases channels, unregisters the DMA device, and destroys caches.

## Control Flow

Registration exits early if `dmaengine=0`. Otherwise it allocates channel array, command and descriptor slab caches, configures source/destination address widths from the DMA mask, sets `DMA_MEMCPY` and `DMA_INTERRUPT`, optionally marks channels private, initializes one channel per CCP queue, and registers the DMA device.

`prep_dma_memcpy()` wraps source and destination DMA addresses in one-entry SGs and calls `ccp_create_desc()`. Descriptor creation walks source and destination SGs in lockstep, splitting at SG boundaries, and creates a passthrough command for every segment with `CCP_CMD_PASSTHRU_NO_DMA_MAP`, no bit modification or byte swap, source/destination DMA addresses, length, final flag, and callback. Submit moves the descriptor to channel pending. `issue_pending()` splices pending descriptors to active and triggers `ccp_cmd_callback(desc, 0)` to start processing.

Each lower CCP command completion frees the active command, either issues the next segment command or completes the DMA descriptor, then moves to the next active descriptor unless paused. Descriptor completion updates DMA cookie state, unmaps descriptor resources, invokes client callback, and runs dependencies.

## State And Persistence Behavior

Device state includes DMA device registration, per-queue DMA channels, slab caches, and channel lists (`created`, `pending`, `active`, `complete`) protected by spinlocks. Descriptor state stores DMAengine status, cookie, length, pending/active CCP commands, and callbacks. Completed descriptors remain on `complete` until acknowledged and cleaned by tasklet.

## Dependencies And Integration Points

This file depends on Linux DMAengine APIs, DMA mapping metadata, CCP command enqueue API, passthrough no-map command support in `linux/ccp.h`/operation layer, and queue count from `struct ccp_device`. It is called from v3/v5 device init/destroy.

## Risks And Edge Cases

- `GFP_NOWAIT` allocations in prep paths can fail under pressure, returning no descriptor.
- Pause and terminate contain TODOs about waiting for active DMA; active hardware commands may still complete after state changes.
- `ccp_prep_dma_interrupt()` creates a descriptor with no pending CCP commands; issue/completion behavior relies on the descriptor handling path accepting empty descriptors.
- Terminate frees active/pending/created descriptors but leaves complete descriptors unless acknowledged cleanup runs.
- Channel public/private visibility can be overridden globally, which may expose DMA channels not intended by platform vdata.

## Test Signals

Signals include DMAengine memcpy correctness for single and multi-SG transfers, cookie/status transitions, client callback invocation and dependency running, pause/resume behavior, terminate under active load, private/public channel attributes, `dmaengine=0` behavior, allocation failure handling, and module unload with clients attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-dmaengine.c -->
