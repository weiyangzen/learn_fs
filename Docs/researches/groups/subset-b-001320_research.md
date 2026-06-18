# subset-b-001320 AMDGPU RAS research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras.c

## Purpose

`amdgpu_ras.c` is the central AMDGPU RAS (Reliability, Availability, Serviceability) implementation. It owns RAS feature discovery and enablement, per-IP RAS manager objects, sysfs/debugfs control surfaces, error query and injection dispatch, interrupt bottom halves, poison handling, GPU recovery scheduling, bad-page retirement, persistent bad-page restore/save through EEPROM, event IDs, and several platform-specific paths for SR-IOV, UniRAS, ACA/MCA, XGMI hives, and x86 MCE.

The file sits between generic AMDGPU device lifecycle code, per-IP RAS block implementations, PSP/RAS TA firmware, PMFW/SMU, NBIO fatal interrupt support, VRAM manager reservation, UMC address conversion, and the EEPROM backend in `amdgpu_ras_eeprom.c`.

## Important APIs, Types, And Functions

- Global lookup strings and helpers: `ras_error_string`, `ras_block_string`, `ras_mca_block_string`, `get_ras_block_str()`, `ras_block_str()`, and `ras_err_str()` provide human-readable block/error names used in logs and filesystem nodes.
- Context accessors: `amdgpu_ras_get_context()` and `amdgpu_ras_set_context()` store the `struct amdgpu_ras` pointer in `adev->psp.ras_context.ras`.
- Lifecycle APIs: `amdgpu_ras_init()`, `amdgpu_ras_late_init()`, `amdgpu_ras_resume()`, `amdgpu_ras_suspend()`, `amdgpu_ras_pre_fini()`, and `amdgpu_ras_fini()` allocate, configure, expose, and tear down the RAS subsystem.
- Per-block registration and lifecycle: `amdgpu_ras_register_ras_block()`, `amdgpu_ras_block_late_init()`, `amdgpu_ras_block_late_fini()`, `amdgpu_ras_find_obj()`, `amdgpu_ras_create_obj()`, and `put_obj()` manage `struct ras_manager` instances for each RAS block and MCA sub-block.
- Feature control: `amdgpu_ras_feature_enable()`, `amdgpu_ras_feature_enable_on_boot()`, `amdgpu_ras_enable_all_features()`, `amdgpu_ras_disable_all_features()`, `amdgpu_ras_is_supported()`, `amdgpu_ras_is_feature_allowed()`, and `amdgpu_ras_is_feature_enabled()` maintain `con->features` and communicate feature state to PSP RAS TA where needed.
- Query and reset: `amdgpu_ras_query_error_status()`, `amdgpu_ras_query_error_status_with_event()`, `amdgpu_ras_query_error_status_helper()`, `amdgpu_ras_query_error_count()`, `amdgpu_ras_reset_error_count()`, and `amdgpu_ras_reset_error_status()` collect CE/UE/DE counters by direct IP callbacks, ACA/MCA firmware logging, SR-IOV host telemetry, or UniRAS command paths.
- Error injection: `amdgpu_ras_error_inject()` and `amdgpu_uniras_error_inject()` route debugfs injection requests to UniRAS, IP-specific `ras_error_inject`, or PSP `psp_ras_trigger_error()`.
- Filesystem interfaces: `amdgpu_ras_fs_init()`, `amdgpu_ras_fs_fini()`, `amdgpu_ras_sysfs_create()`, `amdgpu_ras_sysfs_remove()`, `amdgpu_ras_debugfs_create_all()`, `amdgpu_ras_debugfs_ctrl_write()`, `amdgpu_ras_debugfs_eeprom_write()`, and read helpers expose error counts, bad pages, feature/schema/version/event state, injection, EEPROM reset, thresholds, and EEPROM dump data.
- Interrupt handling: `amdgpu_ras_interrupt_add_handler()`, `amdgpu_ras_interrupt_dispatch()`, `amdgpu_ras_interrupt_handler()`, `amdgpu_ras_interrupt_poison_creation_handler()`, `amdgpu_ras_interrupt_poison_consumption_handler()`, `amdgpu_ras_interrupt_umc_handler()`, `amdgpu_ras_global_ras_isr()`, and `amdgpu_ras_interrupt_fatal_error_handler()` bridge IH entries to deferred work, poison handling, and reset scheduling.
- Recovery and bad pages: `amdgpu_ras_recovery_init()`, `amdgpu_ras_recovery_fini()`, `amdgpu_ras_do_recovery()`, `amdgpu_ras_reset_gpu()`, `amdgpu_ras_add_bad_pages()`, `amdgpu_ras_save_bad_pages()`, `amdgpu_ras_load_bad_pages()`, `amdgpu_ras_reserve_page()`, and `amdgpu_ras_check_bad_page()` maintain bad-page state and recover the GPU or XGMI hive.
- Page retirement and poison queues: `amdgpu_ras_put_poison_req()`, `amdgpu_ras_page_retirement_thread()`, `amdgpu_ras_poison_creation_handler()`, `amdgpu_ras_poison_consumption_handler()`, `amdgpu_ras_do_page_retirement()`, and `amdgpu_ras_ecc_log_init()/fini()` process deferred UMC poison events, PASID callbacks, VRAM retirement, and reset requirements.
- Event accounting: `amdgpu_ras_event_mgr_init()`, `ras_event_mgr_init()`, `amdgpu_ras_mark_ras_event_caller()`, `amdgpu_ras_acquire_event_id()`, and `amdgpu_ras_event_log_print()` maintain per-event sequence IDs and print tagged logs for fatal, poison creation, and poison consumption events.
- Per-instance register helpers: `amdgpu_ras_inst_get_memory_id_field()`, `amdgpu_ras_inst_get_err_cnt_field()`, `amdgpu_ras_inst_query_ras_error_count()`, and `amdgpu_ras_inst_reset_ras_error_count()` support block implementations that expose RAS status in register tables.
- Error data aggregation: `amdgpu_ras_error_data_init()`, `amdgpu_ras_error_data_fini()`, `amdgpu_ras_error_statistic_ce_count()`, `amdgpu_ras_error_statistic_ue_count()`, and `amdgpu_ras_error_statistic_de_count()` maintain total and socket/die-scoped counters in linked `ras_err_node` lists.
- Critical-region protection: `amdgpu_ras_add_critical_region()`, `amdgpu_ras_check_critical_address()`, `amdgpu_ras_critical_region_init()`, and `amdgpu_ras_critical_region_fini()` keep firmware/reserved VRAM regions from being treated as ordinary bad-page reservation targets.

## Control Flow

