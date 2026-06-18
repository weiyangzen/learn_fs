# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras.c

## Purpose

`amdgpu_ras.c` is the central AMDGPU RAS implementation. It owns RAS feature discovery and enablement, per-IP RAS manager objects, sysfs/debugfs control surfaces, error query and injection dispatch, interrupt bottom halves, poison handling, GPU recovery scheduling, bad-page retirement, persistent bad-page restore/save through EEPROM, event IDs, and platform-specific paths for SR-IOV, UniRAS, ACA/MCA, XGMI hives, and x86 MCE.

## Important APIs, Types, And Functions

- Context/lifecycle: `amdgpu_ras_get_context()`, `amdgpu_ras_set_context()`, `amdgpu_ras_init()`, `amdgpu_ras_late_init()`, `amdgpu_ras_resume()`, `amdgpu_ras_suspend()`, `amdgpu_ras_pre_fini()`, and `amdgpu_ras_fini()`.
- Per-block management: `amdgpu_ras_register_ras_block()`, `amdgpu_ras_block_late_init()`, `amdgpu_ras_block_late_fini()`, `amdgpu_ras_find_obj()`, `amdgpu_ras_create_obj()`, and `put_obj()` manage `struct ras_manager` instances.
- Feature control: `amdgpu_ras_feature_enable()`, `amdgpu_ras_feature_enable_on_boot()`, `amdgpu_ras_enable_all_features()`, `amdgpu_ras_disable_all_features()`, and `amdgpu_ras_is_supported()` maintain `con->features` and firmware state.
- Query/reset/inject: `amdgpu_ras_query_error_status()`, `amdgpu_ras_query_error_status_with_event()`, `amdgpu_ras_query_error_status_helper()`, `amdgpu_ras_query_error_count()`, `amdgpu_ras_reset_error_status()`, and `amdgpu_ras_error_inject()`.
- Filesystem interfaces: `amdgpu_ras_fs_init()`, `amdgpu_ras_sysfs_create()`, `amdgpu_ras_debugfs_create_all()`, `amdgpu_ras_debugfs_ctrl_write()`, and `amdgpu_ras_debugfs_eeprom_write()`.
- Interrupt/recovery: `amdgpu_ras_interrupt_add_handler()`, `amdgpu_ras_interrupt_dispatch()`, `amdgpu_ras_interrupt_handler()`, `amdgpu_ras_global_ras_isr()`, `amdgpu_ras_interrupt_fatal_error_handler()`, `amdgpu_ras_reset_gpu()`, and `amdgpu_ras_do_recovery()`.
- Bad pages and poison: `amdgpu_ras_init_badpage_info()`, `amdgpu_ras_add_bad_pages()`, `amdgpu_ras_save_bad_pages()`, `amdgpu_ras_load_bad_pages()`, `amdgpu_ras_reserve_page()`, `amdgpu_ras_put_poison_req()`, `amdgpu_ras_page_retirement_thread()`, and `amdgpu_ras_do_page_retirement()`.
- Event/error helpers: `amdgpu_ras_mark_ras_event_caller()`, `amdgpu_ras_acquire_event_id()`, `amdgpu_ras_event_log_print()`, `amdgpu_ras_error_data_init()/fini()`, and CE/UE/DE statistic helpers.
- Register helpers: `amdgpu_ras_inst_get_memory_id_field()`, `amdgpu_ras_inst_get_err_cnt_field()`, `amdgpu_ras_inst_query_ras_error_count()`, and `amdgpu_ras_inst_reset_ras_error_count()`.

## Control Flow

`amdgpu_ras_init()` allocates `struct amdgpu_ras` plus manager slots, stores it in the PSP RAS context, calls `amdgpu_ras_check_supported()` to populate `ras_hw_enabled`, `ras_enabled`, poison support, and ACA state, initializes NBIO fatal interrupt support, creates common sysfs nodes, initializes ACA/MCA if supported, and prepares critical-region tracking.

`amdgpu_ras_late_init()` initializes per-device or XGMI hive event state, resets ACA/MCA during recovery, then iterates registered `amdgpu_ras_block_object` entries. The default per-block late init enables the feature, optionally harvests persistent EDC counters, installs interrupt handlers, creates sysfs count nodes, and seeds cached CE/UE counts.

Queries select one of several modes: SR-IOV host counts, direct IP callbacks, ACA/MCA firmware logging, or UniRAS command routing. `amdgpu_ras_query_error_status_with_event()` creates temporary `ras_err_data`, obtains a query mode, takes the reset-domain read semaphore, calls the helper, merges results into the manager totals, and emits event-tagged logs. Virtual host counts are treated as absolute and diffed against previous local totals.

Debugfs `ras_ctrl` parses enable, disable, inject, retire_page, and check_address commands. Injection validates support, blocks UMC injection into known bad pages, normalizes instance masks, and routes to UniRAS, IP-specific hooks, or PSP `psp_ras_trigger_error()`.

