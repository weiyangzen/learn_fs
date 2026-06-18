# Research: subset-b-001235

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport.c

## Purpose
`adf_transport.c` implements the QAT ETR transport ring manager. It allocates coherent DMA rings, reserves ring slots inside banks, programs CSR ring base/config/head/tail registers, dispatches responses to service callbacks, initializes per-bank interrupt/coalescing state, and tears the transport down for a QAT acceleration device.

## Important APIs, Types, And Functions
The exported API is `adf_init_etr_data()`, `adf_cleanup_etr_data()`, `adf_create_ring()`, `adf_remove_ring()`, `adf_send_message()`, `adf_ring_nearly_full()`, and `adf_response_handler()`. Internal helpers include `adf_verify_ring_size()`, `adf_reserve_ring()`, `adf_init_ring()`, `adf_handle_response()`, `adf_init_bank()`, and `cleanup_bank()`. The file operates on `struct adf_etr_data`, `struct adf_etr_bank_data`, and `struct adf_etr_ring_data` from `adf_transport_internal.h`.

## Control Flow
`adf_init_etr_data()` allocates the transport root, allocates one bank structure per hardware bank, creates a `transport` debugfs directory, obtains the ETR CSR base, and initializes each bank. Bank initialization clears all ring CSRs, allocates ring metadata, shares the `inflights` counter between paired TX/RX rings using the device `tx_rx_gap`, chooses coalescing timers from config, installs debugfs, clears interrupt flags, and programs interrupt source selection.

`adf_create_ring()` validates bank, message size, configured ring number, and in-flight capacity, reserves the ring in the bank mask, fills ring metadata, allocates and initializes the DMA ring, enables hardware arbitration, creates debugfs, and optionally enables ring IRQs. `adf_send_message()` increments the shared in-flight counter, copies the firmware request into the ring tail slot, advances tail by message size modulo ring size, and writes the tail CSR. Responses are scanned until `ADF_RING_EMPTY_SIG`; each message calls the ring callback, decrements in-flight count, clears the slot, advances head, and finally writes the head CSR. `adf_response_handler()` processes non-empty IRQ-enabled rings and re-enables interrupt/coalescing flags. Removal disables IRQs and arbitration, clears CSRs, removes debugfs, unreserves the ring, and frees DMA memory.

## State And Persistence Behavior
All state is volatile kernel memory plus device CSRs. `accel_dev->transport` persists from transport init to cleanup. Banks persist with ring masks, IRQ masks, coalescing timers, CSR bases, debugfs dentries, and ring arrays. Rings persist with DMA base, DMA address, head/tail, thresholds, callback, lock, and shared in-flight counter. Ring contents are initialized and reset to `0x7f` so `ADF_RING_EMPTY_SIG` marks free response slots. There is no disk persistence.

## Dependencies And Integration Points
The file depends on hardware CSR operations from `GET_CSR_OPS()`, device-specific ring masks/gaps, `adf_cfg` configuration keys, debugfs helpers, DMA coherent allocation, QAT arbitration via `adf_update_ring_arb()`, and ISR/tasklet code that invokes `adf_response_handler()`. Crypto, compression, PKE, and admin clients create rings and submit 32/64/128-byte firmware requests through this layer.

## Risks
Ring sizing and alignment are hardware contracts; a wrong conversion can produce invalid modulo math or DMA base alignment failures. `atomic_t *inflights` is shared between TX/RX pairs, so incorrect `tx_rx_gap` or mask setup corrupts flow control. The response loop trusts callbacks and ring empty signatures; stale or malformed ring memory can stall processing. Error handling in bank cleanup is sensitive because allocated `inflights` exist only for TX rings. `adf_cleanup_etr_data()` also frees `etr_data->banks->rings` after per-bank cleanup has already freed each bank's rings, which is a notable double-free risk in this source snapshot.

## Test Signals
Useful signals are successful QAT probe, transport debugfs directories per bank/ring, valid ring head/tail movement, no DMA mapping/alignment errors, and successful crypto/compression request completions. Stress tests should cover full rings, backlog behavior, interrupt and polling modes, invalid config ring numbers, probe failure cleanup, repeated ring create/remove, and response handling under high concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport.h

## Purpose
`adf_transport.h` is the public transport ring interface for QAT common code. It hides the internal ETR ring layout and exposes ring creation, message submission, flow-control checks, and ring removal to crypto, compression, and administrative users.

## Important APIs, Types, And Functions
The file forward-declares `struct adf_etr_ring_data`, defines `adf_callback_fn` as the response callback type, and declares `adf_create_ring()`, `adf_ring_nearly_full()`, `adf_send_message()`, and `adf_remove_ring()`. `adf_create_ring()` binds an accelerator, config section, bank, message count, message size, ring-name config key, callback, polling mode, and output ring pointer.

## Control Flow
The header has no executable control flow. It defines the contract consumed by service code: create a ring after transport initialization, submit firmware request messages with `adf_send_message()`, optionally use `adf_ring_nearly_full()` for backlog decisions, and remove the ring during service/device teardown.

## State And Persistence Behavior
The header exposes opaque ring state only by pointer. Ring lifetime and DMA resources are owned by `adf_transport.c`; clients persist only the returned pointer while the accelerator device and service are active.

## Dependencies And Integration Points
It includes `adf_accel_devices.h` and is used by `qat_algs_send.c`, VF/PF service setup, and QAT service code that needs TX/RX transport rings. The callback type integrates hardware response delivery with service-specific completion handlers such as symmetric, asymmetric, and compression callbacks.

## Risks
The API does not encode ownership or lifetime in types, so callers must not use a ring after service/device removal. `adf_send_message()` accepts a raw `u32 *` and assumes the message size matches the ring's configured firmware request width. Callback implementations must be safe in bottom-half/response context.

## Test Signals
Compile coverage should catch missing declarations. Runtime validation comes from service ring creation, correct `-EAGAIN`/`-ENOSPC` propagation through submit helpers, and callback delivery for each QAT service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_access_macros.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_access_macros.h

## Purpose
`adf_transport_access_macros.h` centralizes constants and conversion macros for QAT ETR ring configuration. It translates compact hardware ring/message-size encodings into byte counts, builds ring config CSR values, defines watermarks and coalescing limits, and computes the maximum number of in-flight requests.

## Important APIs, Types, And Functions
Important constants include ring size encodings from `ADF_RING_SIZE_128` to `ADF_RING_SIZE_4M`, message sizes `ADF_MSG_SIZE_32/64/128`, `ADF_RING_EMPTY_SIG`, coalescing min/default/max values, and near-full/near-empty watermark values. Key macros are `ADF_MSG_SIZE_TO_BYTES()`, `ADF_BYTES_TO_MSG_SIZE()`, `ADF_SIZE_TO_RING_SIZE_IN_BYTES()`, `ADF_RING_SIZE_BYTES_MIN()`, `ADF_RING_SIZE_MODULO()`, `ADF_SIZE_TO_POW()`, `ADF_MAX_INFLIGHTS()`, `BUILD_RING_CONFIG()`, and `BUILD_RESP_RING_CONFIG()`.

## Control Flow
The file is macro-only. `adf_transport.c` uses the conversions when validating create-ring parameters, allocating DMA ring memory, moving head/tail pointers, building CSR config words, and computing near-full thresholds.

## State And Persistence Behavior
No runtime state is owned here. The constants define how transport code interprets ring metadata fields stored in `struct adf_etr_ring_data` and programmed into hardware CSRs.

## Dependencies And Integration Points
It includes `adf_accel_devices.h` and is tightly coupled to CSR operations and firmware request sizing. ISR, debugfs, and send paths all rely on the same byte/encoding conversions to agree on ring offsets.

## Risks
These macros are hardware contract code; off-by-one, endian, or shift mistakes affect all ring users. `ADF_RING_SIZE_IN_BYTES_TO_SIZE()` appears suspicious because it shifts `1 << (SIZE - 1)` rather than deriving an encoding from a byte size; current users rely mostly on the forward conversion. `ADF_MAX_INFLIGHTS()` must stay consistent with firmware ring capacity or flow control can overrun ring slots.

## Test Signals
Ring creation with each message size, ring debugfs size reporting, full-ring pressure tests, and CSR dumps provide validation. Static review should include macro expansion for 32/64/128-byte messages and 4K/16K ring defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_access_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_debug.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_debug.c