Initialization begins in `amdgpu_ras_init()`. It allocates `struct amdgpu_ras` plus a contiguous array of `struct ras_manager` slots, stores it in the PSP RAS context, and calls `amdgpu_ras_check_supported()` to fill `adev->ras_hw_enabled`, `adev->ras_enabled`, poison support, and ACA enablement. If RAS is disabled, most initialization is skipped, except a special Vega20 disabled-GFX context used to issue a later RAS disable command. Otherwise the file initializes NBIO RAS support early, creates the common sysfs group, initializes ACA/MCA support where applicable, records the task that initialized the driver, and creates the critical-region list.

Late init is two-phase. `amdgpu_ras_late_init()` initializes the shared event manager, resets ACA/MCA state on reset recovery, then iterates `adev->ras_list`. Each registered `amdgpu_ras_block_object` either calls its own `ras_late_init` or the default `amdgpu_ras_block_late_init()`. The default path checks support, enables the block through boot-aware feature control, optionally harvests persistent EDC counters, installs an interrupt handler when the block provides a RAS callback or poison consumption hooks, creates per-block sysfs count files when query hooks exist, and seeds cached CE/UE counts.

Feature enablement is split between software bookkeeping and PSP firmware control. `amdgpu_ras_feature_enable()` sends PSP RAS TA commands for host-side GFX enable/disable when appropriate, then calls `__amdgpu_ras_feature_enable()` to create or release the manager object and set or clear `con->features`. Boot-time enablement treats VBIOS-initialized RAS specially and can create software objects even if older RAS TA calls return `-EINVAL`.

Query flow starts from sysfs/debugfs reads, periodic delayed work, recovery harvesting, or public callers. `amdgpu_ras_query_error_status_with_event()` allocates temporary `ras_err_data`, chooses a mode via `amdgpu_ras_get_error_query_mode()`, creates an event ID when needed, takes the reset-domain read semaphore with `down_read_trylock()`, and calls `amdgpu_ras_query_error_status_helper()`. The helper selects SR-IOV host telemetry, direct UMC/IP callbacks, ACA/MCA firmware logging, or UniRAS commands. Results are merged into the manager’s persistent counters and printed through event-tagged logs. For virtual telemetry, host-provided absolute counters are diffed against previous local counters before updating local state.

Interrupt flow stores incoming IV entries in a per-block software ring and schedules `ih_work`. In poison mode, UMC interrupts are treated as poison creation and non-UMC interrupts as poison consumption. Creation events mark a RAS event and wake the page-retirement thread for UMC 12.x and newer. Consumption events set block poison state, optionally confirm poison status through block hooks, run UMC poison handling, call block consumption handlers, and schedule GPU reset when required. Without poison mode, UMC interrupts call the IP-provided callback and accumulate returned CE/UE/DE counts.

Fatal interrupt flow uses `amdgpu_ras_global_ras_isr()` and `amdgpu_ras_interrupt_fatal_error_handler()`. The global ISR marks a fatal event once through `amdgpu_ras_in_intr`, logs the ERREVENT, sets fatal error detected state, requests mode1 reset, and schedules recovery. The fatal handler polls/acks NBIO RAS controller and ATHUB fatal status for hardware without the necessary BIF rings, while skipping duplicate handling when a non-fatal RAS error is already in state.

Recovery is scheduled through `amdgpu_ras_reset_gpu()`, which sets `ras->in_recovery`, accounts for XGMI hive recovery already in progress, and schedules `recovery_work` on the reset domain. `amdgpu_ras_do_recovery()` marks hive recovery, propagates fatal error status across hive members, harvests RAS counters unless disabled, builds a single-device or hive device list, queries UniRAS or traditional RAS error status, chooses reset flags (full reset, mode1, mode2), calls `amdgpu_device_gpu_recover()`, and clears recovery state.

Bad-page restore starts in `amdgpu_ras_init_badpage_info()`: it initializes the EEPROM control, loads EEPROM records when valid, converts records from old PA layout or newer MCA/NPS layout as needed, reserves retired pages in VRAM, sends bad-page counts and channel bitmaps to SMU, and can reformat older UMC 12.x EEPROM records into V3 layout. New bad pages are added through `amdgpu_ras_add_bad_pages()`, which deduplicates by retired page, reserves VRAM with `amdgpu_ras_reserve_page()`, grows the bad-page array in 512-record aligned chunks, and increments `con->bad_page_num`. `amdgpu_ras_save_bad_pages()` appends only newly added units to EEPROM, using one record per retire unit on UMC 12.x+ and older PA-style groups on older ASICs.

Page retirement has a dedicated kernel thread. Interrupts and KFD/UMC poison consumers enqueue requests in atomic counters and `poison_fifo`. The thread processes poison creation first, repeatedly querying UMC error status until deferred pages and consumption queues appear or timeout expires. It then processes consumption messages, invokes PASID callbacks, combines requested reset flags, flushes page-retirement work, and triggers GPU reset when necessary. Delayed work `amdgpu_ras_do_page_retirement()` runs outside reset/recovery windows, asks UMC to handle bad pages, and reschedules while new deferred pages remain tagged in the ECC log radix tree.

Finalization unwinds in ordered stages. `amdgpu_ras_pre_fini()` disables features and stops recovery/page-retirement state. `amdgpu_ras_fini()` clears critical regions, calls per-block fini/default late fini, removes registered block nodes, removes sysfs/debugfs references, removes interrupt handlers, tears down ACA/MCA, cancels periodic count work, clears the PSP context, and frees the RAS context.

## State And Persistence Behavior

Persistent runtime state lives mostly in `struct amdgpu_ras`: feature and schema masks, manager list, per-block manager array, recovery work and locks, EEPROM control, bad-page threshold and bad-page count, poison support, poison FIFO, page-retirement counters, ECC radix tree, RAS error bit state, event manager, critical-region list, RMA flag, UniRAS and SMU driver pointers, and reserved VRAM size.

Per-block state lives in `struct ras_manager`: a `ras_common_if` key, reference count, sysfs/debugfs metadata, interrupt ring state, accumulated `ras_err_data`, and optional ACA handle. Manager lifetimes are manual through `get_obj()` and `put_obj()` rather than kernel refcount APIs.

Bad-page persistence spans `con->eh_data` and the EEPROM control. `eh_data->bps` caches `struct eeprom_table_record` entries, `count` is the in-memory count, `count_saved` marks the first unsaved record, and `space_left` tracks allocation slack. EEPROM record counts and table validity are maintained by `amdgpu_ras_eeprom.c`; this file decides when to load, convert, reserve, and save records. Records loaded from EEPROM can be marked invalid by setting `retired_page = U64_MAX` when already known, but the in-memory slot is still consumed.

