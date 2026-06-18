# Research: subset-b-003542 AMD RAS rascore

Grouped worker report for `subset-b-003542`. Each section preserves the source path in its title and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_core.c

Purpose: this is the central lifecycle and integration layer for the AMD GPU RAS core. It creates/destroys `struct ras_core_context`, initializes software and hardware submodules, exposes common helpers for timestamps, GPU status, reset locking, notifier dispatch, address translation, ECC queries, and sequence-number handling.

Important APIs and control flow: `ras_core_sw_init()` installs `sys_fn`, allocates poison-creation and poison-consumption `kfifo`s, initializes ACA, UMC, command handling, log ring, and PSP. `ras_core_hw_init()` records EEPROM/poison capabilities, initializes PSP, ACA, MP1, NBIO, UMC, GFX, discovers firmware RAS features, chooses firmware EEPROM or physical EEPROM, loads saved bad pages, validates storage state, then starts the event-processing thread. Error labels unwind hardware initialization in reverse order. `ras_core_hw_fini()` stops processing and tears down hardware state. Runtime entry points include `ras_core_handle_nbio_irq()`, `ras_core_handle_fatal_error()`, `ras_core_update_ecc_info()`, `ras_core_query_block_ecc_data()`, `ras_core_check_safety_watermark()`, `ras_core_event_notify()`, and UMC address translation wrappers.

State and persistence: the file owns core boolean state such as `is_initialized`, `ras_core_enabled`, `is_rma`, `ras_fw_features`, poison FIFOs, and spinlock. Persistence is delegated to EEPROM or firmware EEPROM, but `ras_core_eeprom_recovery()` coordinates reloading saved bad pages after reset and synchronizing bad-page/channel notifications.

Dependencies and integration: it depends on `ras.h`, `ras_core_status.h`, ACA, UMC, PSP, MP1, NBIO, GFX, EEPROM, log ring, process, and system callbacks in `ras_core_config`. Risks center on partial init cleanup, unchecked optional callback behavior, FIFO allocation leaks on later `sw_init` failures, and the correctness of the firmware-vs-I2C EEPROM selection. Test signals should exercise unsupported IP versions, missing callbacks, reset recovery with saved EEPROM records, threshold/RMA transitions, FIFO fallback sequence generation, and init failure unwinding at every label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_core_status.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_core_status.h

Purpose: this header defines numeric RAS core status codes shared by the RAS core modules. `RAS_CORE_OK` is zero and the remaining values encode not-supported and failure categories near 248-255.

Important definitions: `RAS_CORE_NOT_SUPPORTED`, `RAS_CORE_FAIL_ERROR_QUERY`, `RAS_CORE_FAIL_ERROR_INJECTION`, `RAS_CORE_FAIL_FATAL_RECOVERY`, `RAS_CORE_FAIL_POISON_CONSUMPTION`, `RAS_CORE_FAIL_POISON_CREATION`, `RAS_CORE_FAIL_NO_VALID_BANKS`, and `RAS_CORE_GPU_IN_MODE1_RESET`. Several call sites return the negative form of these constants, for example `-RAS_CORE_NOT_SUPPORTED` from notifier wrappers or `-RAS_CORE_GPU_IN_MODE1_RESET` from event handling.

Control flow and state: there is no runtime state. The constants influence error propagation through core, MP1, PSP, process, and RAS command paths, so consumers must know whether a function returns Linux `-errno`, a negative RAS status value, or zero.

Dependencies and integration: only include guards are present. It is pulled into core, CPER, GFX, MP1, and log-ring sources. Risks are semantic rather than structural: these values overlap neither conventional Linux errno values nor positive TA statuses, but they are not self-describing once negated. Test signals should verify callers do not compare these codes to raw positive constants and that reset handling treats `-RAS_CORE_GPU_IN_MODE1_RESET` as a special control signal rather than a generic failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_core_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cper.c

Purpose: this file serializes RAS log-ring entries into CPER-like binary records for runtime, fatal, boot/RMA-style reporting. It converts `struct ras_log_info` batches into packed headers, descriptors, and payload sections suitable for host consumption.

Important functions: `cper_get_timestamp()` converts Unix seconds via `ras_core_convert_timestamp_to_time()`. `fill_section_hdr()` writes CPER signature, revision, severity, platform/device IDs, creator ID, record ID, timestamp, and notify GUID. `fill_section_descriptor()` fills section offsets, severity, FRU text, and flags such as RMA threshold or latent error. `fill_section_runtime()` copies ACA register dumps into the nonstandard/runtime section. `fill_section_fatal()` stores the fatal status/address/IPID/syndrome subset. `ras_cper_generate_cper()` is the exported API, mapping log events to CPER type and severity before writing the caller-provided buffer.

Control flow and state: the implementation is stateless apart from reading system info and trace contents. Runtime and RMA events produce one record with `count` descriptors/sections; UE fatal events produce repeated single-section fatal records. Size is calculated up front by `cper_get_record_size()` and compared with `buf_len`.

Dependencies and integration: this sits behind log-ring retrieval and consumes ACA register index conventions. It calls core timestamp and device-info callbacks. Risks include trusting `trace_list[0]` without null/count validation, relying on packed layout macros from the header, truncating `record_id` and strings into fixed fields, and inconsistent fatal sizing when multiple records are emitted. Test signals should include CE, DE, UE, poison, and RMA event batches, undersized buffers, multi-record fatal output length, and validation of generated offsets against packed struct sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cper.h

Purpose: this header defines the CPER wire-format structures, GUID helpers, severity/type enums, ACA register slots, and the `ras_cper_generate_cper()` API. The structures are packed because callers write them directly into binary CPER buffers.