## Purpose
`adf_transport_debug.c` provides debugfs inspection for QAT ETR banks and rings. It exposes per-ring configuration and raw ring data dumps plus per-bank head/tail/empty summaries.

## Important APIs, Types, And Functions
The exported internal debugfs hooks are `adf_ring_debugfs_add()`, `adf_ring_debugfs_rm()`, `adf_bank_debugfs_add()`, and `adf_bank_debugfs_rm()`. Seq-file operations are implemented by `adf_ring_start/next/show/stop()` and `adf_bank_start/next/show/stop()`. The ring debug entry stores the human-readable ring name and debugfs dentry in `struct adf_etr_ring_debug_entry`.

## Control Flow
Bank debugfs creation makes `transport/bank_%02d/config`. Ring debugfs creation adds `ring_%02d` under the bank directory and records the configured ring name. Reading a ring file locks `ring_read_lock`, emits a header with ring name, bank/ring number, CSR head/tail, empty status, ring and message sizes, then hex-dumps each message slot. Reading a bank config locks `bank_read_lock`, emits a bank header, skips unreserved rings, and reports head/tail/empty state for active rings.

## State And Persistence Behavior
Debug state is runtime-only. Each active ring owns an allocated debug entry; each bank stores debugfs dentries. The seq readers inspect live coherent DMA ring memory and live CSRs, so output changes as hardware and callbacks advance rings.

## Dependencies And Integration Points
The file depends on debugfs, seq_file, transport internals, CSR operations, and transport conversion macros. It is called only from transport bank/ring create and cleanup paths, and becomes a diagnostic integration point for QAT services using ETR rings.

## Risks
Ring dumping exposes raw firmware messages to privileged debugfs readers; this may include addresses or request metadata. The global read mutexes serialize reads but do not freeze hardware updates, so dumps can be a live snapshot rather than a coherent transaction. `adf_bank_show()` casts `loff_t *pos` to `int *`, which is fragile across type sizes and can misreport on unusual architectures.

## Test Signals
With `CONFIG_DEBUG_FS`, probe should create transport bank directories and ring files. Reading ring files should show correct head/tail progression and no crashes under concurrent traffic. Removal should clean dentries without leaks or use-after-free warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_internal.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_internal.h

## Purpose
`adf_transport_internal.h` defines the private ETR transport structures shared by transport implementation, debugfs, and ISR code. It is the concrete layout behind the opaque `adf_etr_ring_data` public pointer.

## Important APIs, Types, And Functions
`struct adf_etr_ring_data` stores coherent ring base, shared in-flight counter, callback, parent bank, DMA address, optional debug entry, spinlock, head/tail, threshold, ring number, ring size encoding, and message size encoding. `struct adf_etr_bank_data` stores ring array, response tasklet, CSR base, coalescing timer, bank number, ring/IRQ masks, lock, accelerator pointer, and debugfs dentries. `struct adf_etr_data` stores all banks and the transport debugfs root. It declares `adf_response_handler()` and debugfs add/remove functions with no-op stubs when debugfs is disabled.

## Control Flow
The header has no runtime control flow but defines lifecycle ownership. Transport init allocates `adf_etr_data`, banks, and ring arrays; create-ring fills individual ring records; ISR code schedules bank response handlers; debugfs code inspects the same structures; cleanup frees and clears them.

## State And Persistence Behavior
The structures are volatile per-device transport state. Ring head/tail are software mirrors of CSR positions. `inflights` persists for a TX/RX pair and is decremented in response handling. `ring_mask` and `irq_mask` are protected by bank lock and define reserved and interrupt-enabled rings.

## Dependencies And Integration Points
The header includes interrupt/tasklet and spinlock types plus the public transport header. It integrates transport with `adf_vf_isr.c`, PF/MSI-X ISR code outside this subset, and all QAT service users that keep ring pointers.

## Risks
Concurrency depends on using the correct lock: bank masks use the bank lock and ring head/tail use the ring lock in send paths, while response paths update head without the ring send lock. Structure layout is used by debugfs and cleanup, so ownership mistakes can leak or double-free ring debug entries, `inflights`, or ring arrays.

## Test Signals
Build coverage validates debugfs stub selection. Runtime stress of create/remove, interrupt response, and debugfs reads validates structure lifetime and lock coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_transport_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_vf_isr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_vf_isr.c

## Purpose
`adf_vf_isr.c` implements interrupt resources for QAT virtual functions. It enables MSI, handles VF interrupt source bits for bundle and PF-to-VF messages, schedules bottom halves, and coordinates asynchronous VF shutdown/restart when the PF reports a restart.

## Important APIs, Types, And Functions
Exported functions are `adf_enable_pf2vf_interrupts()`, `adf_disable_pf2vf_interrupts()`, `adf_pf2vf_handle_pf_restarting()`, `adf_vf_isr_resource_alloc()`, `adf_vf_isr_resource_free()`, `adf_flush_vf_wq()`, `adf_init_vf_wq()`, and `adf_exit_vf_wq()`. Important internals are `adf_isr()`, `adf_pf2vf_bh_handler()`, `adf_setup_pf2vf_bh()`, `adf_setup_bh()`, `adf_request_msi_irq()`, and `adf_dev_stop_async()`. `struct adf_vf_stop_data` carries deferred stop work.

## Control Flow
Resource allocation enables one MSI vector, initializes the PF2VF tasklet and VF2PF lock, initializes the transport bank response tasklet, and requests the IRQ. The top-half reads `ADF_VINTSOU`, masks it with `ADF_VINTMSK`, disables PF2VF interrupts and schedules the PF2VF tasklet when a PF message arrives, and disables bundle interrupts plus schedules bank 0 response handling when ring responses arrive. The PF2VF bottom half receives and handles messages and re-enables PF2VF interrupts if handling is complete. A PF-restarting message clears PF-running status and queues work that notifies restart, calls `adf_dev_down()`, re-enables PF2VF interrupts, notifies restart completion, and frees work data.

## State And Persistence Behavior
The global `adf_vf_stop_wq` persists from module init to exit. Per-device VF state includes tasklets, the IRQ name, IRQ enabled flag, VF2PF lock, and status bits. MSI affinity is hinted to a CPU derived from accelerator ID. No persistent storage is used.

## Dependencies And Integration Points
The file depends on PCI MSI APIs, tasklets, workqueues, PF/VF message helpers, transport bank response handling, accelerator lifecycle helpers (`adf_dev_down`, restart notifications), and CSR access to the PMISC BAR. It is the VF-specific bridge between hardware interrupt sources and QAT common transport/service callbacks.

## Risks
Top-half masking is essential; failure to disable PF2VF or bundle sources can reschedule already pending work. VF restart handling runs asynchronously and interacts with device teardown, so lifetime of `accel_dev` and workqueue flushing matters. Only bank 0 is scheduled for bundle interrupts in this VF path, which must match VF hardware exposure. Error unwinding in resource allocation must reverse tasklet/MSI setup exactly.

## Test Signals
VF probe should allocate MSI and request IRQ. PF2VF messages should be handled once and re-enable interrupts. Ring completions should drain through `adf_response_handler()`. Restart tests should show VF down/restart-complete notification, no workqueue leaks, and clean IRQ free on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_vf_isr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw.h

## Purpose
`icp_qat_fw.h` defines common QAT firmware request/response ABI structures and bitfield helpers shared by symmetric crypto, compression, PKE, DMA, and admin services.

## Important APIs, Types, And Functions
Important types include `struct icp_qat_fw_comn_req_hdr`, `icp_qat_fw_comn_req_hdr_cd_pars`, `icp_qat_fw_comn_req_mid`, `icp_qat_fw_comn_req_cd_ctrl`, `icp_qat_fw_comn_req`, `icp_qat_fw_comn_resp_hdr`, and `icp_qat_fw_comn_resp`. Enums define common service/request IDs and slice IDs. Macros include `QAT_FIELD_SET()`, `QAT_FIELD_GET()`, common header valid/CNV/CNVNR flags, pointer/content descriptor flag builders, current/next slice ID accessors, and response status builders/getters.

## Control Flow
The header is declarative. Runtime code fills a request header, content descriptor parameters, mid fields with source/destination/opaque data, service-specific request parameters, and content descriptor controls. Firmware returns a common response header plus opaque data, which service callbacks use to recover request context and decode status/error bits.

