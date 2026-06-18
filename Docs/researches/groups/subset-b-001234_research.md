# subset-b-001234 Research

Grouped research for Intel QAT common driver files. Each section preserves the source path and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_ras.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_ras.h

Purpose: defines the Gen6 QAT reliability, availability, and serviceability register map used by the Gen6 RAS implementation. It is a hardware contract header: error-source registers, mask registers, parity status/control registers, CPP/RI/TI fault registers, ATU fault status, rate-limiting error bits, and generic status fields.

Important API: `adf_gen6_init_ras_ops(struct adf_ras_ops *ras_ops)` is the only function declaration. The rest of the file is symbolic register offsets and bit masks such as `ADF_GEN6_ERRSOU{0..3}`, `ADF_GEN6_ERRMSK{0..3}`, `ADF_GEN6_RIMEM_PARERR_FATAL_MASK`, `ADF_GEN6_CPP_CFC_FATAL_ERR_BIT`, and `ADF_GEN6_GENSTS_*`.

Control flow and state: no executable control flow or persistent state lives here. Runtime code includes this header to enable, mask, clear, classify, and report hardware error conditions. State is in device registers and `accel_dev->ras_errors` maintained elsewhere.

Dependencies and integration: depends on Linux `BIT()`/`GENMASK()` helpers. Integrates with Gen6 hardware data, ISR RAS dispatch, and sysfs RAS counters.

Risks and test signals: off-by-one or wrong-bit masks can misclassify fatal/nonfatal errors, suppress interrupts, or force unnecessary resets. Test via RAS interrupt injection, register readback after enable/disable, sysfs counter increments, and reset-required behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_ras.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_shared.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_shared.c

Purpose: provides a thin Gen6 compatibility layer that reuses Gen4 implementations for common QAT mechanisms. It avoids duplicating CSR, PF/VF, VF migration, and device configuration logic when Gen6 register layout or behavior matches Gen4.

Important APIs: `adf_gen6_init_pf_pfvf_ops()` delegates to `adf_gen4_init_pf_pfvf_ops`; `adf_gen6_init_hw_csr_ops()` delegates to Gen4 CSR operations; `adf_gen6_comp_dev_config()` and `adf_gen6_no_dev_config()` call shared Gen4 configuration helpers; `adf_gen6_init_vf_mig_ops()` delegates to Gen4 VF migration operations. All are exported GPL symbols.

Control flow and state: no local state. Each function directly initializes an ops table or returns another helper's result. The state changed is owned by caller-provided ops structures or `accel_dev` configuration.

Dependencies and integration: depends on Gen4 config, CSR, PF/VF, and migration headers plus the Gen6 public header. Device-specific Gen6 drivers use these symbols during hardware data initialization.

Risks and test signals: risk is semantic drift if Gen6 hardware diverges from Gen4. Test by probing Gen6 PF/VF messaging, CSR ring control, compression/no-device config, and migration paths under the device-specific driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_shared.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_shared.h

Purpose: declares the Gen6 shared helper entry points used by Gen6 device drivers to initialize common operations by reusing Gen4 implementations.

Important API: forward-declares `struct adf_hw_csr_ops`, `struct qat_migdev_ops`, `struct adf_accel_dev`, and `struct adf_pfvf_ops`; declares `adf_gen6_init_pf_pfvf_ops`, `adf_gen6_init_hw_csr_ops`, `adf_gen6_comp_dev_config`, `adf_gen6_no_dev_config`, and `adf_gen6_init_vf_mig_ops`.

Control flow and state: header-only declarations; no state or behavior. It sets the compile-time interface boundary between Gen6 hardware files and common/Gen4 helpers.

Dependencies and integration: included by Gen6 hardware-data sources and implemented by `adf_gen6_shared.c`. It indirectly connects Gen6 devices to PF/VF communication, CSR operations, compression configuration, and VF live migration.

Risks and test signals: declaration/implementation mismatch would fail build or link. Functional risk follows from callers assuming Gen4-compatible behavior. Test via build coverage for Gen6 configs and runtime smoke tests for PF/VF, CSR, config, and migration init hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_tl.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_tl.c

Purpose: supplies Gen6 telemetry counter metadata consumed by the common telemetry debugfs code. It maps named counters to offsets inside the Gen6 firmware-populated telemetry DMA layout.

Important APIs: `adf_gen6_init_tl_data(struct adf_tl_hw_data *tl_data)` fills layout sizes, history depth, max monitored ring-pairs, conversion factors, counter arrays, and command-queue multipliers. Static counter tables cover device counters, slice utilization/execution counters, command queue wait/execute/drain counters, and ring-pair counters.

Control flow and state: mostly static data initialization. Runtime state is not stored here; `adf_tl_init/run` copies these descriptors into the hardware data path and uses them to interpret DMA snapshots.

Dependencies and integration: depends on `adf_gen6_tl.h` register layout structs, generic `adf_telemetry.h`, `adf_tl_debugfs.h` macros, and firmware admin slice-count structs. Integrated by Gen6 hardware-data setup before telemetry is initialized.

Risks and test signals: wrong offsets or queue multipliers produce misleading debugfs telemetry without obvious failures. Test by enabling telemetry, checking `device_data` and `rp_*_data` fields against firmware/hardware expectations, and verifying slice/cmdq counts do not exceed Gen6 maxima.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_tl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_tl.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_tl.h

Purpose: defines the Gen6 telemetry DMA layout, maximum telemetry resource counts, hardware unit conversion constants, and the public initializer for Gen6 telemetry metadata.

Important types and macros: `adf_gen6_tl_slice_data_regs`, `adf_gen6_tl_cmdq_data_regs`, `adf_gen6_tl_device_data_regs`, `adf_gen6_tl_ring_pair_data_regs`, and `adf_gen6_tl_layout` mirror firmware-written memory. Macros define layout sizes, message-count offset, max slices/cmdqs, max ring-pairs, history buffer count, and conversion constants.

Control flow and state: no executable state. The layout structs define how common telemetry reads coherent DMA memory and how debugfs offsets are calculated.

Dependencies and integration: depends on Linux types and, under `CONFIG_DEBUG_FS`, declares `adf_gen6_init_tl_data`. Shared offset macros in `adf_tl_debugfs.h` reference these struct names.

Risks and test signals: structure packing/alignment and field order must match firmware exactly. Tests should validate `sizeof`-driven layout against firmware ABI, successful telemetry admin start, monotonic `reg_tl_msg_cnt`, and plausible values for device, slice, cmdq, and ring-pair counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen6_tl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat.c

