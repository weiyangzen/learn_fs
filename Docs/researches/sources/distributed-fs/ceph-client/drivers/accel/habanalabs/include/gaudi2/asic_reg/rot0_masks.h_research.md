# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_masks.h

## Purpose
`rot0_masks.h` defines bit positions and masks for Gaudi2 rotator instance 0 global control/status registers. It is the field companion to `rot0_regs.h`.

## Important APIs, Types, And Functions
The macros cover KMD-mode enable, completion queue enable/address/data/AWUSER/AXI attributes, completion message threshold and AXI attributes, writeback AXI attributes, stop-on-error, error status bits for rotator and QMAN HBW/LBW faults, WBC/RSB/MRSB maximum outstanding and rate-limit fields, empty/AXI-idle status, monitoring counters/timestamps/context IDs, MSS halt/status, SEI/SPI status and masks, pad-calculation disable, QMAN force-stop, clock-enable disable bits, and MSS halted status.

## Control Flow
There is no executable flow. Callers use these fields while enabling the rotator, configuring completion behavior, tuning read/write buffering, masking or reading interrupts, stopping on errors, forcing QMAN stop, and polling empty/idle/halt state.

## State, Persistence, And Dependencies
The header stores no state. Writes using these masks alter persistent rotator hardware state until reprogrammed or reset. It depends on `rot0_regs.h` addresses and on callers using read/modify/write for fields that share a register.

## Integration Points
These fields connect descriptor submission, rotator completion queues, MSS halt handling, SEI/SPI interrupt processing, error recovery, clock gating, and performance monitoring. Driver-level composed masks may wrap these generated fields for common idle or halt checks.

## Risks
Some fields are status-only while others are write controls; using a status mask as a write value can be harmful. Shared AXI fields require preserving unrelated cache/protection bits. Interrupt mask polarity must be confirmed before enabling or suppressing SEI/SPI signals. Force-stop and halt bits can leave in-flight descriptors incomplete.

## Test Signals
Signals include successful KMD-mode enable, completion queue operation, correct interrupt mask/status behavior, stop-on-error triggering, idle/empty polling matching actual work completion, rate limiter configuration readback, and clean recovery from forced halt.