## State And Persistence Behavior
No state is owned here. The structures are transient firmware messages in ring DMA memory or per-request software buffers. The layout is effectively persistent ABI between driver and firmware versions.

## Dependencies And Integration Points
It includes `icp_qat_hw.h` for hardware enums and is included by service-specific firmware headers (`icp_qat_fw_la.h`, `icp_qat_fw_comp.h`, `icp_qat_fw_pke.h`, admin headers) and request-building code. The common opaque pointer field is central to async completion routing.

## Risks
Structure packing, field sizes, and bit positions must match firmware exactly. `QAT_FIELD_SET()` is a statement macro that mutates its first argument and can surprise callers if used with expressions. Status bits use inverted meanings in some contexts (`OK` is zero), so callbacks must use the correct service-specific getter. ABI drift can silently corrupt hardware requests.

## Test Signals
Compile-time ABI checks are limited, so runtime firmware selftests, request completions across all services, and decoded firmware errors are primary signals. Tests should cover SGL versus flat pointer flags and all common response status paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_comp.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_comp.h

## Purpose
`icp_qat_fw_comp.h` defines the firmware ABI for QAT compression/decompression requests and responses, including deflate, LZ4/LZ4S, and zstd command IDs, session/request flags, content descriptor headers, state layouts, CRC data, and response counters.

## Important APIs, Types, And Functions
Key enums are `icp_qat_fw_comp_cmd_id`, `icp_qat_fw_comp_20_cmd_id`, and `icp_qat_fw_comp_bank_enabled`. Important structures include `icp_qat_fw_comp_req_params`, `icp_qat_fw_xlt_req_params`, `icp_qat_fw_comp_cd_hdr`, `icp_qat_fw_xlt_cd_hdr`, `icp_qat_fw_comp_req`, `icp_qat_fw_resp_comp_pars`, `icp_qat_fw_comp_state`, `icp_qat_fw_comp_resp`, `icp_qat_fw_comp_crc_data_struct`, and `xxhash_acc_state_buff`. Macros build and extract session flags, SOP/EOP/BFINAL/CNV/CRC/xxhash/append/drop/partial-decompress request flags, CNV error types, and RAM bank flags.

## Control Flow
The header itself has no control flow. `qat_comp_req.h` and compression context builders copy request templates, fill `comn_mid`, set `comp_len` and output buffer size, and read response counters/status/error codes through this ABI. Firmware consumes request flags to determine compression direction, stream framing, checksum behavior, and optional translator/intermediate buffer usage.

## State And Persistence Behavior
The structures describe per-request message state and optional stateful compression context state. In this driver subset, `qat_comp_algs.c` uses stateless requests but still relies on template context built elsewhere. Response counters persist only until the async completion callback updates `acomp_req->dlen`.

## Dependencies And Integration Points
The file includes `icp_qat_fw.h` and is used by `qat_comp_req.h`, `qat_comp_algs.c`, and device-specific compression context builders. It integrates with the Linux async compression API through the produced/consumed counters and firmware error/status fields.

## Risks
Flag bitfields are dense and version-sensitive. A wrong SOP/EOP/BFINAL/CNV setting can produce invalid streams or disable verified compression. Output overflow is reported through firmware status/errors and must map correctly to `-E2BIG`. End-to-end CRC and xxhash fields require consistent DMA-visible state if enabled.

## Test Signals
Deflate, LZ4S-zstd, and native zstd compression/decompression tests should validate status, produced counters, overflow behavior, CNV flags, and checksum modes. Hardware firmware traces or debug logs should show expected command IDs and request parameter flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_comp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_init_admin.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_init_admin.h

## Purpose
`icp_qat_fw_init_admin.h` defines QAT initialization/admin firmware commands and response layouts. It covers AE initialization, TRNG, constants, heartbeat, capability queries, rate limiting, telemetry, power-management state, counters, CNV stats, secure version number operations, and firmware status.

## Important APIs, Types, And Functions
The main command enum is `icp_qat_fw_init_admin_cmd_id`; response statuses are in `icp_qat_fw_init_admin_resp_status`. Important structures are `icp_qat_fw_init_admin_req`, `icp_qat_fw_init_admin_resp`, `icp_qat_fw_init_admin_slice_cnt`, `icp_qat_fw_init_admin_sla_config_params`, `icp_qat_fw_init_admin_tl_rp_indexes`, and `icp_qat_fw_init_admin_pm_info`. Compatibility aliases map sync/capability command names.

## Control Flow
No executable control flow exists here. Admin code builds a packed request with command ID, optional configuration size/pointer, opaque data, and command-specific union payload. Firmware returns a packed response with status, command ID, opaque data, and a union chosen by command, such as firmware version, counters, crypto/compression capabilities, timestamp, slice counts, SVN status, or PM info.

## State And Persistence Behavior
The header defines transient admin messages and returned telemetry snapshots. Some commands affect firmware/device state, such as heartbeat timer, rate-limit entries, telemetry start/stop, power-management configuration, and SVN commit. The C structures themselves do not persist outside caller-owned buffers.

## Dependencies And Integration Points
It includes the common firmware ABI and is used by QAT admin/firmware-management paths. Capability bits returned here influence which crypto/compression algorithms are registered and which device features are exposed.

## Risks
The packed request/response unions must be interpreted only with the matching command ID. New command IDs above the classic range, such as PM, rate limiting, telemetry, and SVN, make version/capability checks important. Misinterpreting capability fields can register unsupported algorithms or miss supported ones.

## Test Signals
Admin heartbeat/status/counter queries, firmware version reporting, crypto/compression capability reads, PM info reads, and rate-limit/telemetry command handling provide validation. Negative tests should cover unsupported-command and retry statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_init_admin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_la.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_la.h

## Purpose
`icp_qat_fw_la.h` defines the lookaside crypto firmware ABI for bulk cipher, auth, cipher-hash, hash-cipher, TRNG, key-derive, MGF1, and precompute requests. It supplies request layouts, content descriptor control headers, service-specific flags, cipher/auth parameter blocks, and response layout.

## Important APIs, Types, And Functions
Key command IDs are in `icp_qat_fw_la_cmd_id`. Important structures include `icp_qat_fw_la_bulk_req`, `icp_qat_fw_cipher_req_hdr_cd_pars`, `icp_qat_fw_cipher_auth_req_hdr_cd_pars`, `icp_qat_fw_cipher_cd_ctrl_hdr`, `icp_qat_fw_auth_cd_ctrl_hdr`, `icp_qat_fw_cipher_auth_cd_ctrl_hdr`, `icp_qat_fw_la_cipher_req_params`, `icp_qat_fw_la_auth_req_params`, and `icp_qat_fw_la_resp`. Macros build and mutate LA flags for IV pointer/data mode, content descriptor offset, partial state, protocol, auth compare/return, digest-in-buffer, update-state, ZUC/GCM, and slice type.

## Control Flow
Runtime users build a common bulk request, choose a command (`CIPHER`, `CIPHER_HASH`, or `HASH_CIPHER` in this subset), fill content descriptor address and size, program current/next slice IDs, fill cipher/auth request parameters, and submit through transport. Completion decodes the common crypto status from `icp_qat_fw_la_resp`.

## State And Persistence Behavior
The header owns no state. It defines firmware-visible request fields copied into per-request buffers and content descriptor control fields that describe caller-owned DMA content descriptors. For multi-part operations, partial/update flags can represent firmware state progression, though this subset mainly uses non-partial requests.

## Dependencies And Integration Points
It includes `icp_qat_fw.h` and is consumed by `qat_algs.c` for AEAD and skcipher request setup. It bridges Linux Crypto API parameters, QAT hardware cipher/auth setup blocks from `icp_qat_hw.h`, and ETR transport messages.

## Risks
The hash/cipher control headers overlap in the same request `cd_ctrl` memory, so offsets and current/next IDs must match the chosen command chain. Packed auth params require exact offsets. Incorrect digest-in-buffer or compare-auth flags can turn encryption into invalid authentication behavior. AES-GCM/CCM AAD limit constants are protocol-specific.

## Test Signals
Crypto selftests for authenc HMAC-CBC-AES and AES CBC/CTR/XTS validate request parameters and response status handling. Descriptor dumps should show correct slice chains: cipher->auth for encrypt and auth->cipher for decrypt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_la.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_loader_handle.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_loader_handle.h