Purpose: implements QAT heartbeat health monitoring. It allocates DMA memory for firmware heartbeat counters, configures firmware heartbeat timer ticks, compares live and previous counters, tracks failures, and triggers fatal-error notification when firmware appears unresponsive.

Important APIs: `adf_heartbeat_init`, `adf_heartbeat_start`, `adf_heartbeat_shutdown`, `adf_heartbeat_status`, `adf_heartbeat_check_ctrs`, `adf_heartbeat_ms_to_ticks`, and `adf_heartbeat_save_cfg_param`. Key helpers include `check_ae`, `adf_hb_get_status`, `get_timer_ticks`, and `adf_heartbeat_reset`.

Control flow and state: init allocates `struct adf_heartbeat` plus one page of coherent DMA. Start validates platform-specific counter count, computes timer ticks from config/defaults, and sends admin timer setup. Status reads are rate-limited by `hb_timer`, increment sent/failed counters, compare each active AE/thread, and throttle fatal reset notification to `ADF_CFG_HB_RESET_MS`.

Dependencies and integration: uses admin commands, config keys, device clock callbacks, AE masks, optional `adf_timer`, and `adf_notify_fatal_error`. Debugfs reads invoke status checks.

Risks and test signals: DMA layout assumes enough page space for live/last/failure arrays; too-frequent polling returns unsupported; counter-count adaptation mutates `hw_device->num_hb_ctrs`. Test normal alive reads, stalled-counter threshold, minimum timer validation, restart handling, and fatal-error reset notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat.h

Purpose: defines heartbeat constants, status enum, DMA counter pair structure, driver heartbeat state, and public heartbeat APIs with debugfs/config build fallbacks.

Important types and APIs: `enum adf_device_heartbeat_status` reports unresponsive, alive, or unsupported. `struct hb_cnt_pair` stores response/request counters. `struct adf_heartbeat` stores counters, configured timer, last check/reset timestamps, DMA addresses, and debugfs dentries. Function declarations cover init/start/shutdown, timer conversion/config persistence, status checks, counter initialization, and optional error injection.

Control flow and state: state is per-`adf_accel_dev` through `accel_dev->heartbeat`. When `CONFIG_DEBUG_FS` is off, heartbeat init/start/save/check become no-ops, so callers can remain unconditional.

Dependencies and integration: used by lifecycle code in `adf_init.c`, heartbeat debugfs, error injection, and platform hooks that prefill/check counter memory.

Risks and test signals: build-configuration fallbacks can hide heartbeat coverage in non-debugfs builds. Test compile with and without `CONFIG_DEBUG_FS` and `CONFIG_CRYPTO_DEV_QAT_ERROR_INJECTION`, verify dentry lifecycle, and ensure `struct adf_heartbeat` fields are initialized before debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_dbgfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_dbgfs.c

Purpose: exposes heartbeat status, statistics, runtime timer configuration, and optional error injection through debugfs under each QAT device.

Important APIs: `adf_heartbeat_dbgfs_add` creates `heartbeat/status`, `queries_sent`, `queries_failed`, `config`, and optionally `inject_error`. `adf_heartbeat_dbgfs_rm` removes those dentries. File operations implement reads for counters/status/config, writes for config, and writes for injection.

Control flow and state: reading `status` invokes `adf_heartbeat_status`, so it can update counters and trigger reset notification on failures. Writing `config` validates integer input, enforces minimum timer, pins timer to 200 ms when `accel_dev->timer` exists, persists config, converts to ticks, and sends an admin timer command. Error injection accepts only a single `1\n` style write.

Dependencies and integration: depends on debugfs, admin heartbeat timer command, config storage, and `adf_heartbeat_inject_error`.

Risks and test signals: status reads have side effects; config writes race with active polling only through heartbeat fields without a local lock. Test valid/invalid config writes, min timer enforcement, debugfs removal during device stop, and injected failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_dbgfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_dbgfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_dbgfs.h

Purpose: declares the heartbeat debugfs add/remove interface.

Important API: `adf_heartbeat_dbgfs_add(struct adf_accel_dev *accel_dev)` and `adf_heartbeat_dbgfs_rm(struct adf_accel_dev *accel_dev)`.

Control flow and state: no behavior or state in the header. It establishes the integration contract between generic debugfs setup and heartbeat diagnostics.

Dependencies and integration: forward-declares `struct adf_accel_dev`; implemented by `adf_heartbeat_dbgfs.c`. Called from broader QAT debugfs lifecycle when a device starts/stops.

Risks and test signals: build or link catches signature drift. Runtime test should confirm heartbeat debugfs directory appears only when heartbeat state exists and is removed without stale dentries during shutdown/restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_dbgfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_inject.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_inject.c

Purpose: implements heartbeat failure injection for debug/test builds. It deliberately makes a selected AE/thread look stalled to exercise heartbeat error detection and reset paths.

Important APIs: `adf_heartbeat_inject_error(struct adf_accel_dev *accel_dev)` is called from debugfs. Helpers set the firmware heartbeat timer to maximum, optionally stop the platform timer, disable arbitration for one AE/thread via `adf_disable_arb_thd`, and mutate heartbeat DMA counters to satisfy the failure predicate.

Control flow and state: chooses a random active AE and random heartbeat thread, prevents firmware from updating counters, disables scheduling for the chosen thread, then changes live and last counter values so future status checks see `req != resp` and unchanged response. It writes directly into heartbeat DMA memory and changes `heartbeat->hb_timer`.

Dependencies and integration: depends on admin heartbeat timer command, hardware arbitration control, random bytes, and heartbeat counter layout.

Risks and test signals: intended destructive behavior can make a device require reset; should only be reachable under error-injection config. Test debugfs injection returns errors on unsupported admin/arbiter paths and triggers heartbeat failure on the next valid poll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_hw_arbiter.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_hw_arbiter.c

Purpose: configures the QAT hardware service arbiter, maps AE worker threads to arbiters, updates per-bank ring arbitration enable bits, and supports disabling one thread for heartbeat error injection.

Important APIs: `adf_init_arb`, `adf_update_ring_arb`, `adf_exit_arb`, and `adf_disable_arb_thd`. CSR write macros compute service arbiter and worker-thread mapping register addresses.

Control flow and state: init reads `arb_info` and platform thread-to-arbiter mapping, writes four service-arbiter config registers, and maps active AEs. Ring updates compute enabled TX/RX pair intersections and write per-bank arbitration enable masks. Exit clears all thread mappings and ring enables. Error injection clears one thread nibble in the AE mapping.