Important types and constants: `struct ras_cper_guid` and `CPER_GUID__INIT()` define GUID literals. `enum ras_cper_type` separates runtime, fatal, boot, and RMA records. `enum ras_cper_severity` maps CE/UE/RMA severities. Packed structs include `cper_section_hdr`, `cper_section_descriptor`, runtime headers/descriptors/register dumps, crashdump/fatal/boot sections, and `ras_cper_fatal_record`.

Control flow and persistence: no active behavior or persistence exists in the header; it defines the layout contract used by `ras_cper.c`. The section offset macros determine how binary sections are placed in the generated buffer.

Dependencies and integration: consumers must also understand ACA register ordering and log-ring events. A notable risk is that several length macros reference names such as `cper_sec_desc`, `cper_sec_crashdump_boot`, `cper_sec_crashdump_fatal`, and `cper_sec_nonstd_err`, while this header defines `cper_section_descriptor`, `cper_section_boot`, `cper_section_fatal`, and `cper_section_runtime`. If no aliases exist through other included headers, this is a compile-time break. Even with aliases, binary ABI tests are important because packed bitfields and enum widths can be compiler-sensitive. Test signals should include static size assertions, offset assertions, and compile coverage for all macros used by `ras_cper.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom.c

Purpose: this is the physical I2C EEPROM backend for persistent RAS bad-page records and GPU health metadata. It owns table layout, endian encoding, checksum generation, circular append/read behavior, threshold/RMA decisions, and synchronization notifications.

Important APIs and functions: `ras_eeprom_hw_init()` configures thresholds, I2C limits, adapter/port/address, initializes the mutex, and checks or creates the table. `ras_eeprom_reset_table()` writes a clean header and v2.1/v3 RAS info area. `ras_eeprom_append()` appends serialized `eeprom_umc_record` entries and updates checksum/header metadata. `ras_eeprom_read()` reads records from `ras_fri`, handling wraparound. `ras_eeprom_check_storage_status()` verifies checksum, reads RAS info, handles `AMDR` versus `BADG` header status, warns near threshold, and may restore a good tag if the configured threshold increased. `ras_eeprom_check_safety_watermark()` and `ras_eeprom_check_gpu_status()` expose RMA/health state.

Control flow and state: transfer helpers split reads/writes according to `max_read_len`/`max_write_len`, hold the GPU reset lock around I2C, and sleep after writes. The table is a circular record region with `ras_fri`, `ras_num_recs`, `ras_max_record_count`, `tbl_hdr.tbl_size`, checksum, `bad_channel_bitmap`, and update flags protected by `ras_tbl_mutex`. Persistence is in EEPROM at either a configured base address with header, optional RAS info, and 24-byte records.

Dependencies and risks: this depends on system I2C callbacks, reset locking, UMC bad-page counts, and event notifications. Risks include short-transfer handling, checksum coverage after wraparound, threshold behavior when `record_threshold_count` is zero, table-version migration, write latency during reset-sensitive paths, and that `ras_eeprom_append()` rejects appends where existing plus new exceeds capacity despite lower-level wrap logic. Test signals should cover fresh EEPROM creation, v1/v2.1/v3 table reads, corrupted checksum/header, wraparound read/write, threshold transitions to `BADG`, disabled retirement, I2C limit splitting, and bad-channel notification updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom.h

Purpose: this header defines the physical EEPROM table contract and the public API used by core and UMC for persistent bad-page storage.

Important types and macros: table versions are `RAS_TABLE_VER_V1`, `RAS_TABLE_VER_V2_1`, and `RAS_TABLE_VER_V3`. Threshold modes include `NONSTOP_OVER_THRESHOLD`, `WARN_NONSTOP_OVER_THRESHOLD`, and `DISABLE_RETIRE_PAGE`. NPS/address packing helpers store bad-page PFN bits and NPS mode inside `eeprom_umc_record.retired_row_pfn`. `struct ras_eeprom_table_header` is the serialized table header. `struct ras_eeprom_table_ras_info` stores RMA status, health percent, and threshold. `struct ras_eeprom_control` tracks table geometry, I2C callbacks, limits, counters, mutex, and bad-channel bitmap. `struct eeprom_umc_record` is the in-memory bad-page record with serialized fields plus runtime-only current-NPS fields.

Control flow and state: the header has no active behavior, but it defines the persistent schema that `ras_eeprom.c`, `ras_umc.c`, and firmware EEPROM compatibility paths rely on. `ras_eeprom_append()`, `ras_eeprom_read()`, reset, count, sync, storage status, and health functions form the exported backend.

Dependencies and integration: it includes `ras_sys.h` for system callback types and forward-declares `ras_core_context`. Risks are ABI/layout related: the comment notes serialized record size differs from `sizeof(struct eeprom_umc_record)`, so callers must not write the struct directly. Test signals should verify packing macros, threshold mode behavior, and that runtime-only fields are reconstructed before callers use RAM bad-page records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom_fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom_fw.c

Purpose: this is the firmware-backed EEPROM facade. It exposes the same broad bad-page persistence behavior as the physical EEPROM backend, but record storage and lookup are performed by MP1/SMU firmware messages rather than direct I2C table serialization.

Important APIs: `ras_fw_init_feature_flags()` reads MP1 RAS feature bits and enables the backend when `RAS_CORE_FW_FEATURE_BIT__RAS_EEPROM` is present. `ras_fw_get_table_version()`, `ras_fw_get_badpage_count()`, `ras_fw_get_badpage_mca_addr()`, `ras_fw_get_badpage_ipid()`, `ras_fw_get_timestamp()`, `ras_fw_set_timestamp()`, and `ras_fw_erase_ras_table()` wrap firmware messages. `ras_fw_eeprom_hw_init()` configures thresholds and reads firmware table state. `ras_fw_eeprom_read_idx()` reconstructs `eeprom_umc_record` and/or `ras_bank_ecc` arrays from firmware MCA/IPID/timestamp records. `ras_fw_eeprom_update_record()` polls for a new firmware record after an error. Append/reset/sync/status/health functions mirror the physical backend API.

Control flow and state: local state is limited to version, counters, threshold configuration, mutex, bad-channel bitmap, and RMA flag updates. Firmware owns durable records. `ras_fw_get_badpage_count()` polls `-EBUSY` until timeout. Init sets firmware timestamp from `ktime_get_real_seconds()` and caps max records at 4000.

Dependencies and risks: this depends on `ras_mp1.sys_func->mp1_send_eeprom_msg`, UMC `mca_ipid_parse`, UMC bad-page counts, and core event notifications. Risks include assuming firmware count changes after append, hard-coded 4000 capacity, only reading one new record in `ras_fw_eeprom_update_record()`, weak null checks for MP1 callbacks in helper wrappers, and threshold behavior that marks `is_rma` without the physical header/health-percent detail. Test signals should mock MP1 responses for busy/timeout, split high/low 64-bit reads, threshold/RMA transitions, firmware feature absence, and reconstruction of channel/mcumc IDs from IPID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom_fw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom_fw.h

Purpose: this header declares the firmware EEPROM control structure and public operations that let core and UMC use MP1/SMU-managed persistent bad-page storage through an EEPROM-like interface.

Important types and APIs: `struct ras_fw_eeprom_control` tracks firmware table version, threshold mode/count, record count, max capacity, mutex, bad-channel bitmap, and update flag. Exported functions cover feature discovery, table version/count, MCA address/IPID/timestamp retrieval, timestamp setting, table erase/reset, safety-watermark checking, append/read/update operations, init/fini, storage status, GPU health, and notification sync.

Control flow and state: no active code lives here. The declarations define the integration seam used by `ras_core.c` to choose firmware storage and by `ras_umc.c` to load/save bad pages without knowing whether persistence is firmware-backed or I2C-backed.

Dependencies and integration: the header assumes `struct ras_core_context`, `struct eeprom_umc_record`, `struct ras_bank_ecc`, and `enum ras_gpu_health_status` are visible through broader `ras.h` include context. Risks are mainly API contract drift with `ras_eeprom.h`: callers expect matching semantics for count, append, read, health, and threshold operations even though firmware has different durability and indexing behavior. Test signals should compile both backends under the same caller paths and validate identical behavior for disabled retirement, record counting, channel bitmap notifications, and RMA state reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_eeprom_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx.c

Purpose: this is the generic GFX RAS IP dispatch layer. It chooses an IP-version-specific GFX RAS function table and exposes a wrapper for mapping driver GFX subblocks to RAS TA subblocks.

Important APIs: `ras_gfx_hw_init()` copies `gfx_ip_version` from config and selects `gfx_ras_func_v9_0` for IP versions 9.4.3, 9.4.4, and 9.5.0. `ras_gfx_get_ta_subblock()` calls the selected `get_ta_subblock` operation. `ras_gfx_hw_fini()` is currently a no-op.

Control flow and state: the file stores only `ras_core->ras_gfx.gfx_ip_version` and `ip_func`. Initialization fails with `-EINVAL` when the GFX IP is unsupported. There is no persistence.

Dependencies and integration: PSP error injection calls `ras_gfx_get_ta_subblock()` before sending a TA trigger-error command for GFX blocks. The selected implementation comes from `ras_gfx_v9_0.c`. Risks include no null guard in `ras_gfx_get_ta_subblock()` if called before successful hardware init and no fallback for unknown IPs. Test signals should include supported/unsupported IP initialization, calling GFX error injection with valid and invalid subblocks, and verifying 9.5.0 behavior where UMC code also branches on GFX version for row handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx.h

Purpose: this header defines the generic GFX RAS dispatch interface used by the core and PSP layers.

Important types and APIs: `struct ras_gfx_ip_func` currently contains one operation, `get_ta_subblock()`, which translates a driver-visible GFX subblock and error type to a TA-compatible subblock. `struct ras_gfx` stores the configured GFX IP version and selected function table. Public functions are `ras_gfx_hw_init()`, `ras_gfx_hw_fini()`, and `ras_gfx_get_ta_subblock()`.

Control flow and state: no behavior is implemented here. State is the selected version/function pointer stored in the core context. There is no persistence.

Dependencies and integration: this header is consumed by core initialization and PSP TA error injection. It intentionally hides the large v9 subblock table behind the generic function table. Risks are null function-table use if callers skip or ignore `ras_gfx_hw_init()` failure, and API narrowness if future IP versions need more GFX RAS hooks. Test signals should compile both generic and v9-specific users and exercise error-type validation across the public `ras_gfx_get_ta_subblock()` wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx_v9_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx_v9_0.c

Purpose: this file implements the GFX v9 subblock mapping and support validation used by RAS TA error injection.

Important data/functions: `enum ta_gfx_v9_subblock` mirrors the TA-facing subblock numbering. `struct ras_gfx_subblock_t` stores name, TA subblock ID, hardware-supported error-type bitmask, and software-supported error-type bitmask. `RAS_GFX_SUB_BLOCK()` builds the large `ras_gfx_v9_0_subblocks[]` table. `gfx_v9_0_get_ta_subblock()` validates that the requested subblock index exists, has a populated table entry, is supported by hardware for the requested error type, and is supported by the driver before returning the TA subblock ID. `gfx_ras_func_v9_0` exports this operation.

Control flow and state: the file is stateless and table-driven. Unsupported entries return `-EINVAL` or `-EPERM`, with diagnostic logs for unsupported error types. There is no persistence.

Dependencies and integration: PSP trigger-error flow calls this through `ras_gfx_get_ta_subblock()` for `RAS_TA_BLOCK__GFX`, then packs the resulting subblock plus instance mask into the TA command. Risks include the driver and TA enums drifting out of sync, sparse table entries with null names, and bitmask interpretation mismatch between `enum ras_ta_error_type` values and the table's packed support flags. Test signals should enumerate every `RAS_GFX_V9__GFX_MAX` index, verify expected TA IDs, verify parity/CE/UE/poison support masks, and include invalid subblock/error-type combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx_v9_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx_v9_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx_v9_0.h

Purpose: this header defines the driver-visible GFX v9 RAS subblock enumeration and exposes the v9 function table.

Important definitions: `enum ras_gfx_v9_subblock` enumerates CPC, CPF, CPG, GDS, SPI, SQ, SQC ranges, TA, TCA, TCC ranges, TCI, TCP, TD, EA ranges, and UTC/ATC units. Range start/end constants are embedded in the enum to support validation and grouping. `extern const struct ras_gfx_ip_func gfx_ras_func_v9_0` is implemented by `ras_gfx_v9_0.c`.

Control flow and state: no code or persistence exists here. The enum values are an ABI-like contract with the v9 mapping table and callers that request injection subblocks.

Dependencies and integration: included by generic GFX dispatch and the v9 implementation. PSP error injection ultimately depends on these values being stable and aligned with the TA enum table. Risks include accidental renumbering, missing table entries for enum values, and confusing similarly named driver and TA enums. Test signals should include compile-time or unit checks that the table length covers `RAS_GFX_V9__GFX_MAX`, that expected range endpoints match table groups, and that user-facing injection requests map to supported TA subblocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx_v9_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_log_ring.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_log_ring.c

Purpose: this file implements an in-memory RAS event log ring using a mempool and radix tree keyed by batch/subsequence numbers. It stores ACA register snapshots for later CPER generation or inspection.

Important functions: `ras_log_ring_sw_init()` creates a preallocated mempool, initializes the radix tree and spinlock. `ras_log_ring_create_batch_tag()` reserves a batch ID and timestamp; `ras_log_ring_add_log_event()` allocates a log record, fills timestamp/event/register data, synthesizes RMA register data when needed, and inserts it. `ras_log_ring_get_batch_records()` returns records in a batch. `ras_log_ring_get_batch_overview()` reports first/last batch indexes and count. Cleanup paths delete tree entries and destroy the mempool.

Control flow and state: `mono_upward_batch_id` grows as batches or unbatched entries are created. `last_del_batch_id` advances when old data is removed. `logged_ecc_count` tracks live records. Batch sequence numbers use the high bits for batch ID and low 8 bits for sub-sequence; `MAX_RECORD_PER_BATCH` is 32. If allocation fails or the pool is too full, the code deletes a temporary number of old records before retrying.

Dependencies and integration: CPER code consumes `struct ras_log_info` records; ACA producers provide register arrays; core supplies timestamps and device info. Risks include radix-tree insertion collisions, `logged_batch_count` including empty/deleted batches, count comparison against byte-sized mempool constants, and no deep copy on `get_batch_records()`. Test signals should cover batched/unbatched insertion, batch overflow, deletion under memory pressure, RMA synthetic register content, concurrent add/query paths, and CPER generation from returned records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_log_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_log_ring.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_log_ring.h

Purpose: this header defines the in-memory RAS log-ring data model and public operations.

Important types and macros: `MAX_RECORD_PER_BATCH` caps per-batch entries at 32. `RAS_LOG_SEQNO_TO_BATCH_IDX()` extracts the batch from a sequence number. `enum ras_log_event` distinguishes UE, DE, CE, poison creation/consumption, RMA, and sentinel values. `struct ras_aca_reg` wraps ACA register dumps. `struct ras_log_info` records sequence, timestamp, event, and register payload. `struct ras_log_batch_tag` carries batch ID, timestamp, and sub-sequence while producers add related events. `struct ras_log_ring` stores mempool, radix root, spinlock, counters, and deletion cursor.

Control flow and state: the header declares init/fini, batch-tag create/destroy, log append, batch record retrieval, and overview APIs. No persistent storage is involved; the ring is volatile kernel memory.

Dependencies and integration: it includes `ras_aca.h` for register counts and indices. CPER serialization depends on this header's event and register layout. Risks include callers retaining pointers after ring cleanup/deletion, event enum drift against CPER mapping, and unclear ownership of batch tags. Test signals should verify all events map to expected CPER behavior, batch tag lifetime is respected, and overview counts remain sensible after cleanup and wrap-like deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_log_ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1.c

Purpose: this is the generic MP1 RAS dispatch layer. It selects an IP-specific MP1 function table and forwards valid-bank count and bank-dump requests used by ACA/ECC collection and firmware EEPROM feature discovery.

Important APIs: `ras_mp1_hw_init()` records `mp1_ip_version`, installs `mp1_sys_fn` from config, selects `mp1_ras_func_v13_0` for supported MP1 v13 variants, and fails if callbacks or IP support are absent. `ras_mp1_get_bank_count()` and `ras_mp1_dump_bank()` forward to the selected IP functions. `ras_mp1_hw_fini()` is a no-op.

Control flow and state: state is limited to configured IP version, system callbacks, and selected function table in `ras_core->ras_mp1`. No persistence is owned here.

Dependencies and integration: `ras_eeprom_fw.c` also uses `ras_mp1.sys_func` for EEPROM firmware messages, while ACA paths use bank count/dump operations. Risks include wrapper calls with null `ip_func` if initialization failed, unsupported MP1 IP versions halting `ras_core_hw_init()`, and system callback implementations having firmware-specific side effects. Test signals should initialize supported and unsupported IP versions, missing `mp1_sys_fn`, missing specific MP1 callbacks, CE/DE/UE bank queries, and firmware feature discovery using the same MP1 system function block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1.h

Purpose: this header defines the MP1 RAS dispatch interface for querying and dumping valid MCA banks.

Important types and APIs: `struct ras_mp1_ip_func` contains `get_valid_bank_count()` and `dump_valid_bank()` operations. `struct ras_mp1` stores the MP1 IP version plus selected IP and system callback tables. Public APIs are `ras_mp1_hw_init()`, `ras_mp1_hw_fini()`, `ras_mp1_get_bank_count()`, and `ras_mp1_dump_bank()`.

Control flow and state: no behavior is implemented here. The state is embedded in `struct ras_core_context` and initialized by `ras_mp1.c`.

Dependencies and integration: it includes `ras.h` for core and error type definitions. ACA and firmware EEPROM paths depend on a valid MP1 system callback configuration. Risks are API contract ambiguity around `ecc_type`/`enum ras_err_type` values and unchecked null function pointers in generic wrappers. Test signals should compile all MP1 users, verify CE/DE share the CE message path in v13, and assert unsupported error types return `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1_v13_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1_v13_0.c

