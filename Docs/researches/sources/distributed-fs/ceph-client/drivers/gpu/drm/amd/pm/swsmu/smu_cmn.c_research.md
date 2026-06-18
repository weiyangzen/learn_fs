# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu_cmn.c

## Purpose

`smu_cmn.c` implements shared SWSMU helpers: SMU v1 mailbox transport, response decoding, common-to-ASIC mapping translation, feature enablement, table transfers, metrics caching, power-management policy descriptions, DPM level formatting, PCIe helper indexes, and firmware version querying. It is the central glue between AMDGPU power-management code and ASIC-specific `ppt_funcs`.

## Important APIs, Types, And Functions

The transport API is `smu_msg_v1_ops`, with `smu_msg_v1_send_msg`, `smu_msg_v1_wait_response`, `smu_msg_v1_decode_response`, and debug-mailbox send support. Public wrappers include `smu_cmn_send_smc_msg_with_param`, `smu_cmn_send_smc_msg`, debug variants, `smu_msg_wait_response`, and `smu_msg_send_async_locked`. Mapping and feature helpers include `smu_cmn_to_asic_specific_index`, `smu_cmn_feature_is_supported`, `smu_cmn_feature_is_enabled`, `smu_cmn_get_enabled_mask`, `smu_cmn_feature_update_enable_state`, `smu_cmn_set_pp_feature_mask`, and `smu_cmn_disable_all_features_with_exception`. Table helpers include `smu_cmn_update_table_read_arg`, `smu_cmn_write_watermarks_table`, `smu_cmn_write_pptable`, `smu_cmn_get_metrics_table`, and `smu_cmn_get_combo_pptable`.

## Control Flow, State, And Persistence

SMU message flow validates mappings and argument counts, filters VF-only commands, locks the mailbox, applies RAS priority filtering, checks firmware hang/init state, pre-polls for previous completion, writes args/message registers, optionally returns for async commands, post-polls, decodes the response, updates `smc_fw_state` on fatal protocol errors, and reads output registers. Table updates copy through the shared driver table buffer, flush or invalidate HDP as direction requires, then issue the firmware transfer message. Metrics reads cache table data for roughly one millisecond unless bypassed. Persistent state includes cached firmware versions, feature bits in firmware, SMU table buffers, metrics cache timestamp, custom pstate fields, and firmware hang/runtime state.

## Dependencies And Integration Points

The file depends on AMDGPU MMIO helpers, `amdgpu_smu.h`, `soc15_common.h`, RAS FED status, reset/halt handling, PCI probing, sysfs emit helpers, and ASIC-specific maps installed in `smu_context`. It is used by PPT implementations, sysfs power controls, metrics export, SMC table programming, display/audio power logic, and RAS-priority command paths.

## Risks And Test Signals

Risks include mailbox deadlock from incorrect lock-held usage, response timeout misclassification, command filtering hiding VF failures, feature-map mismatches, cache coherency bugs around table copies, and unsafe command attempts during RAS fatal error. Test signals include SMU message success/failure injection, async wait behavior, VF command filtering, RAS FED priority behavior, table round trips, metrics cache refresh, suspend/resume, firmware hang detection, and DPM/PCIe sysfs formatting.
