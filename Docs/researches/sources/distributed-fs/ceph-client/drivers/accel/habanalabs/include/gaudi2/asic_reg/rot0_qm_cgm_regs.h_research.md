# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_qm_cgm_regs.h

## Purpose
`rot0_qm_cgm_regs.h` defines the small clock-gating-manager register block for rotator 0's queue manager.

## Important APIs, Types, And Functions
It exports three address macros: `mmROT0_QM_CGM_CFG`, `mmROT0_QM_CGM_STS`, and `mmROT0_QM_CGM_CFG1`. There are no C functions or types.

## Control Flow
The header contains no logic. Driver code writes configuration registers to enable or tune QMAN clock gating and reads status to confirm the block is gated, ungated, or idle as expected.

## State, Persistence, And Dependencies
Clock-gating policy and status live in hardware. Configuration persists until reset or subsequent writes. The block depends on the rotator QMAN being idle-safe before aggressive gating is enabled.

## Integration Points
This register block integrates with power management, reset paths, idle checks, and queue-manager bring-up/teardown. It complements the wider QMAN and rotator status registers.

## Risks
Enabling clock gating while queues or ARC communication are active can cause timeouts or lost progress. Misreading status may make reset code assume the block is idle when transactions are still in flight.

## Test Signals
Useful tests verify queue submission before and after clock-gating transitions, idle status consistency, power-management entry/exit, and recovery from reset with default CGM settings restored.