Purpose: this file implements MP1 v13 RAS bank-query commands by mapping generic RAS error types to firmware message IDs.

Important functions: `mp1_v13_0_get_bank_count()` maps UE to `RAS_MP1_MSG_QueryValidMcaCount` and CE/DE to `RAS_MP1_MSG_QueryValidMcaCeCount`, then calls `mp1_get_valid_bank_count`. It validates the output pointer and rejects counts at or above the per-query maximum. `mp1_v13_0_dump_bank()` maps UE to `RAS_MP1_MSG_McaBankDumpDW` and CE/DE to `RAS_MP1_MSG_McaBankCeDumpDW`, then calls `mp1_dump_valid_bank`. `mp1_ras_func_v13_0` exports these operations.

Control flow and state: this file is stateless. It relies entirely on `ras_core->ras_mp1.sys_func` and returns `-RAS_CORE_NOT_SUPPORTED` when required callbacks are missing.

Dependencies and integration: ACA/ECC collection uses these operations to retrieve valid MCA bank data. Firmware message constants are hard-coded for MP1 v13. Risks include off-by-one treatment of `MAX_UE_BANKS_PER_QUERY`/`MAX_CE_BANKS_PER_QUERY`, DE count validation using the CE limit only through the CE/DE branch, and error propagation mixing RAS status with Linux errno. Test signals should mock MP1 callbacks for UE, CE, DE, unsupported types, null output pointers, missing callbacks, maximum count boundary, and register dump indexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1_v13_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1_v13_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1_v13_0.h