Dependencies and integration: depends on `adf_hw_device_data` callbacks, transport bank CSR base, CSR ops, and ring mask conventions. Called during device init/exit and ring lifecycle.

Risks and test signals: wrong mapping can starve rings or route services incorrectly. Test transport with each service mix, ring pair enable/disable, SR-IOV modes, and heartbeat injection thread disable on strand/admin-thread aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_hw_arbiter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_init.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_init.c

Purpose: orchestrates QAT device service registration and the device up/down/restart lifecycle. It orders hardware setup, firmware load/start, interrupts, RAS, PF/VF communication, heartbeat, rate limiting, telemetry, registered services, crypto/compression algorithm registration, debugfs, and sysfs.

Important APIs: `adf_service_register`, `adf_service_unregister`, `adf_dev_up`, `adf_dev_down`, `adf_dev_restart`, `adf_dev_restarting_notify`, `adf_dev_restarted_notify`, and `adf_error_notifier`. Static phases are `adf_dev_init`, `adf_dev_start`, `adf_dev_stop`, and `adf_dev_shutdown`.

Control flow and state: `state_lock` serializes up/down. Init validates configuration, initializes ETR/admin/arbiter/AE/firmware/MSI-X/RAS/PFVF, then heartbeat/RL/TL and service `INIT`. Start sets starting/started bits, starts AE/admin/clock/PM/timer/heartbeat/RL/TL/services, registers algorithms, and adds debugfs/sysfs. Stop reverses user-facing and runtime services. Shutdown releases firmware, services, RL/RAS/heartbeat/TL/IRQs/config/admin/ETR and flushes misc work.

Dependencies and integration: central integration point for nearly every common QAT subsystem.

Risks and test signals: partial failure paths return without fully unwinding some earlier init work, relying on later down paths. Test repeated up/down/restart, failure injection at each hw callback, service unregister while active, VF auto-config, and algorithm registration rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_isr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_isr.c

Purpose: allocates MSI-X vectors, registers QAT interrupt handlers, manages bank response tasklets, handles AE-cluster interrupts for VF2PF, PM, and RAS events, and owns the shared misc workqueue used by several subsystems.

Important APIs: `adf_isr_resource_alloc`, `adf_isr_resource_free`, `adf_enable_vf2pf_interrupts`, `adf_disable_all_vf2pf_interrupts`, `adf_init_misc_wq`, `adf_exit_misc_wq`, `adf_misc_wq_queue_work`, `adf_misc_wq_queue_delayed_work`, and `adf_misc_wq_flush`.

Control flow and state: allocation builds IRQ metadata, enables MSI-X, initializes bank tasklets, and requests bank plus AE-cluster vectors. Bank ISR clears interrupt flags and schedules the response handler. AE ISR checks VF2PF interrupts first in SR-IOV mode, then PM, then RAS. VF2PF handling disables pending VF interrupts, applies rate limiting, and queues PF work.

Dependencies and integration: uses PCI IRQ APIs, transport CSR ops, PF/VF ops, RAS ops, PM hooks, SR-IOV VF info, and workqueues used by telemetry/timers/PF responses.

Risks and test signals: IRQ count differs with SR-IOV; affinity hints and tasklets need cleanup on failures. Test MSI-X allocation failure unwinds, VF interrupt flood rate limiting, RAS fatal notification, PM interrupt dispatch, and workqueue lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_isr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_mstate_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_mstate_mgr.c

Purpose: provides a compact manager for building, validating, and walking QAT migration-state buffers. It writes a preamble and nested typed sections into caller-provided memory and can initialize from remote state for restore.

Important APIs: `adf_mstate_mgr_new/destroy/init`, `adf_mstate_preamble_add/update`, `adf_mstate_sect_add`, `adf_mstate_sect_add_vreg`, `adf_mstate_sect_update`, `adf_mstate_mgr_init_from_remote`, `adf_mstate_state_size`, `adf_mstate_state_size_from_remote`, and `adf_mstate_sect_lookup`.

Control flow and state: `adf_mstate_mgr` tracks `buf`, current `state` cursor, total size, and section count. Add paths reserve headers, let populate callbacks fill nested content, validate available room, then update header sizes/subsection counts and cursor. Remote init validates magic/version/header length and scans sections for bounds safety. Lookup walks section headers and optionally invokes an action callback with a sub-manager.

Dependencies and integration: used by VF live migration code to serialize ETR, BAR, config, PF/VF, and SLA state sections named by header constants.

Risks and test signals: section add failures after header reservation can leave cursor advanced; callers must treat NULL as failed state build. Test malformed remote sizes, nested section bounds, preamble version compatibility, and round-trip save/restore section lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_mstate_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_mstate_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_mstate_mgr.h

Purpose: defines migration-state section identifiers, manager/preamble structures, callback types, and the public state-buffer manager API.

Important types and API: constants such as `ADF_MSTATE_ETRB_IDS`, `ADF_MSTATE_CONFIG_IDS`, `ADF_MSTATE_SLA_IDS`, `ADF_MSTATE_VM2PF_IDS`, and `ADF_MSTATE_PF2VM_IDS` form the state schema. `struct adf_mstate_mgr`, `struct adf_mstate_preh`, and `struct adf_mstate_vreginfo` define the generic buffer cursor, preamble, and virtual-register copy source. Callback typedefs support custom preamble validation, population, and restore actions.

Control flow and state: header only. State is caller-owned buffer memory plus the manager cursor.

Dependencies and integration: consumed by `adf_mstate_mgr.c` and migration/device-specific code that serializes QAT VF state.

Risks and test signals: section IDs are fixed-width eight-byte fields, so naming collisions/truncation would break lookup. Test all producer/consumer section IDs, buffer size accounting, and compatibility with older remote preamble versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_mstate_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_msg.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_msg.h

Purpose: defines the PF/VF register-message protocol ABI used by QAT SR-IOV PF and VF drivers. It documents Gen2 and Gen4 register layouts, common interrupt/origin bits, typed messages, compatibility versions, ring reset responses, block-message formats, and block payload structs.

Important types and macros: `struct pfvf_message` is the abstract message. Enums cover PF2VF and VF2PF message types, compatibility versions, compatibility results, ring-reset results, block response types/errors, block request categories, capabilities versions, and ring-to-service map versions. Payload structs include `capabilities_v1/v2/v3` and `ring_to_svc_map_v1`.

