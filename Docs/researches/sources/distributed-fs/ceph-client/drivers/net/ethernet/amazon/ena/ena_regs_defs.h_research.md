# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_regs_defs.h

## Purpose
`ena_regs_defs.h` defines ENA MMIO register offsets, register bit fields, and reset reason codes. It is the low-level register ABI used by ENA common code and the netdev driver when resetting or configuring the device.

## Important APIs, Types, And Functions
`enum ena_regs_reset_reason_types` enumerates reset causes including normal reset, keep-alive timeout, admin timeout, missed TX completion, invalid RX/TX request ID, too many RX descriptors, initialization error, watchdog timeout, shutdown, user trigger, missed interrupt, suspected poll starvation, and malformed RX descriptor. Macros define offsets for version, controller version, capabilities, admin queue bases/caps/doorbells, completion queue, AENQ, interrupt mask, device control/status, MMIO read request/response, RSS indirection update, and PHC doorbell. Additional masks/shifts describe version fields, capabilities, queue depths/entry sizes, device control reset reason, device status bits, MMIO read fields, RSS update fields, and PHC request ID.

## Control Flow, State, And Integration
There is no direct control flow. The reset reason enum is stored in `ena_adapter.reset_reason` and passed to `ena_com_dev_reset()`. Register offsets and masks are consumed by lower ENA common MMIO/admin code to initialize admin queues, request MMIO reads, configure RSS entries, and interact with PHC. The reset reason values are also diagnostic state visible to hardware/firmware.

## Dependencies
The file is coupled to ENA hardware/firmware register ABI and to common ENA code. It does not include Linux headers directly, so including code must provide bit macro context where needed.

## Risks And Test Signals
Risks are ABI mismatch, wrong reset reason reporting, and incorrect register mask use causing failed initialization or reset loops. Test signals include probe/reset success, MMIO readless mode, admin queue initialization, RSS indirection updates, PHC timestamp requests, and reset reason validation in device/driver logs.