Purpose: this header exposes the MP1 v13 RAS function table.

Important definition: `extern const struct ras_mp1_ip_func mp1_ras_func_v13_0` is the table selected by `ras_mp1.c` for supported MP1 v13 IP versions.

Control flow and state: no code or persistent state exists. It is a narrow declaration header.

Dependencies and integration: includes `ras_mp1.h`, so users receive the generic MP1 function-table type. Risks are minimal but include stale declaration if the implementation table changes shape. Test signals are compile coverage of generic MP1 init selecting this symbol and linker coverage for all supported v13 IP version cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1_v13_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio.c

Purpose: this is the generic NBIO RAS dispatch layer. It selects the NBIO IP function table, enables/disables NBIO RAS interrupt sources through system callbacks, and forwards IRQ handling.

Important APIs: `ras_nbio_hw_init()` installs `nbio_sys_fn`, selects `ras_nbio_v7_9` for IP versions 7.9.0 and 7.9.1, and enables RAS controller and ATHUB error-event IRQs if callbacks are present. `ras_nbio_hw_fini()` disables those IRQs. `ras_nbio_handle_irq_error()` calls IP-specific handlers for controller and ATHUB interrupts and returns true.

Control flow and state: state is the configured NBIO IP version, system callback table, and selected IP function table. No persistence is owned here. IRQ enablement is a hardware side effect during core hardware init/fini.

