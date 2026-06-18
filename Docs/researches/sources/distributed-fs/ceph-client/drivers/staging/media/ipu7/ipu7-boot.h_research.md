# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-boot.h

## Purpose

This header declares the IPU7 firmware boot API used by subsystem drivers.

## Important APIs, Types, and Functions

It declares `FW_QUEUE_CONFIG_SIZE()`, `ipu7_boot_init_boot_config()`, `ipu7_boot_release_boot_config()`, `ipu7_boot_start_fw()`, `ipu7_boot_stop_fw()`, and `ipu7_boot_get_boot_state()`.

## Control Flow

No implementation flow. Callers initialize queue/subsystem config, call start to boot firmware, use syscom queues, stop firmware, then release boot config.

## State and Persistence Behavior

The API operates on `struct ipu7_bus_device` boot and syscom fields and DMA-visible queue/config allocations.

## Dependencies and Integration Points

It forward-declares `ipu7_bus_device` and `syscom_queue_config` and includes Linux types. ISYS firmware glue uses these calls directly.

## Risks and Edge Cases

Call order matters: release before stop or start before init leaves `ipu7_bus_device` fields invalid. Queue count and config array sizing must match `FW_QUEUE_CONFIG_SIZE()`.

## Test Signals

Compile namespace users and run firmware init/open/close/release sequencing tests, including failure unwinds.