## Purpose
`icp_qat_fw_loader_handle.h` defines top-level state objects used by the QAT firmware loader and HAL. It captures per-AE loader state, chip capability/register metadata, MMIO mappings, object handles, and firmware DRAM descriptors.

## Important APIs, Types, And Functions
Important structures are `icp_qat_fw_loader_ae_data`, `icp_qat_fw_loader_hal_handle`, `icp_qat_fw_loader_chip_info`, `icp_qat_fw_loader_handle`, and `icp_firml_dram_desc`. Fields track AE masks, admin AE masks, slice masks, revision, ustore sizes, reset delays, local memory size, reset/clock/FCU CSR offsets, firmware-authentication features, CSS variant flags, PCI device, UOF/SUOF/MOF object handles, and mapped SRAM/CAP/EP CSR regions.

## Control Flow
The header has no executable control flow. Loader code initializes these structures, maps MMIO regions, parses firmware objects, configures chip-specific CSR offsets, loads/authenticates firmware through HAL/FCU paths, and frees mappings during teardown.

## State And Persistence Behavior
The handle persists for the firmware loading lifetime of an accelerator. AE data records free ustore ranges, live contexts, and AE state. Chip info is effectively static per hardware generation. DRAM descriptors persist while firmware image staging memory is allocated.

## Dependencies And Integration Points
It includes `icp_qat_uclo.h` for firmware object structures and is included by `icp_qat_hal.h`. It integrates PCI, MMIO CSR access, firmware object parsing, authentication, and accelerator engine state management.

## Risks
Chip-specific offsets and flags must match hardware generation; wrong values can reset or program the wrong CSR. AE masks and ustore sizes gate firmware placement, so inconsistencies can corrupt AE instruction store. Firmware authentication flags (`fw_auth`, `css_3k`, `dual_sign`) must align with the image format.

## Test Signals
Firmware load success, AE live context masks, authenticated image status, FCU load/auth completion, and unload/reload cycles validate these structures. Multi-generation tests should cover classic, 4xxx/6xxx, CSS 2K/3K, and dual-sign firmware metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_loader_handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_pke.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_pke.h

## Purpose
`icp_qat_fw_pke.h` defines the public-key-engine firmware ABI used by RSA and Diffie-Hellman acceleration. It describes PKE request headers, source/destination parameter-table pointers, response headers, and status/valid flag helpers.

## Important APIs, Types, And Functions
Important structures are `icp_qat_fw_req_hdr_pke_cd_pars`, `icp_qat_fw_req_pke_mid`, `icp_qat_fw_req_pke_hdr`, `icp_qat_fw_pke_request`, `icp_qat_fw_resp_pke_hdr`, and `icp_qat_fw_pke_resp`. Macros include `ICP_QAT_FW_PKE_HDR_VALID_FLAG_SET()` and `ICP_QAT_FW_PKE_RESP_PKE_STAT_GET()`.

## Control Flow
PKE users zero a request, set the valid header flag, set service type to PKE, choose a firmware function ID, point `src_data_addr` and `dest_data_addr` at DMA parameter tables, set input/output parameter counts, store an opaque request pointer, and submit through a PKE transport ring. The callback decodes PKE status from response flags and uses the opaque value to complete the Crypto API request.

## State And Persistence Behavior
The header owns no state. Request and response structures are transient ring messages. Parameter tables and key buffers are caller-owned DMA mappings that must remain valid until callback completion.

## Dependencies And Integration Points
It includes `icp_qat_fw.h` and is used by `qat_asym_algs.c` for RSA encrypt/decrypt and DH public/shared-secret operations. It integrates the Linux akcipher/KPP APIs with QAT PKE firmware function IDs.

## Risks
PKE status is embedded in a common-response byte shifted out of `comn_resp_flags`, so decoding must use the PKE-specific macro. Parameter counts and table terminators must match the chosen firmware function ID or firmware will read bad addresses. The ABI assumes 64-bit DMA addresses in flat pointer tables.

## Test Signals
RSA and DH Crypto API selftests across supported key sizes should show valid PKE statuses. Negative tests should cover unsupported key sizes, too-small destination buffers, malformed keys, and firmware error responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_pke.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hal.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hal.h

## Purpose
`icp_qat_hal.h` defines low-level QAT accelerator-engine and firmware-control-unit CSR offsets, status/command enums, bit masks, timing constants, MMIO address calculations, and CSR access macros used by firmware loader HAL code.

## Important APIs, Types, And Functions
Important enums are `hal_global_csr`, generation-specific global CSR offsets, `hal_ae_csr`, `fcu_csr`, `fcu_csr_4xxx`, `fcu_cmd`, and `fcu_sts`. Macros define AE masks, context enable bits, local memory/global mode bits, wakeup events, FCU status positions, authentication retry timing, MMIO region offsets, and accessors such as `SET_CAP_CSR()`, `GET_CAP_CSR()`, `AE_CSR_ADDR()`, `SET_AE_CSR()`, `GET_AE_CSR()`, `AE_XFER_ADDR()`, `SET_AE_XFER()`, and `SRAM_WRITE()`.

## Control Flow
No functions are implemented here. Loader code uses these definitions to reset AEs, enable clocks, write ustore/local memory/registers, start or authenticate firmware through the FCU, poll status, and address per-AE local and transfer CSRs.

## State And Persistence Behavior
The header owns no software state. It defines how `icp_qat_fw_loader_handle` MMIO base pointers are interpreted and how writes affect persistent device state until reset or driver teardown.

## Dependencies And Integration Points
It includes `icp_qat_fw_loader_handle.h`, uses `ADF_CSR_RD/WR`, and is tightly coupled to firmware loader code, chip generation metadata, and PCI BAR mappings.

## Risks
These macros can write device control registers directly; wrong offsets or AE IDs can hang firmware loading or reset active engines. Generation-specific offsets must be selected correctly. Polling constants such as authentication retry periods affect boot latency and failure detection.

## Test Signals
Firmware load/auth/start on each supported generation, AE reset/restart, ustore programming validation, and FCU status transitions are the main signals. CSR trace logs can confirm expected offsets and commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw.h

## Purpose
`icp_qat_hw.h` defines common QAT hardware algorithm enums, capability masks, and descriptor setup structures for authentication, cipher, and compression services.

## Important APIs, Types, And Functions
Key enums include AE/QAT IDs, auth algorithms/modes, slice masks, capability masks, cipher algorithms/modes/direction/convert flags, and compression direction/delayed-match/algo/depth/file-type. Important structures include `icp_qat_hw_auth_config`, `icp_qat_hw_auth_setup`, `icp_qat_hw_auth_sha512`, `icp_qat_hw_auth_algo_blk`, `icp_qat_hw_cipher_config`, `icp_qat_hw_ucs_cipher_config`, `icp_qat_hw_cipher_algo_blk`, and `icp_qat_hw_compression_config`. Macros build auth, auth counter, cipher, and compression config words and define key/block/state sizes.

## Control Flow
The header is declarative. `qat_algs.c` fills auth and cipher blocks using `ICP_QAT_HW_AUTH_CONFIG_BUILD()` and `ICP_QAT_HW_CIPHER_CONFIG_BUILD()`. Compression context builders use the compression config builder. Hardware capability masks gate algorithm registration and feature paths such as AES v2.

## State And Persistence Behavior
No state is owned here. The structures are embedded in DMA content descriptors that persist for a crypto transform or compression context. Capability masks reflect hardware/firmware state discovered during device initialization.

## Dependencies And Integration Points
It includes `linux/bits.h` and is included by common firmware and algorithm files. It bridges Linux Crypto API algorithm choices to QAT hardware slice configuration words.

## Risks
Descriptor field constants must match hardware. Duplicate AES-XTS key size macros appear in the file, which is harmless if identical but a maintenance smell. SHA3 algorithm encoding splits across normal and high bits in the auth config builder, so adding auth algorithms requires care. Compression algo mask is only one bit while enum includes zstd value, so generation-specific headers may be needed for newer formats.

## Test Signals
Crypto and compression selftests validate config words indirectly. Capability-based registration tests should confirm algorithms are exposed only when hardware supports the required slices/features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_20_comp.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_20_comp.h

## Purpose
`icp_qat_hw_20_comp.h` provides typed builders for generation 2.0 QAT compression and decompression CSR configuration words. It converts enum-valued compression settings into firmware/hardware config dwords.