Dependencies and integration: core delegates NBIO interrupts to this layer. UMC asks core for current NPS mode, which forwards to `nbio->ip_func->get_memory_partition_mode`. Risks include unconditional true return even if handlers fail, optional callback omissions silently leaving interrupts disabled, and no null checks in current NPS mode beyond the core wrapper. Test signals should cover supported/unsupported IP init, missing sys callbacks, IRQ enable/disable calls, handler error propagation expectations, and NPS mode reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio.h

Purpose: this header defines the NBIO RAS dispatch interface.

Important types and APIs: `struct ras_nbio_ip_func` contains operations to handle RAS controller interrupts without BIF ring, handle ATHUB error-event interrupts without BIF ring, and read the current memory partition/NPS mode. `struct ras_nbio` stores the NBIO IP version, selected IP function table, and system callback table. Public functions are `ras_nbio_hw_init()`, `ras_nbio_hw_fini()`, and `ras_nbio_handle_irq_error()`.

Control flow and state: no active behavior exists here. NBIO state is held inside the core context.

Dependencies and integration: it includes `ras.h` and is used by core initialization, IRQ handling, and UMC NPS discovery. Risks are callback-contract issues: interrupt handlers are optional in the function table but memory partition mode is assumed by UMC initialization. Test signals should verify `get_memory_partition_mode` is available for every supported IP and that IRQ paths tolerate missing individual handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio_v7_9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio_v7_9.c