The error counters in `ras_manager.err_data` are long-lived totals. Query-time temporary `ras_err_data` instances collect deltas or current host counts, then merge into the manager totals. When source information is available, counts are stored per socket/die in sorted linked nodes; legacy paths update flat CE/UE/DE counters.

Event state can be per-device or shared by XGMI hive through `hive->event_mgr`. Event IDs are not allocated per log call; the event marker increments a sequence and the acquire function returns the last sequence for that event type. Logs therefore rely on callers marking events before acquiring/logging.

Critical VRAM regions are persisted only for the driver lifetime, not across boot. The firmware reserved BO is registered as a critical region at recovery teardown/init points, and page reservation skips addresses inside those regions.

## Dependencies And Integration Points

- PSP/RAS TA: `psp_ras_enable_features()`, `psp_ras_trigger_error()`, and `psp_fatal_error_recovery_quirk()` provide firmware control for feature toggles, injection, and fatal recovery quirks.
- Per-IP RAS block objects: `adev->ras_list` entries supply block matching, late init/fini, interrupt callbacks, and `amdgpu_ras_block_hw_ops` for query, reset, poison, and injection behavior.
- UMC: UMC callbacks perform ECC query, error address conversion, PA/MCA conversion, page lookup, bad-page handling, retire-unit sizing, flip-bit setup, and page-retirement MCA handling.
- EEPROM backend: `amdgpu_ras_eeprom_init()`, `read()`, `append()`, `check()`, `reset_table()`, `max_record_count()`, and debugfs helpers persist bad-page records and RMA state.
- SMU/DPM/PMFW: `amdgpu_dpm_get_ecc_info()`, `amdgpu_dpm_send_hbm_bad_pages_num()`, `amdgpu_dpm_send_hbm_bad_channel_flag()`, `amdgpu_dpm_get_ras_smu_driver()`, and `amdgpu_dpm_send_rma_reason()` integrate with firmware telemetry and notifications.
- ACA/MCA: `amdgpu_aca_*` and `amdgpu_mca_*` provide firmware error collection, debug mode, reset/fini, sysfs, and debugfs support.
- SR-IOV and UniRAS: virtual functions use host telemetry through `amdgpu_virt_req_ras_err_count()`, address validation through `amdgpu_virt_ras_*`, and UniRAS command handling through `amdgpu_ras_mgr_handle_ras_cmd()`.
- NBIO/NBIF: ASIC-specific NBIO RAS structs initialize fatal-controller and ATHUB interrupts and provide fatal interrupt ack/poll handlers.
- Reset domain: recovery uses reset-domain scheduling and semaphores to serialize against GPU reset; EEPROM and query paths avoid unsafe access during reset.
- VRAM manager: `amdgpu_vram_mgr_query_page_status()`, `reserve_range()`, `query_address_block_info()`, and resource block helpers determine reservation state and critical regions.
- KFD: poison consumption sets an SRAM ECC flag and can invoke PASID callbacks so clients can react to poisoned memory ownership.
- Linux kernel infrastructure: debugfs/sysfs, workqueues, delayed work, kthread, waitqueue, kfifo, radix tree, list sorting, atomics, mutexes, rwsems, x86 MCE notifier, and module parameters.

## Risks And Edge Cases

- Manager refcounting is custom and easy to unbalance. Some paths create objects for interrupts before feature enablement, while sysfs/debugfs and feature toggling take additional references.
- Interrupt software rings have no explicit overflow handling beyond a comment; `wptr` can lap `rptr` if interrupts arrive faster than work processing.
- `amdgpu_ras_query_error_status_with_event()` returns `-EINVAL` without freeing `err_data` if `amdgpu_ras_get_error_query_mode()` fails after initialization, though current `ras_err_data_init()` only initializes a list head.
- Bad-page conversion paths are highly version- and NPS-dependent. Incorrect detection of old PA records versus MCA records can mis-convert retired pages, especially around UMC 12.x and table V3 transitions.
- `amdgpu_ras_save_bad_pages()` computes unsaved unit counts partly outside the lock, then uses `data` after releasing `recovery_lock`; concurrent retirement updates would need careful reasoning.
- Threshold handling changes behavior based on module parameter values `-2`, `-1`, `0`, and custom positive values. Custom thresholds can set RMA and force mode1 reset; defaults warn but keep service.
- Debugfs control can directly retire pages and warns that this is test-only and corrupts RAS EEPROM. Address validation attempts to block critical, already bad, and owned pages but is necessarily platform-specific.
- Error query/reset is blocked or altered during reset/recovery and ACA/MCA debug modes. Tests need to cover direct, firmware, and virtual modes because they update counters differently.
- UniRAS and legacy RAS paths are interleaved. Many public functions branch early to UniRAS, which can bypass local event accounting and EEPROM behavior.
- XGMI hive recovery shares state across devices. Fatal status propagation and duplicate recovery suppression depend on correct hive reference handling and atomic state transitions.
- `amdgpu_ras_recovery_fini()` calls `amdgpu_ras_critical_region_init()` during teardown, which looks surprising and should be checked against broader lifecycle assumptions.
- Several paths intentionally return success when unsupported, disabled, or running on SR-IOV guests. Callers must distinguish "not applicable" from real success when adding behavior.

## Test Signals

- Boot with supported and unsupported ASIC/IP-version combinations and verify `ras_hw_enabled`, `ras_enabled`, `schema`, poison support, ACA enablement, and NBIO RAS selection.
- Exercise per-block late init and fini for blocks with and without callbacks, hw_ops, sysfs nodes, and ACA handles; verify manager reference counts end at zero.
- Read sysfs `features`, `version`, `schema`, `event_state`, per-block `*_err_count`, and `gpu_vram_bad_pages`; confirm inaccessible query state, reset auto-clear behavior, and UMC DE output.
- Use debugfs `ras_ctrl` for enable, disable, injection with and without instance masks, retire_page, and check_address; include malformed commands and unsupported blocks.
- Test direct, firmware/MCA/ACA, SR-IOV virtual, and UniRAS error query modes and confirm CE/UE/DE totals and event logs are updated correctly.
- Trigger poison creation and consumption interrupts; validate event IDs, FIFO handling, PASID callbacks, KFD SRAM ECC flag, page-retirement work scheduling, and requested reset mode selection.
- Trigger fatal RAS interrupt and verify FED state, mode1/full reset flags, hive propagation, NBIO ack paths, emergency restart decision on Vega20 firmware, and recovery clearing.
- Seed EEPROM with V1, V2.1, V3, old PA-style, MCA-style, SMU-managed, wrapped, corrupted, threshold-exceeded, and near-threshold tables; verify load, conversion, bad-page reservation, RMA setting, and reformat/save behavior.
- Race tests around reset-domain semaphore, concurrent sysfs queries, delayed page retirement, recovery work, and EEPROM access are important because the file relies on multiple locks and workqueues.
- Build coverage should include `CONFIG_DEBUG_FS`, `CONFIG_X86_MCE_AMD`, SR-IOV VF, APU, XGMI-connected CPU, and UniRAS configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras.h