Control flow and state: no runtime behavior. The header defines bitfield masks and bounds used by PF/VF protocol implementations to encode/decode CSR messages and byte-wise block transfers.

Dependencies and integration: included by PF and VF message/protocol files, generation-specific PFVF ops, SR-IOV, and VF hardware initialization.

Risks and test signals: ABI changes affect PF/VF compatibility. Test old/new PF-VF pairings, block-message truncation, CRC validation, Gen2/Gen4 type width limits, and ring-reset field validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_msg.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_msg.c

Purpose: implements PF-originated notifications to VFs and PF-side block-message providers for VF queries.

Important APIs: `adf_pf2vf_notify_restarting`, `adf_pf2vf_wait_for_restarting_complete`, `adf_pf2vf_notify_restarted`, `adf_pf2vf_notify_fatal_error`, `adf_pf_capabilities_msg_provider`, and `adf_pf_ring_to_svc_msg_provider`.

Control flow and state: restarting notification marks initialized, compatible VFs as `restarting` and sends a message. The wait loop polls up to 100 times with 100 ms sleeps for VFs to send restart-complete. Restarted and fatal-error notifications are sent to initialized compatible VFs. Providers serialize PF hardware extended DC capabilities, capabilities mask, and ring-to-service map into block-message buffers with versioned headers.

Dependencies and integration: uses PCI VF count, PFVF send helper, VF info state, and hardware data. Called by SR-IOV disable/restart/error paths and PF block-message request handling.

Risks and test signals: wait loop can delay shutdown up to about 10 seconds; provider version content must match VF parser expectations. Test VF restart handshake, timeout warning, fatal-error broadcast, and VF retrieval of capabilities/ring map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_msg.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_msg.h

Purpose: declares PF-side PF/VF notification and block-message provider interfaces with no-op fallbacks when PCI IOV is disabled.

Important API: declares restart/fatal notification helpers, `adf_pf2vf_blkmsg_provider` callback type, `adf_pf_capabilities_msg_provider`, and `adf_pf_ring_to_svc_msg_provider`.

Control flow and state: when `CONFIG_PCI_IOV` is absent, notification functions compile to empty inline stubs so common lifecycle code can call them without ifdefs. Provider declarations remain available for protocol code.

Dependencies and integration: includes `adf_accel_devices.h` for device types. Implemented by `adf_pfvf_pf_msg.c` and used by SR-IOV and PF protocol request handling.

Risks and test signals: stubs mean PF/VF tests must cover both IOV-enabled and disabled builds. Check compile coverage for both configs and runtime delivery of restarting/restarted/fatal notifications in SR-IOV mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_proto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_proto.c

Purpose: implements PF-side receive, dispatch, response, compatibility negotiation, block-message serving, and ring-pair reset handling for VF-to-PF messages.

Important APIs: `adf_send_pf2vf_msg`, `adf_recv_and_handle_vf2pf_msg`, and `adf_enable_pf2vf_comms`. Key helpers include `handle_blkmsg_req`, `handle_rp_reset_req`, and `adf_handle_vf2pf_msg`.

Control flow and state: received messages are decoded through generation-specific PFVF ops. Version requests store `vf_info->vf_compat_ver` and return compatibility. Init/shutdown/restart-complete toggle `vf_info->init/restarting`. Block requests map small/medium/large request encoding to registered providers and can return data bytes or CRC. Ring reset validates reserved bits and VF-local bank index, converts it to PF bank number, and calls `ring_pair_reset`.

Dependencies and integration: uses `accel_dev->pf.vf_info`, PF/VF locks, CRC utilities, capability/ring-map providers, hardware reset callback, and SR-IOV workqueue scheduling.

Risks and test signals: malformed block offsets or provider sizes return protocol error data; unknown message returns false so interrupt may remain disabled. Test compatibility matrix, block CRC/truncation paths, ring reset success/invalid/timeout, and interrupt re-enable after handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_proto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_proto.h

Purpose: declares PF-side low-level PF/VF protocol entry points.

Important API: `adf_send_pf2vf_msg(struct adf_accel_dev *, u8 vf_nr, struct pfvf_message)` sends a PF message to a specific VF. `adf_enable_pf2vf_comms(struct adf_accel_dev *)` initializes PF-side protocol support.

Control flow and state: header only. Runtime state lives in PF/VF ops and `accel_dev->pf` fields initialized by the implementation.

Dependencies and integration: includes Linux types and `adf_accel_devices.h`. Used by PF notification code, SR-IOV, and generation-specific operations.

Risks and test signals: build catches type drift. Runtime tests should verify PF comms init initializes CRC and interrupt lock before SR-IOV enables VF interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_utils.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_utils.c

Purpose: provides shared PF/VF protocol utilities for CRC8 block-message validation and conversion between abstract `pfvf_message` values and generation-specific CSR bit layouts.

Important APIs: `adf_pfvf_crc_init`, `adf_pfvf_calc_blkmsg_crc`, `adf_pfvf_csr_msg_of`, and `adf_pfvf_message_of`. `set_value_on_csr_msg` validates a value against a field mask before shifting it into a CSR word.

Control flow and state: CRC init populates a global CRC8 table using polynomial `0x97`. CSR encoding returns zero if message type/data exceed the format masks; decoding extracts type/data and logs a no-type message as invalid. No per-device state is stored here.

Dependencies and integration: depends on Linux CRC8 and `struct pfvf_csr_format` descriptors from generation-specific PFVF code. Used by both PF and VF protocol paths and block-message CRC checks.

Risks and test signals: encoded zero is also an invalid/no-message sentinel, so callers must treat failures carefully. Test boundary field values, out-of-range data logging, CRC agreement between PF and VF, and Gen2/Gen4 CSR format compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_utils.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_utils.h

Purpose: declares PF/VF utility helpers, CSR field-format descriptors, timing constants for acknowledgement waits, and compatibility checking logic.

Important types and API: `struct pfvf_field_format` and `struct pfvf_csr_format` describe type/data bit positions and masks. Declares CRC and CSR conversion helpers. `adf_vf_compat_checker` returns incompatible for zero, compatible for versions up to current, and unknown for newer VFs.

Control flow and state: inline compatibility policy is the only behavior. There is no persistent state in the header.

Dependencies and integration: includes `adf_pfvf_msg.h` for protocol versions/results. Shared by PF and VF protocol implementations and generation-specific CSR ops.

Risks and test signals: compatibility policy permits newer VFs as "unknown" rather than hard fail at PF side, while VF-side handling decides final acceptance. Test mixed-version PF/VF behavior and ack timing under slow or contended register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_msg.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_msg.c