Purpose: this file implements NBIO v7.9 register-level RAS interrupt clearing and memory partition mode discovery.

Important functions: `nbio_v7_9_handle_ras_controller_intr_no_bifring()` reads `regBIF_BX0_BIF_DOORBELL_INT_CNTL`, checks the RAS controller interrupt status bit, sets the clear bit, and writes it back. A TODO remains for controller interrupt handling. `nbio_v7_9_handle_ras_err_event_athub_intr_no_bifring()` clears ATHUB error-event interrupt status and calls `ras_core_handle_fatal_error()`. `nbio_v7_9_get_memory_partition_mode()` reads `regBIF_BX_PF0_PARTITION_MEM_STATUS`, extracts the NPS mode mask, and returns `ffs(mem_mode)`. `ras_nbio_v7_9` exports the handlers.

Control flow and state: this file is stateless; all effects are MMIO register reads/writes and fatal-error notification. No persistence exists.

Dependencies and integration: it uses SOC15 register access macros, field macros, and core fatal handling. UMC hardware init depends on the NPS mode value returned here. Risks include the controller interrupt TODO, assuming `ffs()` of the NPS bitmask maps directly to NPS mode, missing synchronization around interrupt clear, and fatal handling during reset. Test signals should mock register values for no interrupt, controller interrupt, ATHUB interrupt, combined bits, invalid/zero NPS mode, and verify clear-bit writes plus fatal notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio_v7_9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio_v7_9.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio_v7_9.h

Purpose: this header exposes the NBIO v7.9 RAS function table.

Important definition: `extern const struct ras_nbio_ip_func ras_nbio_v7_9` is selected by generic NBIO init for NBIO IP versions 7.9.0 and 7.9.1.

Control flow and state: no active code or persistent state exists here.

Dependencies and integration: includes `ras_nbio.h` for the function-table type. Risks are minimal and mostly compile/link drift if the generic NBIO function table changes. Test signals are compile coverage and generic NBIO initialization selecting this symbol for both supported v7.9 versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio_v7_9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_process.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_process.c

Purpose: this file implements asynchronous RAS event processing. It queues poison/non-UMC events in a FIFO, counts UMC interrupt requests atomically, wakes a kernel thread, updates ECC data, handles bad-page/RMA reset flow, and notifies the host system.

Important functions: `ras_process_init()` allocates the event FIFO, initializes spinlock/waitqueue, and starts `ras_process_thread`. `ras_process_add_interrupt_req()` rejects uninitialized cores, then either increments UMC counters or queues non-UMC requests. `ras_process_handle_ras_event()` emits begin/end notifications, clears fatal flags, replays pending UMC banks, drains UMC event counts through `ras_process_umc_event()`, then drains non-UMC FIFO through `ras_process_non_umc_event()`. `ras_process_umc_event()` polls ACA ECC data until detected deferred-error count reaches interrupt count or timeout. `ras_process_non_umc_event()` notifies poison consumption and aggregates reset flags.

Control flow and state: `ras_process_thread()` waits for explicit interrupts or a 300 ms polling timeout, skips when not initialized or in reset, and delegates to a system async handler if provided. FIFO operations use spinlocked kfifo; UMC counts use atomics. Reset-caused mode1/RMA paths clear pending work.

Dependencies and risks: depends on core notifier callbacks, ACA ECC update/query, UMC pending-bank logging, reset status, and GPU reset notifications. Risks include event FIFO overflow, polling races between atomic count and ACA data readiness, losing events when mode1 reset clears state, and mixing timeout polling with explicit interrupts. Test signals should exercise UMC event bursts, non-UMC poison events with reset flags, RMA reset cause, GPU-in-reset skip, FIFO full, thread shutdown, async handler delegation, and begin/end notifier ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_process.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_process.h

Purpose: this header defines the RAS event-processing queue structures and public APIs.

Important types and APIs: `struct ras_event_req` carries sequence number, VF index, block, PASID, reset cause, optional PASID callback/data, and opaque data. `struct ras_process` stores device pointer, thread handle, waitqueue, atomic interrupt flags/counters, event FIFO, and FIFO spinlock. Public functions are `ras_process_init()`, `ras_process_fini()`, `ras_process_handle_ras_event()`, and `ras_process_add_interrupt_req()`.

Control flow and state: the header has no active logic. The declared structures capture volatile event state only; persistence happens through UMC/EEPROM after events are processed.

Dependencies and integration: used by `ras_core.c` hardware init/fini and by interrupt producers. Risks include ownership ambiguity for `data` and `pasid_fn`, fixed FIFO sizing in the implementation, and the need to distinguish UMC events from non-UMC events at enqueue time. Test signals should compile all producers, verify field initialization for stack-created requests, and assert `is_umc` routing matches event semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_process.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp.c

Purpose: this file implements the PSP and RAS TA command transport used for RAS TA loading/unloading, runtime error injection, and address translation queries. It manages shared GPU memory blocks, ring write-pointer access, PSP command serialization, TA sessions, and reset-lock coordination.