## Purpose

`amdgpu_ras.h` defines the public and internal contract for the AMDGPU RAS subsystem. It names all RAS blocks, error types, query modes, event types, persistent runtime structures, per-block callback interfaces, bad-page structures, poison handling structures, EEPROM/SMU integration hooks, and exported functions used by AMDGPU IP blocks and lifecycle code.

The header is the coordination point between `amdgpu_ras.c`, the EEPROM backend, per-IP RAS implementations, PSP TA RAS definitions, SMU/MCA/ACA helpers, VRAM bad-page handling, and driver lifecycle code.

## Important APIs, Types, And Constants

- Boot and firmware error bit helpers: `AMDGPU_RAS_GPU_ERR_*`, `AMDGPU_RAS_BOOT_STATUS_*`, and related masks decode MP0 boot-status messages for memory training, firmware load, link training, HBM tests, aborts, and generic boot controller errors.
- Feature and event constants: `AMDGPU_RAS_FLAG_INIT_BY_VBIOS`, `AMDGPU_RAS_INST_MASK`, `AMDGPU_RAS_FEATURES_SOCKETID_*`, `AMDGPU_RAS_RESERVED_VRAM_SIZE_DEFAULT`, `RAS_EVENT_INVALID_ID`, `RAS_EVENT_ID_IS_VALID()`, and `RAS_EVENT_LOG()` encode RAS state conventions.
- `enum amdgpu_ras_block` lists RAS-capable blocks: UMC, SDMA, GFX, MMHUB, ATHUB, PCIE_BIF, HDP, XGMI_WAFL, DF, SMN, SEM, MP0, MP1, FUSE, MCA, VCN, JPEG, IH, MPIO, MMSCH, plus sentinel/ANY values.
- `enum amdgpu_ras_mca_block` splits MCA sub-blocks into MP0, MP1, MPIO, and IOHC. `AMDGPU_RAS_BLOCK_COUNT`, `AMDGPU_RAS_MCA_BLOCK_COUNT`, and `AMDGPU_RAS_BLOCK_MASK` derive table sizes and feature masks.
- `enum amdgpu_ras_gfx_subblock` enumerates detailed GFX SRAM/ECC sub-blocks across CPC, CPF, CPG, GDS, SPI, SQ, SQC, TA, TCA, TCC, TCI, TCP, TD, EA, UTC VML2, and ATC cache/walker regions for injection and reporting.
- `enum amdgpu_ras_error_type` defines parity, single correctable, multi uncorrectable, and poison error categories. Inline `amdgpu_ras_error_to_ta()` maps them to PSP TA RAS values.
- `enum amdgpu_ras_error_query_mode` distinguishes invalid, direct, firmware, and virtual host-count query modes.
- Register decoding helpers: `ERR_STATUS_*`, `AMDGPU_RAS_REG_ENTRY()`, `AMDGPU_RAS_REG_ENTRY_OFFSET()`, and `AMDGPU_RAS_ERR_*_VALID` support table-driven IP register scans.
- Core keys and ECC data: `struct ras_common_if`, `struct ecc_info_per_ch`, `struct umc_ecc_info`, `struct ras_ecc_err`, and `struct ras_ecc_log_info`.
- Event tracking: `enum ras_event_type`, `struct ras_event_state`, `struct ras_event_manager`, `struct ras_event_id`, and `struct ras_query_context`.
- Poison and bad-page structures: `struct ras_poison_msg`, `struct ras_err_pages`, `struct ras_critical_region`, `struct ras_badpage`, `struct ras_cure_if`, and `struct ras_inject_if`.
- SMU EEPROM integration: `struct ras_eeprom_table_version`, `struct ras_eeprom_smu_funcs`, `enum ras_smu_feature_flags`, and `struct ras_smu_drv`.
- Main runtime context: `struct amdgpu_ras` stores feature/schema masks, manager objects, sysfs/debugfs attributes, recovery state, EEPROM control, thresholds, poison support, delayed work, error counters, UMC ECC cache, page-retirement queues, poison FIFO, event manager, reserved VRAM size, init task identity, critical-region list, UniRAS flag, and SMU RAS driver pointer.
- Per-block manager and object contracts: `struct ras_manager`, `struct amdgpu_ras_block_object`, and `struct amdgpu_ras_block_hw_ops` define how IP blocks register, match, initialize, query, reset, inject, and handle poison.
- Filesystem and command wrapper types: `struct ras_fs_if`, `struct ras_query_if`, `struct ras_ih_if`, `struct ras_dispatch_if`, and `struct ras_debug_if`.
- Public function declarations cover initialization, recovery, suspend/resume, feature enablement, sysfs/debugfs, query/reset/inject, interrupt dispatch, bad-page add/save/reserve, context access, RAS block registration, register-count helpers, error-data helpers, ACA binding, FED/error state, event IDs, critical regions, poison requests, RMA state, and reset pre/post hooks.

## Control Flow Encoded By The Header

The workflow comment describes the high-level RAS sequence: VBIOS enables features, PSP/RAS framework initializes in IP init, IPs add interrupt handlers, debugfs/sysfs nodes are created, user or driver code queries/injects errors, filesystem nodes and handlers are removed, and features are disabled.

The main `struct amdgpu_ras` layout enforces that lifecycle order. Early init sets feature/schema masks and the manager array. Late init creates `ras_manager` instances for registered IP blocks and binds sysfs/debugfs/IH state. Recovery init fills EEPROM and page-retirement fields. Fini tears those same pieces down.

The callback interface `struct amdgpu_ras_block_object` lets IP blocks customize block matching for sub-blocks, late init, fini, and interrupt callbacks while sharing common manager state. `struct amdgpu_ras_block_hw_ops` is the direct hardware operation table for injection, count/status/address query, reset, poison status, and poison consumption.

The query path shape is visible in `struct ras_query_if` plus `struct ras_err_data`: callers specify the block through `ras_common_if`, and implementation code fills aggregate CE/UE/DE counts and optional per-socket/die `ras_err_node` data.