Purpose: implements VF-side high-level messages and queries to the PF: init/shutdown/restart-complete notifications, compatibility negotiation, extended capabilities retrieval, and ring-to-service mapping retrieval.

Important APIs: `adf_vf2pf_notify_init`, `adf_vf2pf_notify_shutdown`, `adf_vf2pf_notify_restart_complete`, `adf_vf2pf_request_version`, `adf_vf2pf_get_capabilities`, and `adf_vf2pf_get_ring_to_svc`.

Control flow and state: init sends `INIT` and sets `ADF_STATUS_PF_RUNNING`. Shutdown sends only if PF is marked running. Version request sends current compatibility and stores PF version after accepting compatible/unknown responses. Capabilities query uses block message v1-v3 parsing to update extended DC capabilities, capabilities mask, and clock frequency when provided. Ring map query updates `hw_device->ring_to_svc_map`.

Dependencies and integration: depends on VF protocol request helpers, bitfield masks, PF compatibility version, and hardware data fields consumed later by VF config and service mapping.

Risks and test signals: truncated block messages are partially accepted only where version length permits; missing capabilities leave defaults. Test old PF, newer PF, incompatible PF, truncated v1/v2/v3 payloads, and ring-to-service map fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_msg.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_msg.h

Purpose: declares VF-side PF/VF high-level message helpers with no-op fallbacks for non-IOV builds.

Important API: declares VF init/shutdown/restart-complete notifications plus version, capabilities, and ring-to-service query functions. In non-`CONFIG_PCI_IOV` builds, init returns success and shutdown is empty.

Control flow and state: header-only configuration gating. Runtime state is `accel_dev->vf` and hardware data updated by the implementation.

Dependencies and integration: consumed by VF device setup and VF protocol enablement. Complements `adf_pfvf_vf_proto.h`, which provides lower-level request transport.

Risks and test signals: no-op fallbacks can mask missing SR-IOV coverage in tests. Build both PCI_IOV modes and verify VF probe obtains PF capabilities before services depend on them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_proto.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_proto.c

Purpose: implements VF-side low-level PF/VF transport, synchronous request/response handling, block-message reconstruction with CRC, PF message dispatch, and VF communication enablement.

Important APIs: `adf_send_vf2pf_msg`, `adf_send_vf2pf_req`, `adf_send_vf2pf_blkmsg_req`, `adf_recv_and_handle_pf2vf_msg`, and `adf_enable_vf2pf_comms`.

Control flow and state: synchronous requests reinitialize `vf.msg_received`, send a message, then wait with bounded retries for a PF response completed by interrupt handling. Block-message retrieval asks for version, length, payload bytes, and CRC byte-by-byte, truncating to local buffer length and verifying CRC. PF messages either trigger restart handling, complete responses, or log fatal/unknown messages. Enabling comms initializes CRC, enables PF2VF interrupts, then requests version, capabilities, and ring map.

Dependencies and integration: uses completions, PFVF ops, compatibility fields, VF response storage, and high-level VF query helpers.

Risks and test signals: response timeout returns `-EIO`; concurrent requests share `vf.response` and completion, so transport should be serialized by call paths. Test PF response loss/retry, CRC mismatch, truncated payloads, restart notifications, fatal messages, and enablement sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_proto.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_proto.h

Purpose: declares VF-side low-level PF/VF protocol transport functions.

Important API: `adf_send_vf2pf_msg` sends an asynchronous VF message. `adf_send_vf2pf_req` sends a request and returns the PF response. `adf_send_vf2pf_blkmsg_req` reconstructs a block message into a caller buffer. `adf_enable_vf2pf_comms` initializes VF communication.

Control flow and state: no header state. Implementation uses `accel_dev->vf` lock/completion/response state and generation-specific PFVF ops.

Dependencies and integration: included by VF message code and VF setup paths. It is the lower layer beneath VF capabilities and ring-map queries.

Risks and test signals: signatures expose buffer length as in/out for block messages; callers must pass adequate space and inspect final length. Test request/response sequencing and error propagation into VF probe/config code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs.c

Purpose: exposes a power-management status debugfs file for devices whose PM implementation provides a status printer.

Important APIs: `adf_pm_dbgfs_add` creates `pm_status`; `adf_pm_dbgfs_rm` removes it. `pm_status_read` delegates to `accel_dev->power_management.print_pm_status` when present.

Control flow and state: add checks `pm->present` and `pm->print_pm_status` before creating the file. Read copies `accel_dev->power_management` locally and calls the driver-provided printer. Remove clears the stored dentry pointer.

Dependencies and integration: depends on debugfs and `struct adf_pm` fields in `adf_accel_dev`. Device-specific PM code supplies the actual status formatting.

Risks and test signals: returns `count` if no printer is set, but add normally prevents that file. Test PM-present and PM-absent devices, debugfs removal during device stop, and that printer callbacks honor user buffer/count/pos semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs.h

Purpose: declares PM debugfs lifecycle helpers.

Important API: `adf_pm_dbgfs_add(struct adf_accel_dev *)` and `adf_pm_dbgfs_rm(struct adf_accel_dev *)`.

Control flow and state: header only. The implementation stores dentry state in `accel_dev->power_management`.

Dependencies and integration: used by the broader QAT debugfs lifecycle and device PM implementations.

Risks and test signals: build catches signature drift. Runtime test should confirm PM debugfs appears only when the device reports PM support and is removed cleanly on shutdown/restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs_utils.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs_utils.c

Purpose: provides shared formatting helpers for PM debugfs status tables backed by firmware PM info register arrays.

Important APIs: `adf_pm_scnprint_table_upper_keys` and `adf_pm_scnprint_table_lower_keys`. Both call `pm_scnprint_table`, which formats table rows as `KEY: value` after extracting masked bitfields from register words.

Control flow and state: no persistent state. For each `pm_status_row`, it uppercases or lowercases the row key, extracts `field_mask` from `pm_info_regs[reg_offset]` with `field_get`, and appends to a caller buffer using `scnprintf`.

Dependencies and integration: uses Linux bitfield and string case helpers; depends on table entries created with macros from `adf_pm_dbgfs_utils.h`. Consumed by device-specific PM status printers.

Risks and test signals: `wr` accumulation assumes `buff_size - wr` remains valid; callers must size buffers sufficiently. Test mixed masks, upper/lower formatting, table lengths, and boundary buffer sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs_utils.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs_utils.h