## Important APIs, Types, And Functions
The file defines `icp_qat_hw_comp_20_config_csr_lower`, `icp_qat_hw_comp_20_config_csr_upper`, `icp_qat_hw_decomp_20_config_csr_lower`, and `icp_qat_hw_decomp_20_config_csr_upper`. Builder functions are `ICP_QAT_FW_COMP_20_BUILD_CONFIG_LOWER()`, `ICP_QAT_FW_COMP_20_BUILD_CONFIG_UPPER()`, `ICP_QAT_FW_DECOMP_20_BUILD_CONFIG_LOWER()`, and `ICP_QAT_FW_DECOMP_20_BUILD_CONFIG_UPPER()`.

## Control Flow
Each builder starts with zero, writes each configured enum field with `QAT_FIELD_SET()`, and returns `swab32(val32)`. Compression lower fields include format, search depth, extended delay match, history buffer size, literal buffer controls, min-match, hash behavior, byte skip, and ABD. Compression upper fields include SCB/RMB/SOM controls, hash read, unload, token fusion, buffer memory size, reset mask, lazy, and nice parameters. Decompression builders set speculative decoder, mini-CAM, history/buffer size, format, min-match, and LZ4 checksum options.

## State And Persistence Behavior
The file owns no state. Returned dwords are embedded in compression content descriptors and persist while that descriptor/template is active.

## Dependencies And Integration Points
It includes Linux byte-swap support, generation 2.0 compression definitions, and common firmware bit helpers. Device-specific compression context code calls these builders when preparing QAT 2.0/2.3 compression templates.

## Risks
The return value is byte-swapped, unlike generation 5.1 builders. Mixing generation builders or omitting the swap will misprogram hardware. Defaults live in the defs header; callers must initialize every struct field explicitly or risk zero-valued settings that may not equal intended defaults.

## Test Signals
Compression context dumps should show expected lower/upper dwords for deflate, LZ4S, and zstd-capable 2.3 paths. Functional deflate/LZ4S/zstd tests on QAT 2.0/2.3 hardware validate builder settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_20_comp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_20_comp_defs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_20_comp_defs.h

## Purpose
`icp_qat_hw_20_comp_defs.h` lists generation 2.0 compression/decompression CSR bit positions, masks, enum values, and defaults used by the generation 2.0 builders.

## Important APIs, Types, And Functions
The file defines enums and defaults for compression SCB, RMB, SOM, skip-hash-read, SCB unload, token fusion, long buffer size, reset mask, lazy/nice parameters, history buffer size, ABD, LLLBD, search depth, compression format, min-match, hash collision/update, byte-skip, and extended delay match. Decompression definitions cover speculative decoder, mini-CAM, history buffer size, long buffer size, format, min-match, and LZ4 block checksum.

## Control Flow
There is no executable control flow. The defs are consumed by `icp_qat_hw_20_comp.h` builder functions and by callers selecting per-algorithm settings.

## State And Persistence Behavior
No state is owned here. The constants define firmware/hardware descriptor semantics and act as a stable hardware contract.

## Dependencies And Integration Points
This header is included by `icp_qat_hw_20_comp.h`. It integrates with device-specific compression context construction for deflate, LZ4, LZ4S, and QAT 2.3 zstd formats.

## Risks
Many enum values are not monotonic defaults from zero, so zero-initialized config structs may not be semantically correct for every field. Format definitions include 2.3 zstd values inside the 2.0 header family, so caller capability checks must select formats only on supporting hardware. Bit masks are raw numeric constants and must match hardware documentation.

## Test Signals
Static review can compare defaults against hardware spec. Runtime compression tests per format and search-depth level validate that selected enum combinations are accepted by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_20_comp_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_51_comp.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_51_comp.h

## Purpose
`icp_qat_hw_51_comp.h` provides typed builders for generation 5.1 QAT compression and decompression CSR configuration words.

## Important APIs, Types, And Functions
The config structs are `icp_qat_hw_comp_51_config_csr_lower`, `icp_qat_hw_comp_51_config_csr_upper`, `icp_qat_hw_decomp_51_config_csr_lower`, and `icp_qat_hw_decomp_51_config_csr_upper`. Builder functions are `ICP_QAT_FW_COMP_51_BUILD_CONFIG_LOWER()`, `ICP_QAT_FW_COMP_51_BUILD_CONFIG_UPPER()`, `ICP_QAT_FW_DECOMP_51_BUILD_CONFIG_LOWER()`, and `ICP_QAT_FW_DECOMP_51_BUILD_CONFIG_UPPER()`.

## Control Flow
The builders pack selected enum fields into a zeroed `u32` using `QAT_FIELD_SET()` and return the value without byte-swapping. Compression lower packs ABD, LLLBD, search depth, min-match, and LZ4 checksum. Compression upper packs DMM algorithm, buffer memory size, and SCB reset behavior. Decompression lower currently packs LZ4 checksum, and decompression upper packs buffer memory size.

## State And Persistence Behavior
No state is owned here. Built values become part of generation 5.1 compression descriptors/templates.

## Dependencies And Integration Points
It includes common firmware helpers and generation 5.1 defs. Device-specific 6xxx hardware data uses these builders when preparing compression context words.

## Risks
Generation 5.1 fields differ significantly from generation 2.0 and are not byte-swapped. Some defined fields in the defs header are not exposed in these compact config structs, so new features may require builder expansion. Callers must initialize all struct fields.

## Test Signals
QAT 6xxx compression/decompression context build tests, CSR/config dumps, and async compression selftests validate packing. Cross-generation tests should confirm 5.1 builders are not used on 2.0 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_51_comp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_51_comp_defs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_51_comp_defs.h

## Purpose
`icp_qat_hw_51_comp_defs.h` defines generation 5.1 compression/decompression CSR fields, masks, enum values, and defaults. It covers newer zstd, dictionary, DMM, CNV, ASB, buffer-memory, and internal control features.

## Important APIs, Types, And Functions
Compression definitions include SOM, skip-hash-read, bypass compression, DMM algorithm, token fusion, BMS, SCB reset, zstd frame generation, CNV disable, ASB disable, internal decoder/CAM controls, HBS, ABD, LLLBD, search depth, format, min-match, hash behavior, byte-skip, and LZ4 checksum. Decompression definitions include discard data, BMS, zstd frame generation, internal decoder/CAM controls, HBS, format, and LZ4 checksum.

## Control Flow
The file is constant-only. Its values are used by `icp_qat_hw_51_comp.h` builders and device-specific context construction.

## State And Persistence Behavior
No runtime state exists. The constants represent generation 5.1 hardware descriptor semantics.

## Dependencies And Integration Points
It includes `linux/bits.h` for `GENMASK()` and is included by the generation 5.1 builder header. It integrates with QAT 6xxx hardware-data code and compression algorithm registration gated by extended capabilities.

## Risks
Several fields are marked internal-only by name but are still exposed as definitions; callers must avoid enabling unsupported modes. `ICP_QAT_HW_COMP_51_SEARCH_DEPTH_LEVEL_9` and `LEVEL_10` share the same value, which may be intentional aliasing or a documentation hazard. Format defaults differ from classic deflate-oriented defaults.

## Test Signals
Hardware context dumps should match expected 5.1 default and zstd/LZ4 configurations. Functional tests should include zstd frame-generation behavior, CNV/ASB overflow paths, and decompression discard/format controls where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hw_51_comp_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_uclo.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_uclo.h

## Purpose
`icp_qat_uclo.h` defines constants and parsed object layouts for QAT microcode loader objects: UOF, SUOF, MOF, CSS headers, signed image metadata, AE modes, init tables, register tables, firmware authentication descriptors, and multi-object containers.

## Important APIs, Types, And Functions
Important constants define device type masks, maximum AE/context/uimage/ustore/register counts, object IDs and versions, chunk names, signature/key lengths for CSS/DSS, dual-sign metadata sizes, and AE mode extraction macros. Major structures include `icp_qat_uclo_objhandle`, `icp_qat_uof_filehdr`, `icp_qat_uof_objhdr`, `icp_qat_uof_image`, `icp_qat_uclo_encapme`, `icp_qat_uof_code_page`, `icp_qat_uof_batch_init`, `icp_qat_suof_handle`, `icp_qat_suof_img_hdr`, `icp_qat_fw_auth_desc`, `icp_qat_auth_chunk`, `icp_qat_css_hdr`, `icp_qat_simg_ae_mode`, and MOF table/header structures.

