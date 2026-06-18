# sources/distributed-fs/ceph-client/include/uapi/linux/pfrut.h

Purpose: Defines ioctl ABI and payload layouts for Platform Firmware Runtime Update and telemetry log access.

Important APIs/types/functions: Exports `PFRUT_IOCTL_MAGIC`, update ioctls `PFRU_IOC_SET_REV`, `PFRU_IOC_STAGE`, `PFRU_IOC_ACTIVATE`, `PFRU_IOC_STAGE_ACTIVATE`, `PFRU_IOC_QUERY_CAP`, telemetry ioctls `PFRT_LOG_IOC_SET_INFO`, `PFRT_LOG_IOC_GET_INFO`, `PFRT_LOG_IOC_GET_DATA_INFO`, `struct pfru_payload_hdr`, `enum pfru_dsm_status`, `struct pfru_update_cap_info`, `struct pfru_com_buf_info`, `struct pfru_updated_result`, `struct pfrt_log_data_info`, and `struct pfrt_log_info`.

Control flow: Userspace sets the revision, queries capability, stages a firmware capsule from a communication buffer, activates the staged image, or performs stage+activate. Telemetry userspace sets/gets log selector information and queries physical buffer chunks and rollover/reset counters.

State and persistence behavior: PFRUT operations can mutate platform firmware runtime state and may have durable firmware effects. Capability, communication-buffer, result, and telemetry structs snapshot firmware/ACPI DSM status, versions, GUIDs, physical buffer addresses, sizes, timing, and log metadata.

Dependencies and integration points: Depends on `<linux/ioctl.h>` and `<linux/types.h>`. Integrates with ACPI/DSM firmware interfaces, platform firmware update tools, capsule image formats, and telemetry log readers.

Risks: Firmware update ioctls are high-impact. User input must validate revision IDs, capsule headers, communication buffer boundaries, anti-rollback versions, and firmware status. Physical addresses in telemetry/buffer info must not be exposed to untrusted callers without policy checks.

Test signals: Query capability on supported firmware, stage invalid and valid capsules, activate staged images in controlled environments, verify DSM status mapping, read telemetry log info/data info, test invalid revision/log selectors, and ensure update failures return documented errno paths.
