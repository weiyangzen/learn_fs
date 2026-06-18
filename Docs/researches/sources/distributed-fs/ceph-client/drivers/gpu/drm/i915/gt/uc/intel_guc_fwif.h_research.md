## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fwif.h

Purpose: defines the driver-side GuC firmware interface constants, helper mappings, packed shared-memory structures, ADS layout, logging buffer state, engine class ids, work queue formats, policy formats, and capture-list enumerations that connect i915 to GuC firmware ABI headers.

Important APIs, types, and functions:
- Includes GuC ABI headers for actions, SLPC actions, errors, MMIO communication, CTB communication, KLVs, and messages.
- Defines GuC engine classes, maximum classes/instances, context ids, client priorities, doorbell constants, work queue item/status/type bitfields, and stage descriptor attributes.
- Defines GuC control dword indices and bitfields for log params, workarounds, feature enablement, debug verbosity, ADS address, and device id.
- Provides `MAKE_GUC_ID()`, `GUC_ID_TO_ENGINE_CLASS()`, `GUC_ID_TO_ENGINE_INSTANCE()`, `engine_class_to_guc_class()`, and `guc_class_to_engine_class()`.
- Defines packed structs: `guc_wq_item`, `guc_process_desc_v69`, `guc_sched_wq_desc`, `guc_ctxt_registration_info`, `guc_lrc_desc_v69`, `guc_klv_generic_dw_t`, context/scheduling policy update packets, `guc_policies`, `guc_mmio_reg`, `guc_mmio_reg_set`, `guc_gt_system_info`, `guc_ads`, `guc_engine_usage_record`, `guc_engine_usage`, and `guc_log_buffer_state`.
- Defines capture list owner/type/class enums and GuC log buffer type enum.
- Provides `SLPC_EVENT()` for composing SLPC event id/argument-count fields and policy timeout helpers returning max milliseconds.

Control flow:
- This header does not execute control flow, but its structures are used throughout GuC initialization: ADS construction, context registration, scheduling policy updates, submission work queues, CT send/receive, logging/capture buffer handling, and SLPC requests.

State and persistence:
- Packed structures describe persistent shared-memory contracts between host and GuC firmware. `guc_ads` points GuC at policy, system info, register state, capture lists, and workaround KLVs. `guc_log_buffer_state` is shared mutable state for log/capture producer-consumer coordination.

Dependencies and integration points:
- Used by GuC CT, ADS, submission, log, capture, SLPC, and register/save-restore code. It maps i915 engine classes from `intel_engine_types.h` to firmware class ids.

Risks:
- ABI drift is the largest risk. Packed layout, bitfields, enum values, and unit conversions must exactly match firmware expectations.
- The static engine-class maps assume array sizes matching driver and GuC class ranges; `BUILD_BUG_ON` and `GEM_BUG_ON` catch some misuse.
- Shared log buffer state is firmware-owned in places and host-owned in others; incorrect read/write ownership can lose logs or stall firmware.

Test signals:
- Compile-time layout and array-size checks.
- Firmware integration tests for context registration, scheduling policy updates, ADS parsing, work queue submission, logging, capture, and SLPC event requests.
- ABI review whenever GuC firmware ABI headers are updated.
