# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/abi/ipu7_fw_syscom_abi.h

## Purpose

This header defines the firmware ABI for syscom queue configuration and queue indices.

## Important APIs, Types, and Functions

`struct syscom_queue_params_config` describes a queue token array address, token size, and maximum capacity. `struct syscom_config_s` carries output and input queue counts. Inline helpers `syscom_config_get_queue_configs()` and `_const()` locate the variable-length queue config array immediately after `syscom_config_s`. `struct syscom_queue_indices_s` holds firmware read/write indices.

## Control Flow

No direct runtime flow. Boot code embeds queue parameters after the boot config syscom context and firmware publishes queue index memory location after boot.

## State and Persistence Behavior

Queue config and indices are shared state between host and firmware. Host-owned queue token memory persists until boot config release.

## Dependencies and Integration Points

It includes common ABI address type and is consumed by boot setup and syscom token helpers.

## Risks and Edge Cases

The variable-length layout relies on `&config[1]`; allocation sizes must include all queue configs. Queue capacity must be at least firmware-supported minimum when queues are active.

## Test Signals

Boot queue initialization, syscom token enqueue/dequeue, queue full/empty handling, and queue index address publication after firmware READY.