Purpose: defines PM status table row descriptors and convenience macros for mapping fields in `icp_qat_fw_init_admin_pm_info` to printable debugfs rows.

Important types and macros: `PM_INFO_MEMBER_OFF` converts a struct member to a `u32` register-array offset. `PM_INFO_REGSET_ENTRY_MASK` and `PM_INFO_REGSET_ENTRY32` build `struct pm_status_row` entries. `struct pm_status_row` stores register offset, field mask, and key.

Control flow and state: header only. Generated tables are static data owned by PM-specific code.

Dependencies and integration: includes firmware admin PM info definition and Linux type/stddef helpers. Formatting functions are implemented in `adf_pm_dbgfs_utils.c`.

Risks and test signals: offset calculation assumes PM info is interpreted as a `u32` array and fields are aligned accordingly. Test generated row offsets against firmware struct layout and verify 32-bit/full-mask and subfield extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pm_dbgfs_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl.c

Purpose: implements QAT rate-limiting SLA management. It maintains an in-memory hierarchy of root, cluster, and leaf nodes, validates user SLA requests, maps ring pairs to leaves, writes hierarchy mappings to hardware CSRs, sends admin firmware add/update/delete/init messages, and exposes lifecycle hooks used by device startup.

Important APIs: `adf_rl_init`, `adf_rl_start`, `adf_rl_stop`, `adf_rl_exit`, `adf_rl_add_sla`, `adf_rl_update_sla`, `adf_rl_get_sla`, `adf_rl_remove_sla`, `adf_rl_remove_sla_all`, `adf_rl_get_capability_remaining`, `adf_rl_get_sla_arr_of_type`, and token calculators for PCIe bandwidth, AE cycles, and slice tokens.

Control flow and state: `struct adf_rl` owns SLA pointer arrays, root/cluster/leaf arrays, RP usage flags, user-input state, and `rl_lock`. Start validates firmware capability, initializes token bucket registers, sends RL init, creates default root/cluster nodes for enabled services, and adds sysfs. Add/update validates input, finds parent, checks budget, writes node mappings, sends admin message, then updates budget and arrays. Removal clears mappings, sends delete, frees nodes.

Dependencies and integration: uses hardware RL offsets/scales, service mapping, PMISC CSRs, admin firmware, and `adf_sysfs_rl`.

Risks and test signals: budget arithmetic and cleanup ordering are critical; failures after CSR writes but before array insertion can leave hardware state. Test add/update/remove under each service, parent budget constraints, RP reuse rejection, default-node initialization, FW capability absence, and repeated start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl.h

Purpose: defines the rate-limiting data model, user input format, hardware data, driver state, SLA node structure, constants, and public API.

Important types: `enum rl_node_type` defines root/cluster/leaf hierarchy. `struct adf_rl_sla_input_data` represents sysfs/user operations. `struct rl_slice_cnt` stores firmware slice counts. `struct adf_rl_interface_data` protects sysfs staging state. `struct adf_rl_hw_data` holds device-specific offsets/scales/throughput/slice data. `struct adf_rl` stores all live state. `struct rl_sla` represents one hierarchy node.

Control flow and state: state is per device through `accel_dev->rate_limiting`. The model caps roots, clusters, leaves, ring-pairs per leaf, and total SLA IDs with fixed arrays.

Dependencies and integration: includes service enums from `adf_cfg_services.h`; implemented by `adf_rl.c`, admin bridge, and sysfs frontend.

Risks and test signals: fixed limits must match hardware and sysfs expectations. Test maximum node counts, RP masks beyond device banks, service enablement, and public API behavior for default parent and empty IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl_admin.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl_admin.c

Purpose: bridges rate-limiting SLA state to firmware admin commands. It prepares DMA-backed SLA configuration parameters and sends firmware init/add/update/delete messages.

Important APIs: `adf_rl_send_admin_init_msg`, `adf_rl_send_admin_add_update_msg`, and `adf_rl_send_admin_delete_msg`. Helpers fill `icp_qat_fw_init_admin_req` and `icp_qat_fw_init_admin_sla_config_params`.

Control flow and state: init sends an RL init command and stores returned slice counts, mapping UCS count to symmetric crypto slice tokens. Add/update allocates coherent DMA for firmware params, calculates PCIe in/out, slice utilization, and AE utilization token values from SLA CIR/PIR, copies RP IDs, sends the admin command, then frees DMA. Delete forwards node ID and node type.

Dependencies and integration: depends on admin firmware functions, RL calculator functions, DMA mapping, and `struct rl_sla`.

Risks and test signals: DMA allocation failure aborts add/update; token calculations must match firmware units. Test firmware init failure, add/update DMA failure, params content for each service, and delete after node removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl_admin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl_admin.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl_admin.h

Purpose: declares the rate-limiting admin firmware bridge.

Important API: `adf_rl_send_admin_init_msg`, `adf_rl_send_admin_add_update_msg`, and `adf_rl_send_admin_delete_msg`.

Control flow and state: no header behavior. Admin bridge state is transient DMA request memory in the implementation.

Dependencies and integration: includes `adf_rl.h` for `struct rl_slice_cnt` and `struct rl_sla`. Used by `adf_rl.c`.

Risks and test signals: signature changes affect RL core build. Functional tests should verify RL core handles each admin function's failure return without corrupting SLA state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_rl_admin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sriov.c

Purpose: manages QAT PF SR-IOV enable/disable, VF info initialization, VF2PF work scheduling, and the PF response workqueue.

Important APIs: `adf_schedule_vf2pf_handler`, `adf_reenable_sriov`, `adf_disable_sriov`, `adf_sriov_configure`, `adf_init_pf_wq`, and `adf_exit_pf_wq`. Static helpers enable/disable SR-IOV and add SR-IOV configuration.

Control flow and state: enabling warns without IOMMU, brings down a running idle PF, adds kernel config forcing CY/DC counts to zero, allocates `pf.vf_info`, brings device up without reconfig, initializes VF locks/ratelimits, configures IOV threads, enables VF2PF interrupts, and enables all hardware VFs. Disabling checks busy/reset state, optionally brings device down, notifies VFs restarting, waits for completion, disables PCI SR-IOV and interrupts, clears IOV threads, destroys locks, and frees VF info unless restarting.

Dependencies and integration: uses PCI SR-IOV APIs, QAT lifecycle, config, PF/VF messaging, ISR VF interrupts, and workqueues.

Risks and test signals: `numvfs` is ignored and all hardware VFs are enabled; error paths must clean config and VF info. Test enable/disable while busy, IOMMU warning, VF interrupt flood handling, restart reenable, and full-VF hardware resource mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs.c