## Control Flow
The header has no executable control flow. Firmware loader code parses file headers and chunks, builds string/object tables, maps UOF code pages and init memory/register symbols, selects SUOF signed images for AE masks, creates authentication descriptors, and loads/authenticates firmware through HAL/FCU paths.

## State And Persistence Behavior
Parsed handles persist for the firmware loading/session lifetime. They reference buffers containing firmware objects, decoded strings, uwords, image tables, init-memory lists, and per-AE page/region state. CSS/auth structures represent staged firmware authentication metadata. No disk persistence is performed by this header.

## Dependencies And Integration Points
It is included by firmware loader handle and HAL headers. It integrates firmware file formats with accelerator-engine programming, CSS authentication, and generation-specific loader behavior.

## Risks
The structures mirror binary firmware formats, so padding, field widths, and endian assumptions are critical. Many fields are raw offsets into firmware buffers; parser bounds checks outside this header must be strict. Signature/key length macros vary by CSS 2K/3K and dual-sign support, so wrong chip flags can misplace image offsets.

## Test Signals
Firmware load tests across UOF/SUOF/MOF images, signed/dual-signed images, CSS 2K/3K variants, and multiple AE masks validate this ABI. Fuzzing or malformed firmware-object tests should check parser bounds and chunk validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_uclo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs.c

## Purpose
`qat_algs.c` implements QAT symmetric Crypto API algorithms: AES CBC, AES CTR, AES XTS, and authenc HMAC(SHA1/SHA256/SHA512)-CBC-AES AEAD. It builds QAT lookaside firmware requests, DMA content descriptors, maps scatterlists into QAT buffer lists, handles async completions, updates IVs, supports backlog submission, and registers algorithms once across active devices.

## Important APIs, Types, And Functions
Key context types are `qat_alg_cd`, `qat_alg_aead_ctx`, and `qat_alg_skcipher_ctx`. Important setup helpers include `qat_alg_do_precomputes()`, `qat_alg_init_common_hdr()`, `qat_alg_aead_init_enc_session()`, `qat_alg_aead_init_dec_session()`, `qat_alg_skcipher_init_com()`, `qat_alg_skcipher_init_enc()`, `qat_alg_skcipher_init_dec()`, `qat_alg_validate_key()`, and key-management functions for AEAD/skcipher/XTS. Runtime functions include `qat_alg_aead_enc()`, `qat_alg_aead_dec()`, `qat_alg_skcipher_encrypt()`, `qat_alg_skcipher_decrypt()`, XTS wrappers, `qat_alg_callback()`, and completion callbacks. Public registration functions are `qat_algs_register()` and `qat_algs_unregister()`.

## Control Flow
Transform init records hash settings or allocates XTS fallback/tweak ciphers. Setkey obtains a NUMA-local QAT crypto instance, allocates coherent content descriptors, validates AES key length, fills cipher/auth setup blocks, precomputes HMAC inner/outer states, builds firmware request templates, and sets slice chains. AEAD encrypt/decrypt validates block-aligned payloads, maps source/destination SGLs, copies the template, fills opaque pointer, buffer-list DMA addresses, IV, cipher offset/length, and auth params, then submits through the symmetric ring. Skcipher encrypt/decrypt follows the same pattern with cipher-only params and IV handling; CBC/CTR IVs are updated after completion or precomputed for decrypt, XTS may use hardware or fallback for AES-192-XTS.

## State And Persistence Behavior
Per-transform contexts persist content descriptors, physical addresses, firmware templates, selected instance, fallback objects, mode, and hash metadata. Per-request state lives in `struct qat_crypto_request` embedded in the Crypto API request context and contains the firmware request, mapped buffer list, callback, IV copy, and request pointers. Registration state uses a mutex and `active_devs` reference count.

## Dependencies And Integration Points
The file depends on Linux Crypto API internals, HMAC precompute helpers, AES/XTS helpers, QAT transport/backlog code, `qat_crypto` instance selection, firmware LA/hardware headers, DMA, and `qat_bl` SGL conversion. It integrates with QAT service callbacks through `qat_alg_callback()` registered on rings.

## Risks
DMA mapping/unmapping is complex and must match every error/completion path. AEAD only supports CBC payloads aligned to AES block size and authenc key parsing. XTS hardware/fallback split depends on AES-V2 capability and key size; tweak handling must match firmware expectations. IV updates are mode-specific and can corrupt caller state if completion order or error paths are wrong. Registration refcounting must match device bring-up/tear-down.

## Test Signals
Crypto selftests should cover all registered algorithms, all AES key sizes, AEAD encrypt/decrypt success and auth failure, fragmented and in-place/out-of-place SGLs, zero-length skcipher, CTR counter carry, CBC IV update, XTS fallback for 192-bit halves, AES-V2 XTS/CTR paths, backlog/ring-full behavior, and unregister after multiple devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs_send.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs_send.c

## Purpose
`qat_algs_send.c` provides common firmware-message submission and backlog handling for QAT crypto/compression algorithms. It wraps `adf_send_message()` with retry or Crypto API backlog behavior.

## Important APIs, Types, And Functions
Public functions are `qat_alg_send_message()` and `qat_alg_send_backlog()`. Internal helpers are `qat_alg_send_message_retry()`, `qat_alg_try_enqueue()`, and `qat_alg_send_message_maybacklog()`. It consumes `struct qat_alg_req` and `struct qat_instance_backlog` from `qat_algs_send.h`.

## Control Flow
For requests without `CRYPTO_TFM_REQ_MAY_BACKLOG`, `qat_alg_send_message_retry()` retries a full ring up to `ADF_MAX_RETRIES` and returns `-ENOSPC` on persistent `-EAGAIN`, otherwise `-EINPROGRESS`. With backlog allowed, `qat_alg_send_message_maybacklog()` first tries immediate enqueue if no backlog exists and the ring is not nearly full. If that fails, it locks the backlog, retries under the lock, and queues the request list node with `-EBUSY` if still unable. Completion callbacks call `qat_alg_send_backlog()`, which drains queued requests until the ring refuses one and completes each dequeued base request with `-EINPROGRESS`.

## State And Persistence Behavior
Backlog state is an in-memory list protected by a spinlock. Individual `qat_alg_req` nodes are embedded in per-request contexts and persist until sent or completed. No persistent storage exists.

## Dependencies And Integration Points
It depends on `adf_transport` ring APIs and the Crypto API async request completion mechanism. Symmetric, asymmetric, and compression code all embed `qat_alg_req` and share instance backlogs.

## Risks
Backlogged requests depend on request-context lifetime; callers must not free contexts after receiving `-EBUSY`. The immediate path returns `-EINPROGRESS` even if `adf_send_message()` succeeds after retries, matching Crypto API async semantics. A nearly-full threshold can send requests to backlog before hard full, trading latency for flow control. Completion-driven draining means a dead ring can leave backlog stalled.

## Test Signals
Ring-full tests should observe `-ENOSPC` without backlog and `-EBUSY` with backlog. Completion should later produce `-EINPROGRESS` for dequeued requests. Concurrency tests should cover multiple producers sharing one backlog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs_send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs_send.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs_send.h

## Purpose
`qat_algs_send.h` defines the shared request and backlog structures used by QAT algorithm implementations to submit firmware messages to ETR rings with Crypto API backlog support.

## Important APIs, Types, And Functions
`struct qat_instance_backlog` contains a list head and spinlock. `struct qat_alg_req` contains the firmware request pointer, TX ring pointer, base Crypto API async request, list node, and backlog pointer. It declares `qat_alg_send_message()` and `qat_alg_send_backlog()`.

## Control Flow
The header has no executable flow. Algorithm code fills `qat_alg_req` immediately before submission, then the implementation either sends directly or links it onto the instance backlog. Completion callbacks drain the same backlog.

## State And Persistence Behavior
The backlog persists per QAT crypto/compression instance. `qat_alg_req` persists inside a single in-flight or queued operation. The list node is valid only while the original Crypto API request remains alive.

## Dependencies And Integration Points
It includes list support and transport internals for `adf_etr_ring_data`. It integrates common submission behavior across symmetric LA, PKE, and data-compression rings.

