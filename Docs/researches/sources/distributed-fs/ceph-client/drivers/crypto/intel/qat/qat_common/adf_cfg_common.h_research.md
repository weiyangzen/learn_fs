# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_common.h

## Purpose
This header defines common configuration sizes, device-selection constants, service encoding shifts, config value types, QAT device type IDs, user-visible device status shape, and ioctl command numbers for `/dev/qat_adf_ctl`.

## Important APIs, Types, And Functions
Important definitions include `ADF_CFG_MAX_*`, `ADF_CFG_ALL_DEVICES`, `ADF_MAX_DEVICES`, `enum adf_cfg_service_type`, `enum adf_cfg_val_type`, `enum adf_device_type`, `struct adf_dev_status_info`, and ioctls `IOCTL_CONFIG_SYS_RESOURCE_PARAMETERS`, `IOCTL_STOP_ACCEL_DEV`, `IOCTL_START_ACCEL_DEV`, `IOCTL_STATUS_ACCEL_DEV`, and `IOCTL_GET_NUM_DEVICES`.

## Control Flow
There is no executable flow. The constants drive config parsing, ring-to-service map encoding, device-manager limits, and control-device ioctl dispatch.

## State And Persistence Behavior
No state exists in the header. `struct adf_dev_status_info` is a copied user/kernel data shape for transient status queries.

## Dependencies And Integration Points
It includes Linux types and ioctl helpers. It is shared by kernel config code and user-facing control structures, so it is part of a UAPI-adjacent contract despite living under driver sources.

## Risks
Changing struct layout or ioctl numbers can break user tools. `ADF_MAX_DEVICES` sizes internal bitmaps and device IDs. Service shift constants must match ring-to-service encoding used by hardware-data files.

## Test Signals
Compatibility tests for control ioctls, 32/64-bit compat ioctl, status output, device count, and service map decoding validate this header.
