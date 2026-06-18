## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_config.h

Purpose: Exposes the Gen2 device configuration entry point.

Important APIs/types: Includes `adf_accel_devices.h` and declares `int adf_gen2_dev_config(struct adf_accel_dev *accel_dev);`.

Control flow/state: The header owns no state. Its function initializes config sections and marks the device configured in the implementation.

Dependencies/integration: Used by Gen2 device-specific drivers to install default config before instance creation.

Risks and test signals: Build coverage should ensure Gen2 callers link against the exported implementation and that non-Gen2 code does not depend on Gen2-specific ring constants through this header.