## Risks
The header exposes raw `u32 *fw_req` and ring pointers; callers must ensure the request buffer matches the ring's message size and remains stable while queued. All users sharing one backlog can affect each other's latency.

## Test Signals
Compile coverage validates structure availability. Runtime backlog tests across symmetric, PKE, and compression services validate shared behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_algs_send.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_asym_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_asym_algs.c

## Purpose
`qat_asym_algs.c` implements QAT public-key Crypto API algorithms for RSA (`akcipher`) and Diffie-Hellman (`kpp`). It manages DMA key material, builds PKE firmware parameter tables, handles scatterlist alignment/padding, submits PKE requests, completes async operations, and registers algorithms once per active device set.

## Important APIs, Types, And Functions
Key types are `qat_rsa_ctx`, `qat_dh_ctx`, and `qat_asym_request`, with RSA/DH input/output parameter table structures. Important functions include `qat_alg_send_asym_message()`, `qat_alg_asym_callback()`, `qat_dh_compute_value()`, `qat_dh_set_secret()`, `qat_dh_cb()`, `qat_rsa_enc()`, `qat_rsa_dec()`, `qat_rsa_setkey()`, `qat_rsa_setkey_crt()`, `qat_rsa_cb()`, and function-ID selectors for RSA/DH key sizes. Public registration APIs are `qat_asym_algs_register()` and `qat_asym_algs_unregister()`.

## Control Flow
RSA transform init obtains a QAT instance and sets request size. Key setup parses public/private keys, strips leading zeros, allocates coherent buffers for `n`, `e`, `d`, and optional CRT fields, and selects CRT mode when all CRT components are present. RSA encrypt/decrypt validates key presence, destination length, source length, chooses a PKE function ID by modulus size and CRT/non-CRT mode, pads non-full-size scatterlist input into aligned temporary memory, maps source/output buffers and parameter tables, fills a PKE request, and submits on the PKE ring. Completion unmaps everything, copies aligned output back if needed, sets `dst_len`, and completes the request.

DH init obtains a QAT instance and allocates fallback KPP. `set_secret` decodes DH params; unsupported prime lengths fall back to software. Supported paths allocate coherent `p`, optional `g`, and private `xa`. Public/shared-secret operations build PKE tables for base `g` or peer public value, use optimized G=2 function IDs when possible, align input/output buffers, submit, and complete similarly to RSA.

## State And Persistence Behavior
RSA context persists DMA key components and CRT mode for the transform. DH context persists `p`, optional `g`, `xa`, G=2 flag, fallback transform, and instance. Per-request `qat_asym_request` persists aligned temporary buffers, DMA parameter tables, firmware request, callbacks, and request pointers until completion. Registration uses a mutex and active-device counter.

## Dependencies And Integration Points
The file depends on Crypto API RSA/KPP internals, DH/RSA parsers, FIPS flag header, QAT PKE firmware ABI, QAT transport/backlog, DMA mapping, scatterwalk helpers, and `qat_crypto` instance selection. It integrates with the PKE response callback registered on PKE rings.

## Risks
Key-size support is limited to specific RSA/DH bit lengths. DMA cleanup paths are dense and must avoid leaking sensitive buffers. RSA CRT setup silently falls back to non-CRT if any CRT component allocation/validation fails, while private exponent remains required. Request contexts are manually 64-byte aligned using extra request size. Fallback paths for DH must mirror request flags and output lengths.

## Test Signals
RSA encrypt/decrypt selftests across 512/1024/1536/2048/3072/4096-bit keys, private CRT and non-CRT keys, short inputs, too-small outputs, fragmented SGLs, and malformed keys are important. DH tests should cover supported and unsupported prime sizes, G=2 optimized public-key generation, peer shared secret, fallback, and PKE error status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_asym_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_bl.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_bl.c

## Purpose
`qat_bl.c` converts Linux scatterlists into QAT firmware buffer-list descriptors and frees their DMA mappings. It supports in-place and out-of-place operations, small inline descriptor storage, dynamic descriptor allocation, source/destination skip offsets, and optional extra destination overflow buffers.

## Important APIs, Types, And Functions
Public functions are `qat_bl_sgl_to_bufl()` and `qat_bl_free_bufl()`. The internal worker `__qat_bl_sgl_to_bufl()` performs the mapping and descriptor construction. The implementation fills `struct qat_request_buffs`, `qat_alg_buf_list`, and `qat_alg_buf` structures declared in `qat_bl.h`.

## Control Flow
`qat_bl_sgl_to_bufl()` extracts optional parameters and calls the internal converter. The converter counts source SG entries, chooses inline fixed storage for up to `QAT_MAX_BUFF_DESC` descriptors or allocates a larger list, maps each non-empty source segment after applying `sskip`, records DMA address/length, maps the source descriptor list itself, then either reuses the same list for in-place operations or builds/maps a destination list after `dskip` with an optional extra destination buffer. On failure it unwinds partially mapped destination and source buffers and descriptor-list mappings. `qat_bl_free_bufl()` reverses successful mappings and frees dynamic lists.

## State And Persistence Behavior
Buffer-list state persists only for one in-flight request. `sgl_src_valid` and `sgl_dst_valid` indicate whether inline storage inside `qat_request_buffs` is used or whether memory must be freed. DMA mappings remain valid until the service callback calls `qat_bl_free_bufl()`.

## Dependencies And Integration Points
It depends on Linux DMA mapping, scatterlist helpers, QAT accelerator device wrappers, and `qat_crypto.h`. It is used by symmetric and compression paths to convert Crypto API/acomp scatterlists into firmware SGL pointers.

## Risks
The code uses `dma_map_single()` on `sg_virt()` rather than `dma_map_sg()`, so it assumes CPU-addressable scatterlist entries. Skip handling must keep descriptor lengths consistent with mapped sizes. In out-of-place operations, extra destination buffers are not counted in `num_mapped_bufs` because they are already DMA-mapped elsewhere. Error unwinding loops over original SG counts while zero-length segments may have been skipped, so initialized `DMA_MAPPING_ERROR` sentinels are important.

## Test Signals
Tests should cover in-place and out-of-place SGLs, more than four descriptors, zero-length SG entries, source/destination skip offsets, compression overflow extra destination buffers, DMA mapping failures, and callback cleanup under success and firmware error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_bl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_bl.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_bl.h

## Purpose
`qat_bl.h` defines QAT buffer-list descriptor formats and the conversion/free API used to present Linux scatterlists to QAT firmware.

## Important APIs, Types, And Functions
Key definitions are `QAT_MAX_BUFF_DESC`, `struct qat_alg_buf`, `struct qat_alg_buf_list`, `struct qat_alg_fixed_buf_list`, `struct qat_request_buffs`, and `struct qat_sgl_to_bufl_params`. It declares `qat_bl_free_bufl()` and `qat_bl_sgl_to_bufl()`. The inline `qat_algs_alloc_flags()` maps Crypto API request flags to `GFP_KERNEL` or `GFP_ATOMIC`.

## Control Flow
No executable flow beyond `qat_algs_alloc_flags()` exists here. Callers allocate request context containing `qat_request_buffs`, call `qat_bl_sgl_to_bufl()` before firmware submission, pass `blp`/`bloutp` into firmware requests, and call `qat_bl_free_bufl()` on completion or immediate submission failure.

## State And Persistence Behavior
`qat_request_buffs` tracks per-request descriptor pointers, DMA addresses, sizes, inline fixed-list storage, and inline/dynamic ownership flags. Descriptor lists are packed and fixed descriptors are 64-byte aligned for hardware consumption.

## Dependencies And Integration Points
The header includes Crypto API request flags, scatterlists, and Linux types. It is shared by symmetric crypto and compression code.

## Risks
Structure packing and the `static_assert()` around the header group protect firmware ABI layout. Adding fields outside the grouped header would break `qat_alg_fixed_buf_list` assumptions. `QAT_MAX_BUFF_DESC` controls inline versus dynamic allocation and affects atomic allocation pressure.

## Test Signals
Compile-time static assert verifies layout. Runtime tests with small and large SGL counts validate inline/dynamic paths and allocation flags for sleepable and atomic requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_bl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_algs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_algs.c

## Purpose
`qat_comp_algs.c` implements QAT async compression algorithms for the Linux acomp API. It registers deflate, native zstd when supported, and a zstd facade backed by QAT LZ4S plus software zstd sequence emission on capable hardware. It maps SGLs, builds compression firmware requests, handles overflow/CNV status, performs fallback, and manages shared zstd scratch streams.