Important functions: `ras_psp_sw_init()` installs PSP system callbacks and initializes locks. `ras_psp_hw_init()` selects PSP v13 ring operations and synchronizes preloaded system TA status. `send_psp_cmd()` writes a PSP command buffer, ring frame, fence address/value, advances the ring write pointer, then waits for the fence or RAS interrupt. `send_ras_ta_runtime_cmd()` writes a `ras_ta_cmd`, invokes it, copies output, and checks TA status. `ras_psp_load_firmware()` and `ras_psp_unload_firmware()` manage TA firmware and sessions unless a preloaded TA is active. `ras_psp_trigger_error()` maps GFX/SDMA/VCN/JPEG instance masks and sends trigger-error. `ras_psp_query_address()` sends TA address translation. `ras_psp_check_supported_cmd()` gates query-address to preloaded TA and trigger-error to initialized TA.

Control flow and state: PSP state includes selected IP/system functions, internal or external PSP command mutex, fence counter, ring/command/fence/TA firmware/TA command GPU memory refcounts, TA firmware metadata, init flags, session ID, TA version, and initialization booleans. GPU memory is acquired lazily through core callbacks and released by refcount.

Dependencies and risks: depends on core GPU memory allocation, reset locks, interrupt detection, GFX subblock mapping, PSP v13 register ops, TA ABI structures, and system preload status. Risks include timeout returning success if the fence never matches but no `ret` is set, shared memory lifetime/refcount misuse, lock ordering with reset paths, freeing `fw_bin.bin_addr` ownership on unload, and relying on interrupt detection to treat injection as successful. Test signals should mock PSP ring/fence flow, command status failures, preloaded and dynamically loaded TA sessions, invalid TA interface version, reset-lock contention, GFX subblock validation, address query fallback, and memory refcount under repeated load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp.h

Purpose: this header defines PSP/RAS TA state, memory descriptors, function tables, firmware load/unload request structures, and public PSP APIs.

Important types: `struct ras_ta_image_header` exposes TA image version at offset 0x60. `struct ras_psp_sys_status` carries preloaded TA state and an external PSP mutex. `struct ras_ta_init_param` mirrors startup flags. `struct gpu_mem_block` describes shared GPU memory allocations with refcount. `struct ras_psp_ctx`, `ras_ta_ctx`, and `ras_psp` hold command/fence/firmware memory, locks, sessions, firmware metadata, selected IP/sys functions, and TA initialization state. `struct ras_psp_ta_load` and `ras_psp_ta_unload` are caller request/response containers.

Control flow and state: no active code lives here, but the structures define memory ownership and session state used by `ras_psp.c`. Persistence is not stored here; state is volatile and reset-sensitive.

Dependencies and integration: includes `ras_ta_if.h` and `ras.h`; used by core, UMC address translation, GFX error injection, and firmware loaders. Risks include ambiguous ownership of `bin_addr`, unchecked `void *` mutex/device fields, and tight coupling to PSP GFX ring command structures provided elsewhere. Test signals should compile all transport paths and include structure-size/field-offset checks where firmware ABI requires fixed layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp_v13_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp_v13_0.c

Purpose: this file provides PSP v13 ring write-pointer accessors for the generic PSP command transport.

Important functions: `ras_psp_v13_0_ring_wptr_get()` reads SOC15 MP0 register `regMP0_SMN_C2PMSG_67`. `ras_psp_v13_0_ring_wptr_set()` writes the same register with the new DWORD write pointer. `ras_psp_v13_0` exports these operations in a `struct ras_psp_ip_func`.

Control flow and state: the file is stateless; state lives in the PSP hardware register and the shared ring memory managed by `ras_psp.c`. There is no persistence.

Dependencies and integration: generic PSP init selects this table for PSP IP versions 13.0.6, 13.0.14, and 13.0.12. Command submission uses these callbacks to locate and advance the ring frame slot. Risks include incorrect register selection for future PSP v13 variants, no readback/validation in the setter, and reliance on caller conversion between byte and DWORD pointers. Test signals should mock register reads/writes, ring wrap handling in `ras_psp.c`, and supported IP version selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp_v13_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp_v13_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp_v13_0.h

Purpose: this header exposes the PSP v13 RAS IP function table.

Important definition: `extern const struct ras_psp_ip_func ras_psp_v13_0` is the table selected by generic PSP init for supported PSP v13 IP versions.

Control flow and state: no code or state is implemented here.

Dependencies and integration: includes `ras_psp.h` for the function-table type. Risks are limited to compile/link drift if the PSP interface changes. Test signals are generic PSP init coverage for supported v13 versions and linker coverage of this symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp_v13_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_ta_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_ta_if.h

Purpose: this header defines the host-side ABI for commands exchanged with the RAS Trusted Application through PSP shared memory.

Important definitions: `RAS_TA_HOST_IF_VER` is the host interface version. `enum ras_ta_cmd_id` covers feature enable/disable, trigger-error, block/subblock queries, and address queries. `enum ras_ta_status` enumerates success and TA/TEE/RAS error statuses. `enum ras_ta_block`, `ras_ta_mca_block`, `ras_ta_error_type`, `ras_ta_address_type`, and `ras_ta_nps_mode` define command domains. Input/output structs include feature toggles, trigger-error fields, TA init flags, MCA and physical address descriptors, query-address input/output, and output flags. `union ras_ta_cmd_input`, `union ras_ta_cmd_output`, and `struct ras_ta_cmd` form the shared command buffer layout.

Control flow and state: no code exists here. The packed-ish ABI is interpreted by `ras_psp.c` and TA firmware. Persistence is not represented.

Dependencies and integration: PSP transport writes `struct ras_ta_cmd` into GPU memory and checks `if_version`, `ras_status`, and output flags. UMC uses query-address for MCA-to-PA translation when supported. GFX/SDMA/VCN/JPEG injection uses trigger-error. Risks include ABI drift with TA firmware, enum value stability, command union size assumptions, and misspelled/uppercase constants that still affect source compatibility. Test signals should include shared-buffer size checks, interface-version rejection, each status-code diagnostic path, trigger-error instance packing, and query-address round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_ta_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc.c