The poison path shape is visible in `ras_poison_msg` and the page-retirement fields inside `struct amdgpu_ras`: producers queue block/PASID/reset requests, and the implementation consumes them through a FIFO and waitqueue-backed kthread.

## State And Persistence Behavior

This header defines both transient driver state and state mirrored into persistent storage. `struct amdgpu_ras_eeprom_control` from `amdgpu_ras_eeprom.h` is embedded in `struct amdgpu_ras`, making the EEPROM table part of the live RAS context. Bad pages are represented by `struct eeprom_table_record` in the EEPROM header and by in-memory `ras_err_handler_data`/`ras_badpage` declarations here.

Feature state is split between `adev->ras_hw_enabled`/`adev->ras_enabled` in the device and `amdgpu_ras.features` in the context. The high bits of `features` can carry socket ID while `AMDGPU_RAS_GET_FEATURES()` masks it off for feature-only checks.

Recovery state is represented by atomics (`in_recovery`, `rma_in_recovery`, page-retirement counters, poison counters, CE/UE cached counts), work items (`recovery_work`, `ras_counte_delay_work`, `page_retirement_dwork`), mutexes, waitqueues, and `gpu_reset_flags`.

Event state can be owned locally in `__event_mgr` or shared through `event_mgr` when XGMI hive code points multiple devices at hive-level event state.

Error statistics can be flat (`ue_count`, `ce_count`, `de_count`) or source-aware (`err_node_list` keyed by `amdgpu_smuio_mcm_config_info`), which allows newer platforms to report socket/die-local totals without changing the public query API.

## Dependencies And Integration Points

- Includes `ta_ras_if.h` for PSP TA RAS enums and inline conversions.
- Includes `amdgpu_ras_eeprom.h` for persistent bad-page records and EEPROM control.
- Includes `amdgpu_smuio.h` for socket/die metadata used in error nodes.
- Includes `amdgpu_aca.h` for ACA handle binding inside `ras_manager`.
- Uses Linux debugfs, list, kfifo, and radix-tree APIs in public structure fields, so implementation files must observe kernel lifetime and locking rules.
- Public declarations are consumed by UMC, GFX, SDMA, MMHUB, NBIO, XGMI, KFD/poison, reset, PSP, SMU, and virtualized RAS code.

## Risks And Edge Cases

- The header exposes large mutable structures directly, so internal representation changes can ripple through many AMDGPU IP files.
- `struct amdgpu_ras` embeds many synchronization primitives and work items. Fini order must match field lifetimes exactly or callbacks can observe freed context.
- `struct ras_manager.use` is an `int`, not a `refcount_t`; over/under-release risks are handled by runtime warnings rather than type safety.
- `enum amdgpu_ras_block` values are used as bit indices, array indices, sysfs naming inputs, and TA conversion inputs. Adding blocks requires coordinated updates to strings, masks, conversions, and block object registration.
- MCA sub-blocks are represented by using `AMDGPU_RAS_BLOCK__MCA` plus `sub_block_index`, while the manager array stores them after normal block slots. Indexing must stay consistent with `AMDGPU_RAS_BLOCK_COUNT + AMDGPU_RAS_MCA_BLOCK_COUNT`.
- `ras_debug_if` overlays `ras_common_if` and `ras_inject_if` in a union and is accepted through debugfs, so layout changes affect userspace debug tooling.
- Some macros rely on fixed register field names (`ERR_STATUS_LO`, `ERR_STATUS_HI`, `ERR_STATUS`) and generated AMDGPU register macros being present in implementation contexts.
- `RAS_EVENT_LOG` depends on a valid event ID convention; invalid IDs intentionally print untagged messages, which can make event correlation incomplete if callers forget to mark events.

## Test Signals

- Compile all AMDGPU RAS-enabled configurations to catch callback signature or structure-layout drift.
- Add or modify any RAS block only with checks that `ras_block_string`, TA conversion, support masks, sysfs/debugfs naming, and manager indexing remain aligned.
- Exercise debugfs binary `ras_debug_if` compatibility if any struct layout changes.
- Validate XGMI hive and single-device event-manager initialization because the same public fields support both modes.
- Verify bad-page, poison FIFO, delayed work, and recovery fields are initialized before use and destroyed after all work/threads/interrupt handlers are stopped.
- Use sparse/lockdep/KASAN-style tests around callback use, manager refcounts, and workqueue teardown because many fields are exposed to asynchronous IP code.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras_eeprom.c

## Purpose

`amdgpu_ras_eeprom.c` implements the persistent RAS bad-page table backend for AMDGPU. It detects whether a platform supports RAS EEPROM, locates the EEPROM table in I2C address space or delegates to SMU-managed EEPROM, initializes or resets table metadata, serializes and deserializes table records, appends bad-page records with circular-buffer semantics, verifies and repairs checksums, updates RMA/health status, exposes debugfs table dumps, and wraps SMU/PMFW RAS EEPROM operations.

The file is the persistence layer used by `amdgpu_ras.c` for loading retired pages during driver initialization and saving newly retired pages during page-retirement work.

## Important APIs, Types, And Functions