Purpose: creates the main `qat` sysfs attribute group for device state control, service configuration, PM idle support, auto-reset, ring-pair service lookup, and ring-pair count.

Important API: `adf_sysfs_init`. Attributes include `state`, `cfg_services`, `pm_idle_enabled`, `auto_reset`, `rp2srv`, and `num_rps`.

Control flow and state: `state_store` starts/stops the device after checking reset/busy state. `cfg_services_store` parses service strings, requires device down, updates config, and refreshes capabilities. `pm_idle_enabled_store` requires device down and stores config. `auto_reset_store` directly toggles `accel_dev->autoreset_on_error`. `rp2srv_store/show` stores a selected ring number under `accel_dev->sysfs.lock` and returns its service mapping. Init adds the group and sets ring number to unset.

Dependencies and integration: depends on QAT device manager, config parser/storage, service mapping macros, and lifecycle APIs.

Risks and test signals: sysfs state changes can trigger full device lifecycle; service changes while up are rejected. Test invalid service strings, down/up transitions, busy device rejection, ring bounds, unset `rp2srv`, and config persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_anti_rb.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_anti_rb.c

Purpose: exposes anti-rollback secure-version-number state and commit action through a `qat_svn` sysfs group when supported by the device.

Important APIs: `adf_sysfs_start_arb` and `adf_sysfs_stop_arb`. Attributes are read-only `enforced_min`, `active`, `permanent_min`, and write-only `commit`.

Control flow and state: show handlers resolve `accel_dev` and call `adf_anti_rb_query` with the requested SVN selector. `commit_store` accepts only a true boolean and calls `adf_anti_rb_commit`. Start checks hardware `anti_rb_enabled` callback, adds the group, and marks `sysfs_added`. Stop removes the group, clears `sysfs_added`, and resets `svncheck_retry`.

Dependencies and integration: depends on anti-rollback hardware data and helpers. Lifecycle code starts/stops it after device start/stop.

Risks and test signals: commit is irreversible at hardware/security level; sysfs must only appear when supported. Test unsupported devices, query failures, invalid commit input, successful commit path, and group removal on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_anti_rb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_anti_rb.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_anti_rb.h

Purpose: declares sysfs lifecycle hooks for the anti-rollback `qat_svn` group.

Important API: `adf_sysfs_start_arb(struct adf_accel_dev *)` and `adf_sysfs_stop_arb(struct adf_accel_dev *)`.

Control flow and state: header only. Implementation stores sysfs-added and retry state in anti-rollback hardware data.

Dependencies and integration: called from device start/stop in `adf_init.c`.

Risks and test signals: build coverage catches declaration drift. Runtime tests should verify the sysfs group is gated by hardware anti-rollback support and removed on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_anti_rb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_ras_counters.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_ras_counters.c

Purpose: exposes RAS error counters through a `qat_ras` sysfs group.

Important APIs: `adf_sysfs_start_ras` and `adf_sysfs_stop_ras`. Attributes are `errors_correctable`, `errors_nonfatal`, `errors_fatal`, and write-only `reset_error_counters`.

Control flow and state: show handlers resolve `accel_dev` and read atomic counters from `accel_dev->ras_errors`. Reset accepts only `1\n` and clears all counters. Start is gated by `ras_errors.enabled`, clears counters, adds the sysfs group, and marks `sysfs_added`. Stop removes the group if present and clears counters again.

Dependencies and integration: RAS interrupt handling increments counters through macros in the header. Lifecycle starts/stops sysfs after device start/stop.

Risks and test signals: start sets `sysfs_added` even if `device_add_group` fails; stop will attempt removal if marked. Test group creation failure handling, reset input validation, atomic counter increments under interrupts, and counter reset across restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_ras_counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_ras_counters.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_ras_counters.h

Purpose: declares RAS sysfs lifecycle hooks and defines atomic counter helper macros for RAS error accounting.

Important API/macros: `adf_sysfs_start_ras`, `adf_sysfs_stop_ras`, `ADF_RAS_ERR_CTR_READ`, `ADF_RAS_ERR_CTR_CLEAR`, and `ADF_RAS_ERR_CTR_INC`.

Control flow and state: macros operate on `ras_errors.counter[ERR]` atomics. Clear iterates over `ADF_RAS_ERRORS` and sets each counter to zero.

Dependencies and integration: relies on `ADF_RAS_ERRORS` and counter enum values from broader QAT device definitions. Used by RAS interrupt handlers and sysfs implementation.

Risks and test signals: macros evaluate `ras_errors` repeatedly, so callers should pass a stable lvalue. Test atomic increments from interrupt context, sysfs reads after increments, and clear behavior for all enum slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_ras_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_rl.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_rl.c

Purpose: implements the `qat_rl` sysfs frontend for rate-limiting SLA operations. It stages input fields and executes add/update/remove/get/capability operations against the RL core.

Important APIs: `adf_sysfs_rl_add` and `adf_sysfs_rl_rm`. Attributes include `rp`, `id`, `cir`, `pir`, `srv`, `cap_rem`, and write-only `sla_op`.

Control flow and state: each parameter attribute reads/writes `rate_limiting->user_input` under an rwsem. `srv` and `cap_rem` parse service names and validate enabled service for SLA service. `sla_op_store` matches operation strings, then under write lock calls RL core functions. Add defaults parent to `RL_PARENT_DEFAULT_ID`, type to `RL_LEAF`, and updates `input.sla_id` with the new ID. Add initializes staged service fields to `SVC_BASE_COUNT`.

Dependencies and integration: depends on `adf_rl` APIs and device sysfs group management. Added by `adf_rl_start`, removed by `adf_rl_stop`.

Risks and test signals: staged input persists across operations; users must set fields in the right order. Test each operation, invalid service names, disabled services, concurrent sysfs writes, capability remaining defaults, and removal of all non-default SLAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_rl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_rl.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_rl.h

Purpose: declares rate-limiting sysfs group add/remove functions.

Important API: `adf_sysfs_rl_add(struct adf_accel_dev *)` and `adf_sysfs_rl_rm(struct adf_accel_dev *)`.

Control flow and state: no header behavior. Implementation stores sysfs-added state inside `adf_rl_interface_data`.

Dependencies and integration: called by `adf_rl_start` and `adf_rl_stop`.

Risks and test signals: build catches signature drift. Runtime test should verify `qat_rl` appears only when RL firmware capability and initialization succeed, and is removed during stop before RL state is freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_sysfs_rl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_telemetry.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_telemetry.c

