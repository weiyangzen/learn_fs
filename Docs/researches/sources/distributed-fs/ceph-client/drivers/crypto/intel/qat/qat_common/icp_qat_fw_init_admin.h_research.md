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