- EEPROM addressing constants: `EEPROM_I2C_MADDR_0` and `EEPROM_I2C_MADDR_4` are the two supported base memory addresses for the RAS table.
- Table layout constants: `RAS_TABLE_HEADER_SIZE`, `RAS_TABLE_RECORD_SIZE`, `RAS_TABLE_HDR_VAL`, `RAS_TABLE_HDR_BAD`, `RAS_TBL_SIZE_BYTES`, `RAS_RECORD_START`, `RAS_RECORD_START_V2_1`, `RAS_MAX_RECORD_COUNT`, and `RAS_MAX_RECORD_COUNT_V2_1` define V1 and V2.1/V3 on-EEPROM layouts.
- Index macros: `RAS_INDEX_TO_OFFSET()`, `RAS_OFFSET_TO_INDEX()`, `RAS_RI_TO_AI()`, `RAS_NUM_RECS()`, and `RAS_NUM_RECS_V2_1()` convert between record indices, byte offsets, and circular-buffer relative positions.
- Platform detection: `__is_ras_eeprom_supported()` gates all EEPROM functionality by MP1 IP version and APU/platform conditions. `__get_eeprom_i2c_addr()` chooses the EEPROM base address from VBIOS atom firmware when present or from ASIC/VBIOS part-number rules.
- Serialization helpers: `__encode_table_header_to_buf()`, `__decode_table_header_from_buf()`, `__encode_table_ras_info_to_buf()`, `__decode_table_ras_info_from_buf()`, `__encode_table_record_to_buf()`, and `__decode_table_record_from_buf()` translate host structures to little-endian packed on-EEPROM bytes.
- Header/info writes and checksums: `__write_table_header()`, `__write_table_ras_info()`, `__calc_hdr_byte_sum()`, `__calc_ras_info_byte_sum()`, `amdgpu_ras_eeprom_update_header()`, and `__verify_ras_table_checksum()`.
- Table reset and correction: `amdgpu_ras_eeprom_reset_table()` initializes a clean table or asks SMU to erase it; `amdgpu_ras_eeprom_correct_header_tag()` flips between normal and bad signatures while preserving checksum.
- Append and read: `amdgpu_ras_eeprom_append()`, `amdgpu_ras_eeprom_append_table()`, `__amdgpu_ras_eeprom_write()`, `amdgpu_ras_eeprom_read()`, `amdgpu_ras_eeprom_read_idx()`, and `__amdgpu_ras_eeprom_read()` append/read circular table records or SMU-managed records.
- Initialization and validation: `amdgpu_ras_eeprom_init()`, `amdgpu_ras_smu_eeprom_init()`, `amdgpu_ras_eeprom_check()`, `amdgpu_ras_smu_eeprom_check()`, `amdgpu_ras_eeprom_check_err_threshold()`, and `amdgpu_ras_eeprom_check_and_recover()`.
- Debugfs support: `amdgpu_ras_debugfs_eeprom_size_ops`, `amdgpu_ras_debugfs_eeprom_table_ops`, `amdgpu_ras_debugfs_set_ret_size()`, and their read helpers expose table capacity and formatted table contents.
- SMU wrappers: `amdgpu_ras_smu_eeprom_supported()`, `amdgpu_ras_smu_get_table_version()`, `amdgpu_ras_smu_get_badpage_count()`, `amdgpu_ras_smu_get_badpage_mca_addr()`, `amdgpu_ras_smu_set_timestamp()`, `amdgpu_ras_smu_get_timestamp()`, `amdgpu_ras_smu_get_badpage_ipid()`, and `amdgpu_ras_smu_erase_ras_table()` forward to `struct ras_eeprom_smu_funcs`.
- RMA notification: `amdgpu_ras_check_bad_page_status()` sends out-of-band and in-band CPER/RMA notifications when bad-page counts exceed thresholds.

## Control Flow

Initialization enters through `amdgpu_ras_eeprom_init()`. If PMFW/SMU owns the RAS EEPROM feature, the function delegates to `amdgpu_ras_smu_eeprom_init()`, which reads table version and bad-page count from SMU, sets current timestamp, initializes capacity to 4000 records, and clears PA/MCA counters. Otherwise it verifies platform support, requires an initialized I2C adapter, finds the EEPROM address, initializes the mutex, reads the 20-byte header, creates a new table when the signature is unknown, resets old tables on specific HBM3E device variants, decodes version-specific record counts and offsets, validates max record count, and sets `ras_fri`.

Reset flow in `amdgpu_ras_eeprom_reset_table()` takes the table mutex and either writes a new local EEPROM table or asks SMU to erase its table. Local reset writes the signature `AMDR`, chooses V1/V2.1/V3 by UMC IP version, initializes V2.1+ RAS info (`GPU_HEALTH_USABLE`, 100 percent health, threshold), computes a combined header/RAS-info checksum, writes header and optional RAS info, resets counters and first-record index, sends zero bad-page and channel flags to SMU/DPM, clears saved-count state, and updates debugfs file size.

Append flow starts with `amdgpu_ras_eeprom_append()`. Unsupported EEPROM returns success. SMU-managed EEPROM uses `amdgpu_ras_smu_eeprom_append()` to update local bad-page count and threshold/RMA state; PMFW owns the actual persistence. Local EEPROM append validates `num`, stamps the NPS partition bits into `retired_page`, locks the table, calls `amdgpu_ras_eeprom_append_table()`, updates the header/checksum, refreshes debugfs size, unlocks, and clears the temporary NPS bits from the caller’s records.

`amdgpu_ras_eeprom_append_table()` serializes records into 24-byte EEPROM form, updates the bad-channel bitmap, computes circular-buffer write regions, writes one or two contiguous ranges as needed, advances `ras_fri` when overwriting old records, recomputes `ras_num_recs`, increments PA or MCA record counters depending on UMC generation, and mirrors `con->bad_page_num` into `ras_num_bad_pages`.

Header update flow checks whether bad pages exceed the configured threshold. If so, it emits warnings, optionally generates CPER threshold records, changes the table signature to `BADG` and RAS info to retired/0-percent health for custom thresholds, sets `ras->is_rma`, and sends an RMA reason to firmware. It then recomputes `tbl_size`, reads all records back, recomputes the checksum across records, header, and optional RAS info, writes the header, and writes RAS info for V2.1+.

Read flow in `amdgpu_ras_eeprom_read()` delegates to SMU record-by-index reads when SMU owns EEPROM. Local reads validate the requested count, compute whether the circular table wraps from `ras_fri` to zero, reads one or two ranges under the mutex, decodes each record, and updates bad-channel bitmap state.

Validation flow in `amdgpu_ras_eeprom_check()` either uses SMU threshold checks or local EEPROM checks. Local checks reread RAS info for V2.1+, verify the checksum, warn at 90 percent of threshold, and handle `BADG` signatures by either correcting the header back to `AMDR` when the threshold has increased enough or marking RMA for custom thresholds that remain exceeded. `amdgpu_ras_eeprom_check_and_recover()` can recover a corrupted checksum by resetting the table, re-saving in-memory bad pages through `amdgpu_ras_save_bad_pages()`, and verifying again.

Debugfs table read flow formats a virtual text file from the current header plus all records. It supports partial reads by using `*pos`, reads one EEPROM record at a time according to relative-to-absolute index mapping, decodes it, and prints error type, bank/CU, timestamp, offset/address, memory channel, MCUMC ID, and retired page.

SMU wrapper flow discovers the active `ras_smu_drv` through the live RAS context, checks `RAS_SMU_FEATURE_BIT__RAS_EEPROM`, and forwards only if the relevant function pointer exists. This keeps `amdgpu_ras.c` independent of platform-specific PMFW message implementations.

## State And Persistence Behavior

The local EEPROM table is a circular log. `ras_fri` points at the first readable record, `ras_num_recs` is the number of records currently represented, and `ras_max_record_count` is derived from table version. Appends can overwrite oldest records and advance `ras_fri`.

On-EEPROM record size is fixed at 24 bytes, while the in-memory `struct eeprom_table_record` is larger because some 48-bit fields are stored in `uint64_t`. Serialization masks `offset/address` and `retired_page` to 48 bits.