## Important APIs, Types, And Functions
Key types are `qat_zstd_scratch`, `qat_compression_ctx`, `qat_compression_req`, and `qat_callback_params`. Important functions include `qat_zstd_alloc_scratch()`, `qat_zstd_free_scratch()`, `qat_alg_send_dc_message()`, `qat_comp_generic_callback()`, `qat_comp_alg_callback()`, `qat_comp_alg_init_tfm()`, `qat_comp_alg_compress_decompress()`, `qat_comp_alg_zstd_decompress()`, `qat_comp_lz4s_zstd_callback()`, `qat_comp_alg_lz4s_zstd_compress()`, fallback helpers, and `qat_comp_algs_register()/unregister()`.

## Control Flow
Transform init gets a compression instance for the requested algorithm and builds firmware request context templates. Deflate requests call the common compress/decompress path directly. That path validates source/destination and adjusted lengths, adds a device overflow buffer for compression, converts SGLs to QAT buffer lists with skip parameters, copies the template, fills source/destination/length/opaque fields, and submits through the DC ring. Generic completion decodes status, errors, consumed/produced counters, maps overflow to `-E2BIG`, rejects unsupported verified compression, checks actual output length against caller buffer, sets `areq->dlen`, calls an optional algorithm-specific callback, frees buffer lists, completes the acomp request, and drains backlog.

For zstd native decompression, the input frame header is inspected; large windows or content sizes fall back to software zstd. For LZ4S-backed zstd compression, size limits choose hardware or software fallback. The callback reads LZ4S output, decodes it into zstd sequences/literals using `qat_alg_dec_lz4s()`, and calls `zstd_compress_sequences_and_literals()`.

## State And Persistence Behavior
Per-transform context persists the QAT compression template context, instance pointer, optional fallback acomp, and optional post-processing callback. Per-request state persists firmware request bytes, mapped buffer lists, direction, actual output length, and async request pointer. `qat_zstd_streams` owns a pool of scratch contexts with large buffers and zstd CCtx workspaces.

## Dependencies And Integration Points
The file depends on QAT compression instances/context builders, common firmware comp request helpers, transport/backlog, buffer-list conversion, Linux acomp API, scatterwalk copy helpers, kernel zstd APIs, and device capability bits for extended zstd/LZ4S support.

## Risks
The LZ4S-to-zstd bridge has large scratch buffers and sequence limits; overflow must be handled carefully. Native zstd decompression reads only the first source SG page for the frame header, so fragmented short headers are a risk. Compression uses an overflow buffer beyond caller output to detect actual overflow; failure to clear/check it can leak stale data or misreport. Registration has three separate active-device counters that must unwind according to capability bits.

## Test Signals
Acomp selftests should cover deflate compress/decompress, zstd native paths, LZ4S-backed zstd paths, software fallback thresholds, multi-SG input/output, output overflow, verified compression unsupported status, plain/uncompressed output flag, invalid zstd headers, and repeated register/unregister with capability combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_req.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_req.h

## Purpose
`qat_comp_req.h` provides inline helpers for creating QAT compression/decompression firmware requests from prebuilt templates and for decoding common compression response fields.

## Important APIs, Types, And Functions
It defines `QAT_COMP_REQ_SIZE` and `QAT_COMP_CTX_SIZE`. Request builders are `qat_comp_create_req()`, `qat_comp_create_compression_req()`, and `qat_comp_create_decompression_req()`. Response accessors include consumed/produced counters, produced Adler32, opaque pointer, compression and translator error codes, compression and translator status bits, CNV flag, and uncompressed-block flag.

## Control Flow
`qat_comp_create_req()` copies a template into the request buffer, fills source/destination addresses and lengths, stores opaque data, sets compression length and output buffer size, and scales the ASB threshold by `slen >> 4`. Compression uses the first template in the context, while decompression advances one request-sized template. Completion code calls the response accessors to update `acomp_req`.

## State And Persistence Behavior
No state is owned here. The caller-owned compression context stores two request templates. Per-request buffers receive a copied template and are valid until firmware completion.

## Dependencies And Integration Points
It includes `icp_qat_fw_comp.h` and is used by `qat_comp_algs.c`. It bridges device-specific context builders with generic acomp request submission.

## Risks
The context is assumed to contain exactly two `icp_qat_fw_comp_req` templates in compression/decompression order. ASB threshold scaling mutates the copied request and depends on input length. Accessors assume response pointer points to a valid `icp_qat_fw_comp_resp`.

## Test Signals
Compression/decompression requests should show correct template selection, opaque recovery, length fields, and response counter decoding. Unit-style tests can compare generated request fields for representative source/destination sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_req.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_zstd_utils.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_zstd_utils.c

## Purpose
`qat_comp_zstd_utils.c` translates QAT-produced LZ4S token streams into zstd sequence/literal arrays that can be passed to kernel zstd sequence compression. It is support code for the QAT LZ4S-backed zstd compression path.

## Important APIs, Types, And Functions
The public function is `qat_alg_dec_lz4s()`. Internal helper `emit_delimiter()` inserts explicit zstd block delimiters. Important constants define LZ4S token split (`ML_BITS`, `RUN_BITS`), masks, `LZ4S_MINMATCH`, and `QAT_ZSTD_BLOCK_MAX`.

## Control Flow
`qat_alg_dec_lz4s()` walks the LZ4S buffer byte by byte. For each token, it decodes literal length with extension bytes, copies literal bytes into the literal output buffer in fixed 8-byte chunks, then either emits a trailing literal-only sequence at end of input or reads a 16-bit offset and match length with extension bytes. Nonzero matches are converted into `ZSTD_Sequence` entries, with any accumulated historical literal length folded in. If the next sequence would exceed the zstd block maximum, it emits a delimiter first and resets block size. Zero-length matches defer literal length to the next sequence. Capacity checks return `-EOVERFLOW`.

## State And Persistence Behavior
The function owns no persistent state. It writes caller-provided sequence and literal buffers and updates `lit_len`. Local `hist_literal_len`, `block_decomp_size`, and sequence index track translation state for one stream.

## Dependencies And Integration Points
It depends on kernel zstd sequence types, unaligned little-endian reads, string copying, and debug logging. `qat_comp_algs.c` calls it from the LZ4S-zstd post-processing callback.

## Risks
The literal copy loop copies `QAT_ZSTD_LIT_COPY_LEN` bytes at a time and relies on caller scratch capacity including extra copy slack. The parser assumes valid LZ4S input from firmware; malformed input could overrun `ip` because extension-byte loops do not explicitly check `end_ip` before each read. Sequence delimiter capacity reserves one slot, so max sequence tests are important.

## Test Signals
Tests should cover empty input, literal-only streams, sequences with extended literal/match lengths, zero-length-match literal accumulation, block delimiter insertion at 128KB, capacity overflow, and round-trip zstd output compared with software zstd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_zstd_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_zstd_utils.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_zstd_utils.h

## Purpose
`qat_comp_zstd_utils.h` declares the LZ4S-to-zstd sequence conversion helper used by QAT zstd compression support.

## Important APIs, Types, And Functions
It defines `QAT_ZSTD_LIT_COPY_LEN` as 8 and declares `qat_alg_dec_lz4s(ZSTD_Sequence *out_seqs, size_t out_seqs_capacity, unsigned char *lz4s_buff, unsigned int lz4s_buff_size, unsigned char *literals, unsigned int *lit_len)`.

## Control Flow
The header has no executable flow. Callers allocate sequence and literal buffers, pass a firmware LZ4S output buffer and capacity, then use the returned sequence count and literal length with kernel zstd APIs.

## State And Persistence Behavior
No state is owned here. All output is caller-owned scratch memory for a single compression request or stream operation.

## Dependencies And Integration Points
It includes `linux/zstd_lib.h` for `ZSTD_Sequence` and is included by `qat_comp_algs.c`. It is specific to the zstd facade backed by QAT LZ4S.

## Risks
The API assumes buffers are large enough for fixed-width literal copying and the advertised sequence capacity. Callers must treat negative returns as errors and avoid using partially written sequence data.

## Test Signals
Compile coverage validates zstd type availability. Runtime zstd compression tests through QAT LZ4S validate the declared helper contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_zstd_utils.h -->