Purpose: this file implements generic UMC bad-page handling, including MCA-to-physical conversion dispatch, bad-bank logging, deferred logging during reset, RAM/ROM bad-page views, EEPROM load/save, page reservation notifications, and public bad-page query helpers.

Important functions: `ras_umc_hw_init()` validates current NPS mode and VRAM type, records UMC IP version, and selects v12 functions. `ras_umc_log_bad_bank()` converts a `ras_bank_ecc` to an EEPROM record, inserts it into a tagged radix tree keyed by current-NPS PFN, reserves the page(s), and notifies bad-page detection. `ras_umc_handle_bad_pages()` drains newly tagged records, adds them to ROM/RAM arrays, then saves new records to firmware or physical EEPROM. `ras_umc_load_bad_pages()` reads persisted records and reserves them after reset/init. `ras_umc_add_bad_pages()` maintains ROM records and RAM-expanded page records, suppressing duplicates. Public helpers return counts, records, retired-address checks, and SOC PA/bank translations.

Control flow and state: software init sets radix tree, pending list, and mutexes. UMC state includes IP version, VRAM type, selected IP functions, newly detected radix tree, pending ECC list, `rom_data` matching persisted records, `ram_data` expanded to actual pages to reserve/query, current NPS mode, and last retired PFN. EEPROM record timestamps use a compact 2000-2031 bitfield.

Dependencies and risks: depends on UMC v12 conversion callbacks, PSP query-address support, EEPROM backends, core notifications, ACA bank formats, reset locks, and NBIO NPS mode. Risks include duplicate suppression assumptions, memory growth/reallocation, converting persisted records across NPS changes, pending-list replay after reset, and relying on firmware EEPROM read-index semantics. Test signals should cover physical and firmware EEPROM paths, NPS1/2/4/8 conversions, duplicate bad bank logging, reset-pending replay, disabled retirement, page reservation notifications, RAM/ROM count divergence, and clean shutdown freeing all dynamic arrays/lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc.h

Purpose: this header defines UMC memory types, address structures, IP conversion callbacks, bad-page storage structures, UMC runtime state, and public UMC APIs.

Important types and macros: VRAM constants cover GDDR, DDR, HBM, LPDDR, and HBM3E. `enum umc_memory_partition_mode` defines NPS modes. `struct umc_mca_addr`, `umc_phy_addr`, and `umc_bank_addr` represent MCA, physical, and decoded bank forms. `struct ras_umc_ip_func` supplies IP-specific conversions between banks, SOC PA, EEPROM records, NPS records/pages, and MCA IPID parsing. `struct eeprom_store_record`, `ras_umc_err_data`, and `ras_umc` track persisted-style records, expanded RAM bad-page records, locks, radix tree, and pending ECC list.

Control flow and state: no implementation lives here. The exported APIs initialize/finalize UMC, convert addresses, log bad banks, load/save/clean bad-page data, query records/counts, and translate between SOC PA and bank fields.

Dependencies and integration: includes `ras.h`, `ras_eeprom.h`, and `ras_cmd.h`; interacts with ACA, EEPROM, PSP TA, NBIO NPS mode, and core notifications. Risks are contract-related: each supported UMC IP must implement all callbacks that generic code assumes, and record fields contain both serialized and runtime-only interpretations. Test signals should include callback-null handling, structure field population from firmware and physical EEPROM records, and public query behavior before and after `ras_umc_clean_badpage_data()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc_v12_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc_v12_0.c

Purpose: this file implements UMC v12 address conversion and bad-page retirement math. It converts MCA error addresses and IPID fields into SOC physical row addresses, expands a retired row into all page PFNs that need reservation, and translates between SOC PA and bank-address forms.

Important functions/data: `umc_v12_0_channel_idx_tbl` maps node/UMC/channel instances to channel indices. `umc_v12_0_ma2na_mapping` converts MCA address bits to normalized address bits. `__get_nps_pa_flip_bits()` selects row/column flip bits by NPS mode and HBM/HBM3E type. `convert_nps_pa_to_row_pa()` normalizes a PA to the retirement row. `lookup_bad_pages_in_a_row()` enumerates all PFNs in the retirement unit and optionally logs row/column/bank/channel details. `umc_v12_convert_ma_to_pa()` performs the software MCA-to-PA conversion. `convert_ma_to_pa()` prefers PSP TA query-address when supported. `umc_v12_0_bank_to_eeprom_record()` converts ACA bank data to `eeprom_umc_record`. EEPROM-record conversion, SOC PA-to-bank, bank-to-SOC PA, and IPID parse callbacks complete `ras_umc_func_v12_0`.

Control flow and state: the file is mostly stateless and deterministic, reading `ras_core->ras_umc.umc_vram_type`, GFX version, and firmware EEPROM support. It writes runtime fields into `eeprom_umc_record` but owns no persistence.

Dependencies and risks: depends on UMC v12 bit macros from its header, ACA IPID/address macros, PSP TA availability, device system info, GFX version, and RAS address/PFN macros. Risks are high because address mapping is hardware-specific: NPS handling, HBM3E row-bit changes, channel hash reversal, socket offsets, and firmware-vs-physical EEPROM record interpretations can retire wrong pages if wrong. Test signals should use golden MCA/IPID/PA vectors for NPS1/2/4/8, HBM and HBM3E, PSP-query and software fallback paths, reverse SOC PA-to-bank conversion, zero-PFN handling, and GFX 9.5 row-high behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_umc_v12_0.c -->