The header checksum is a byte sum over the header without the checksum field, optional RAS info, and all active record bytes, then negated so a full byte sum verifies to zero. V2.1/V3 tables include a 256-byte RAS info area; V1 tables have only header plus records.

`RAS_TABLE_HDR_VAL` (`AMDR`) means normal table. `RAS_TABLE_HDR_BAD` (`BADG`) means a custom threshold was exceeded and the GPU should be treated as retired/RMA until policy or threshold changes. V2.1+ RAS info stores `rma_status`, `health_percent`, and `ecc_page_threshold` persistently.

The implementation stores bad-channel bitmap state in the control object while reading or appending records, and asks SMU/DPM to update HBM bad channel flags after reset/load paths.

For UMC 12.x+ local EEPROM writes, `amdgpu_ras_eeprom_append()` temporarily encodes the current NPS partition mode in high bits of `retired_page`. `amdgpu_ras.c` later interprets those bits when converting old/new table records across memory partition modes.

For SMU-managed EEPROM, the local driver does not serialize table bytes. It treats PMFW as the persistence owner and retrieves MCA address, IPID-derived channel metadata, timestamps, table version, and count through SMU callbacks.

## Dependencies And Integration Points

- I2C EEPROM backend: `amdgpu_eeprom_read()` and `amdgpu_eeprom_write()` perform raw EEPROM access through `adev->pm.ras_eeprom_i2c_bus`.
- VBIOS/ATOM firmware: `amdgpu_atomfirmware_ras_rom_addr()` and `atom_context->vbios_pn` determine table address and platform quirks.
- Reset domain: local EEPROM reads/writes take `adev->reset_domain->sem` around I2C operations to avoid unstable access during GPU reset.
- `amdgpu_ras.c`: provides the containing `struct amdgpu_ras`, bad-page threshold, `bad_page_num`, `is_rma`, `update_channel_flag`, and recovery save path.
- SMU/DPM/PMFW: `ras_smu_drv`, `amdgpu_dpm_send_hbm_bad_pages_num()`, `amdgpu_dpm_send_hbm_bad_channel_flag()`, and `amdgpu_dpm_send_rma_reason()` integrate persistence with firmware state.
- UMC: SMU-managed record reads parse MCA IPID through `adev->umc.ras->mca_ipid_parse()`.
- CPER/RMA: threshold updates can call `amdgpu_cper_generate_bp_threshold_record()` and `amdgpu_ras_check_bad_page_status()` can emit in-band/out-of-band RMA records.
- Debugfs: exported file operations are installed by `amdgpu_ras.c` under the RAS debugfs directory.
- UniRAS: threshold checks and CPER generation branch around `amdgpu_uniras_enabled()` and `amdgpu_ras_mgr_check_eeprom_safety_watermark()`.

## Risks And Edge Cases

- Table address selection depends on platform-specific MP1 IP versions, VBIOS part-number substrings, and atom firmware behavior. Incorrect matching can read or overwrite the wrong EEPROM area.
- The local table is circular; append wrap arithmetic must be correct or records can be lost prematurely or `ras_fri` can point at stale data.
- Checksum verification reads the whole active table without taking the reset-domain semaphore in `__verify_ras_table_checksum()`, unlike many other I2C accessors in this file.
- `amdgpu_ras_eeprom_update_header()` allocates a buffer sized by `ras_num_recs`. Empty tables and very large counts depend on earlier validation and `kcalloc(0, ...)` behavior.
- Health percentage divides by `ras->bad_page_cnt_threshold` when threshold is nonzero, but policy values and derived thresholds still need care to avoid unexpected zero thresholds.
- SMU-managed append only updates local counts/RMA state; correctness depends on PMFW having already persisted or exposed the new record count through later `amdgpu_ras_eeprom_update_record_num()`.
- SMU record reads fill `retired_page` with `0x1ULL` as a placeholder because PA is unused, which requires later conversion code to treat MCA/IPID fields as authoritative.
- `amdgpu_ras_eeprom_correct_header_tag()` updates the checksum by delta rather than recalculating from EEPROM contents; it assumes the existing checksum and in-memory header are consistent.
- Debugfs table reads decode `record_err_type_str[record.err_type]` without a visible bounds check; corrupted EEPROM err_type values could index beyond the table.
- Unsupported EEPROM paths frequently return success (`0`) rather than `-EOPNOTSUPP`, which is intentional but can hide missing persistence if callers do not separately check support.

## Test Signals

- Initialize on all supported MP1/UMC combinations, APU/non-APU, HBM3E reset-quirk devices, and VBIOS part-number variants to validate support and I2C address selection.
- Create new tables for V1, V2.1, and V3; verify offsets, max record counts, header fields, RAS info fields, and checksum.
- Append records that fit, wrap once, and overwrite existing records; read them back and confirm order, `ras_fri`, `ras_num_recs`, PA/MCA counters, and debugfs output.
- Corrupt signatures, versions, checksums, record counts, and RAS info to validate reset, rejection, correction from `BADG` to `AMDR`, and recovery behavior.
- Test threshold modes `0`, `-1`, `-2`, and custom positive values; verify warnings, `BADG` signature, RMA state, health percent, CPER generation, and DPM RMA notifications.
- Exercise SMU-managed EEPROM success and `-EOPNOTSUPP` paths for each function pointer, including count update retry behavior and IPID parsing.
- Run EEPROM reads/writes while reset/recovery activity occurs to validate reset-domain semaphore behavior and error returns.
- Read debugfs EEPROM table with small buffer sizes and nonzero positions to validate partial-read formatting and file size updates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras_eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras_eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras_eeprom.h

## Purpose

`amdgpu_ras_eeprom.h` declares the persistent RAS EEPROM table format and API used by AMDGPU RAS code. It defines table versions, GPU health and EEPROM error enums, packed on-disk/on-EEPROM table structures, the live control structure that tracks table offsets/counts/validity, bad-page record layout, EEPROM lifecycle functions, SMU-managed EEPROM wrappers, and debugfs file operations.

The header bridges `amdgpu_ras.c` bad-page retirement logic with the implementation in `amdgpu_ras_eeprom.c` and with SMU/PMFW RAS EEPROM support.

## Important APIs, Types, And Constants