Purpose: implements common telemetry lifecycle and data collection. It allocates firmware DMA telemetry memory, starts/stops telemetry admin commands, snapshots changing counters into history buffers, and provides state used by debugfs readers.

Important APIs: `adf_tl_init`, `adf_tl_start`, `adf_tl_run`, `adf_tl_halt`, `adf_tl_stop`, and `adf_tl_shutdown`. Helpers validate hardware data, allocate/free memory, snapshot registers, and compute command-queue counts from slice counts and hardware multipliers.

Control flow and state: init validates `adf_tl_hw_data`, allocates `struct adf_telemetry`, RP index array, history buffers, and coherent DMA layout. Run sends admin TL start with DMA address and RP indexes, validates returned slice counts, computes cmdq counts, sets `state` and history depth, then queues delayed work. Work handler checks message count, snapshots DMA data under lock when changed, handles race by resnapshotting if count changes mid-copy, advances ring buffer, and requeues. Halt cancels work, clears state, and sends admin stop.

Dependencies and integration: uses admin telemetry commands, misc workqueue, Gen-specific `adf_tl_hw_data`, and debugfs control/data files.

Risks and test signals: cancellation inside worker and external halt must avoid deadlock; state controls history sample count. Test unsupported FW capability, invalid slice counts, TL start/stop/restart, RP selection, history aggregation, and shutdown after active telemetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_telemetry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_telemetry.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_telemetry.h

Purpose: defines generic QAT telemetry hardware metadata, runtime telemetry state, constants, and lifecycle APIs.

Important types: `struct adf_tl_hw_data` describes layout sizes, counter arrays, conversion factors, counts, maximums, and command-queue multipliers. `struct adf_telemetry` stores device pointer, state, selected history depth, current history index, message count, DMA memory, history buffers, selected RP indexes, locks, delayed work, slice counts, and cmdq counts.

Control flow and state: state is per device at `accel_dev->telemetry`. `atomic_t state` doubles as enabled flag and requested aggregation window. `regs_hist_lock` protects history snapshots/readers; `wr_lock` serializes debugfs control writes.

Dependencies and integration: includes firmware admin slice-count struct and debugfs counter declarations. Functions become no-ops without `CONFIG_DEBUG_FS`.

Risks and test signals: no-op fallback means telemetry exists only in debugfs builds. Test build configurations, state transitions, lock ordering with debugfs, and proper freeing of DMA/history buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_telemetry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_timer.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_timer.c

Purpose: provides a periodic 200 ms QAT firmware time synchronization worker used to trigger firmware heartbeat, rate-limiting, and telemetry timer events on platforms that use this internal sync timer.

Important APIs: `adf_timer_start` and `adf_timer_stop`. Static `work_handler` requeues itself and sends `adf_send_admin_tim_sync`.

Control flow and state: start allocates `struct adf_timer`, stores it in `accel_dev->timer`, records initial real time, initializes delayed work, and queues the first run. Each run requeues for 200 ms, computes elapsed periods from current real time divided by 200 ms, and sends that period count to firmware. Stop cancels delayed work, frees the context, and clears `accel_dev->timer`.

Dependencies and integration: uses misc workqueue, admin timer sync command, ktime, and device lifecycle `hw_data->start_timer/stop_timer`. Heartbeat forces 200 ms timer when this context exists.

Risks and test signals: failure to send sync logs but continues; real-time jumps can affect period count. Test start/stop cycles, shutdown while work pending, admin failure logging, and interaction with heartbeat timer minimum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_timer.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_timer.h

Purpose: defines the timer synchronization context and lifecycle functions.

Important types and API: `struct adf_timer` stores `accel_dev`, delayed work, and initial timestamp. Declares `adf_timer_start` and `adf_timer_stop`.

Control flow and state: header only. Runtime state is owned per device at `accel_dev->timer`.

Dependencies and integration: includes ktime and workqueue types. Used by platform hardware hooks and heartbeat logic.

Risks and test signals: callers must only stop timers that were successfully started. Test exported symbol availability, repeated start/stop, and null-safe stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_tl_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_tl_debugfs.c

Purpose: implements debugfs control and formatted reporting for telemetry snapshots. It lets users start/stop telemetry, choose ring-pairs to monitor, and read aggregated device or ring-pair counters.

Important APIs: `adf_tl_dbgfs_add` and `adf_tl_dbgfs_rm`. Files include `telemetry/device_data`, `control`, and `rp_A_data` through the Gen-specific max RP slots. Helpers collect u32/u64 history values, calculate count/min/max/average, convert cycles to ns, convert bandwidth units to Mbps, and print device/slice/cmdq/RP rows.

Control flow and state: `control` write validates requested history depth, stops active telemetry if needed, and calls `adf_tl_run` or `adf_tl_halt` under `wr_lock`. RP file writes change selected RP index, restarting telemetry if active so firmware uses new indexes. Reads require active telemetry, collect recent history under `regs_hist_lock`, and print current plus min/max/avg when state > 1.

Dependencies and integration: depends on `adf_telemetry`, Gen-specific counter descriptors, service mapping, debugfs aux numbers, and misc workqueue-driven snapshots.

Risks and test signals: aggregation depends on `msg_cnt` and history index correctness; RP changes restart firmware telemetry. Test invalid control/RP inputs, zero samples, multi-sample aggregation, concurrent reads/writes, and removal while active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_tl_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_tl_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_tl_debugfs.h

Purpose: defines telemetry debugfs counter names, offset-building macros, counter descriptor types, aggregation value type, and debugfs lifecycle declarations.

Important types/macros: counter name constants define user-visible report keys. `ADF_TL_*_REG_OFF` macros compute offsets into generation-specific telemetry layout structs. `enum adf_tl_counter_type` selects simple, ns, average-latency, or Mbps formatting. `struct adf_tl_dbg_counter` describes one counter's name/type/offsets. `ADF_TL_COUNTER` and `ADF_TL_COUNTER_LATENCY` build descriptors. `struct adf_tl_dbg_aggr_values` stores current/min/max/avg.

Control flow and state: header only. Descriptor arrays are Gen-specific static data, and runtime values come from `adf_telemetry`.

Dependencies and integration: used by Gen6 telemetry metadata and `adf_tl_debugfs.c`.

Risks and test signals: offset macros depend on exact naming of generation layout structs and members. Test compile coverage for each generation, stable debugfs key names, and formatting behavior for every counter type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_tl_debugfs.h -->