Interrupts are copied into a per-manager ring and processed by workqueue. In poison mode, UMC interrupts become poison creation requests and non-UMC interrupts become poison consumption handling. Without poison mode, UMC callbacks update CE/UE/DE counters. Fatal ERREVENT handling marks fatal state, requests mode1/full recovery, and acks/polls NBIO paths where required.

Recovery is scheduled through `amdgpu_ras_reset_gpu()`. `amdgpu_ras_do_recovery()` coordinates XGMI hive recovery, optionally harvests RAS counters, queries UniRAS or legacy RAS status, chooses reset method flags, invokes `amdgpu_device_gpu_recover()`, and clears recovery atomics.

Bad-page restore loads EEPROM records, converts old PA records or newer MCA/NPS records to physical pages through UMC callbacks, reserves VRAM pages unless they are critical regions, and updates DPM bad-page/channel notifications. Page-retirement work saves newly discovered records back to EEPROM and reschedules while deferred-page tags remain.

Fini disables RAS features before IP teardown, flushes page-retirement and recovery work, stops the page-retirement thread, removes sysfs/debugfs and interrupt handlers, tears down ACA/MCA, clears registered RAS block nodes, cancels count work, clears the PSP context, and frees the RAS context.

## State And Persistence Behavior

`struct amdgpu_ras` stores feature/schema masks, manager list and array, recovery locks/work, EEPROM control, bad-page threshold and count, poison support and FIFO, page-retirement counters, ECC radix tree, error bit state, event manager, reserved VRAM size, critical-region list, RMA state, UniRAS switch, and SMU RAS driver pointer.

`struct ras_manager` stores per-block identity, custom reference count, sysfs/debugfs names, interrupt ring, accumulated `ras_err_data`, and ACA handle. Error counts are long-lived totals; temporary query data is merged into these totals after each query.

Bad-page persistence spans `con->eh_data` and `con->eeprom_control`. `eh_data->bps` caches `eeprom_table_record` entries, `count_saved` marks the first unsaved record, and EEPROM counts/validity are maintained by `amdgpu_ras_eeprom.c`.

Event IDs can be per-device or shared by XGMI hive. Event state records a global sequence, per-type count, and last sequence number, and logs include IDs only when callers mark an event before acquiring it.

## Dependencies And Integration Points

The file integrates PSP RAS TA, per-IP RAS block objects, UMC conversion and retirement callbacks, EEPROM persistence, SMU/DPM notifications, ACA/MCA firmware logging, SR-IOV host telemetry, UniRAS command handling, NBIO fatal interrupt implementations, reset-domain scheduling, VRAM manager reservation, KFD poison notifications, x86 MCE notifiers, debugfs/sysfs, workqueues, kthreads, waitqueues, kfifo, radix tree, atomics, mutexes, and XGMI hive state.

## Risks And Edge Cases

- Manager lifetime uses a plain integer reference count; sysfs, debugfs, interrupt, and feature paths must stay balanced.
- The interrupt ring has no strong overflow protection if `wptr` laps `rptr`.
- Bad-page conversion is version-, UMC-, and NPS-dependent, especially across old PA records, MCA records, and table V3.
- Threshold policy differs for `amdgpu_bad_page_threshold` values `0`, `-1`, `-2`, and custom positive thresholds; custom thresholds can set RMA.
- Debugfs page retirement can intentionally corrupt EEPROM for testing if misused.
- UniRAS paths bypass or replace many legacy local behaviors, so new logic must check both paths.
- XGMI hive recovery shares state across devices and suppresses duplicate resets through atomics.
- Recovery/page-retirement/EEPROM paths rely on several locks and workqueue ordering; race coverage is important around reset-domain semaphores.

## Test Signals

- Boot supported/unsupported ASICs and verify `ras_hw_enabled`, `ras_enabled`, schema, poison support, ACA state, and NBIO RAS selection.
- Exercise block late init/fini with callbacks, hw_ops, sysfs nodes, and ACA handles; check manager references end cleanly.
- Read sysfs/debugfs RAS nodes and validate query-inaccessible, auto-clear, UMC DE, event-state, and bad-page output.
- Test debugfs enable/disable/inject/retire/check commands with valid and malformed input.
- Cover direct, firmware/MCA/ACA, SR-IOV virtual, and UniRAS query modes.
- Trigger poison creation/consumption and fatal interrupts; validate event IDs, reset modes, FIFO/PASID handling, and page-retirement scheduling.
- Seed EEPROM with V1/V2.1/V3, PA/MCA, wrapped, corrupted, threshold-exceeded, and SMU-managed tables; verify load/convert/reserve/save behavior.
- Run reset/recovery race tests with concurrent sysfs reads, delayed retirement, EEPROM access, and interrupt dispatch.