- Version constants: `RAS_TABLE_VER_V1`, `RAS_TABLE_VER_V2_1`, and `RAS_TABLE_VER_V3` select EEPROM table layout and feature behavior.
- `enum amdgpu_ras_gpu_health_status` defines persistent health states: usable and retired because ECC reached threshold.
- `enum amdgpu_ras_eeprom_err_type` defines per-record error classes: not applicable/ignore, recoverable, non-recoverable, and count sentinel.
- `struct amdgpu_ras_eeprom_table_header` is the packed persistent header: signature, version, first record offset, table size, and checksum.
- `struct amdgpu_ras_eeprom_table_ras_info` is the packed V2.1+ RAS info area: RMA status, health percentage, ECC page threshold, and reserved padding.
- `struct amdgpu_ras_eeprom_control` is the live driver control object. It stores decoded header and RAS info, EEPROM base address, header/info/record offsets, current and old record counts, bad-page count, MCA-vs-PA record counts, first record index, maximum capacity, table mutex, bad-channel bitmap, and validity flag.
- `struct eeprom_table_record` is the in-memory bad-page record. It contains MCA address or offset, retired GPU page, timestamp, error type, bank/CU, memory channel, and MCUMC ID. It is packed for serialization but still differs from the 24-byte EEPROM record because 48-bit persistent fields are held in `uint64_t`.
- Public lifecycle functions: `amdgpu_ras_eeprom_init()`, `amdgpu_ras_eeprom_reset_table()`, `amdgpu_ras_eeprom_check()`, and `amdgpu_ras_eeprom_check_and_recover()`.
- Public data functions: `amdgpu_ras_eeprom_read()`, `amdgpu_ras_eeprom_read_idx()`, `amdgpu_ras_eeprom_append()`, `amdgpu_ras_eeprom_update_record_num()`, and `amdgpu_ras_eeprom_max_record_count()`.
- Threshold/status functions: `amdgpu_ras_eeprom_check_err_threshold()` and `amdgpu_ras_check_bad_page_status()`.
- SMU wrapper declarations: `amdgpu_ras_smu_eeprom_supported()`, `amdgpu_ras_smu_get_table_version()`, `amdgpu_ras_smu_get_badpage_count()`, `amdgpu_ras_smu_get_badpage_mca_addr()`, `amdgpu_ras_smu_set_timestamp()`, `amdgpu_ras_smu_get_timestamp()`, `amdgpu_ras_smu_get_badpage_ipid()`, and `amdgpu_ras_smu_erase_ras_table()`.
- Debugfs declarations: `amdgpu_ras_debugfs_set_ret_size()`, `amdgpu_ras_debugfs_eeprom_size_ops`, and `amdgpu_ras_debugfs_eeprom_table_ops`.

## Control Flow Encoded By The Header

Callers initialize `struct amdgpu_ras_eeprom_control` through `amdgpu_ras_eeprom_init()`, which fills version, offsets, counts, capacity, and mutex state. Driver recovery code then reads records with `amdgpu_ras_eeprom_read()` or `amdgpu_ras_eeprom_read_idx()` and later appends new bad-page records with `amdgpu_ras_eeprom_append()`.

Validation and repair are explicit phases. `amdgpu_ras_eeprom_check()` verifies thresholds and table integrity after records are loaded. `amdgpu_ras_eeprom_check_and_recover()` can reset and rewrite the table from live bad-page state if checksum validation fails.

When PMFW owns the backing store, callers use the same high-level API, but implementation paths check `amdgpu_ras_smu_eeprom_supported()` and then call the declared SMU wrappers to get table version, count, record MCA address, IPID, timestamp, or erase the table.

Debugfs setup in `amdgpu_ras.c` uses the exported file operations and calls `amdgpu_ras_debugfs_set_ret_size()` whenever the table size changes so userspace sees a coherent formatted dump size.

## State And Persistence Behavior

The header separates persistent table fields from driver-only control fields. `tbl_hdr` and `tbl_rai` mirror data stored in EEPROM, while offsets, counts, `ras_fri`, `ras_max_record_count`, `bad_channel_bitmap`, mutex, and validity flag are driver bookkeeping.

`ras_num_recs` is the active table record count. `ras_num_recs_old` is used for SMU-managed count-update polling. `ras_num_bad_pages` can differ from record count because one record can represent a retire unit or multiple pages depending on ASIC/UMC generation.

`ras_num_mca_recs` and `ras_num_pa_recs` track mixed record formats during migration from older physical-address records to newer MCA-address records. `amdgpu_ras.c` uses these counts and table version to decide conversion behavior.

`ras_fri` is the first readable circular-buffer index. The table can wrap and overwrite older records, so record order is not always physical offset order.

`is_eeprom_valid` lets higher-level code avoid saving to a corrupt or unrecoverable local EEPROM table.

## Dependencies And Integration Points

- Includes `<linux/i2c.h>` because local EEPROM persistence uses an I2C EEPROM bus.
- Forward-declares `struct amdgpu_device`; implementation and callers pass device pointers for SMU, DPM, UMC, reset, and debugfs interactions.
- The header is included by `amdgpu_ras.h`, so `struct amdgpu_ras` embeds `struct amdgpu_ras_eeprom_control`.
- Debugfs file operations are exported so the main RAS file can create `ras_eeprom_size` and `ras_eeprom_table` nodes.
- SMU wrappers depend on `struct ras_smu_drv` and `struct ras_eeprom_smu_funcs` declared in `amdgpu_ras.h`, but this header declares the callable API to avoid exposing implementation details to all callers.

## Risks And Edge Cases

- `struct eeprom_table_record` is marked `__packed` but contains `uint64_t` fields and enums; consumers must not assume its in-memory size equals the 24-byte persistent EEPROM record size.
- The `address/offset` and `bank/cu` unions make field meaning context-dependent. Old PA records, new MCA records, and SMU-managed records must be interpreted with table version and platform support.
- `ras_num_bad_pages` can differ from `ras_num_recs`; code that treats them as identical can make wrong threshold or capacity decisions.
- `ras_fri` and `ras_record_offset` are both required to read the circular log correctly. Direct index arithmetic outside the EEPROM implementation is risky.
- Table version values are encoded as numeric constants; adding a new version requires updates in reset/init/read/check logic and in `amdgpu_ras.c` conversion paths.
- The validity flag is advisory and must be set/cleared consistently by initialization, load, check, and recovery code to avoid writes to a corrupt table.

## Test Signals

- ABI/layout-sensitive tests should verify packed header, RAS info, and record field offsets used by serialization.
- Unit or integration tests around table-count fields should distinguish record count, bad-page count, MCA record count, PA record count, and retire-unit expansion.
- SMU-managed and local-I2C implementations should both satisfy the same high-level read/append/reset/check expectations where applicable.
- Debugfs users should verify that table size updates follow append/reset and that unsupported contexts return clear "Not supported" output.
- Any new EEPROM table version or record field should be tested with old-version load, migration, reset, checksum, threshold, and recovery paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras_eeprom.h -->
