# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/rot0_regs.h

## Purpose
`rot0_regs.h` defines the global register addresses for Gaudi2 rotator instance 0. It controls rotator mode, completion messaging, AXI attributes, error reporting, buffering, MSS halt/interrupt state, QMAN force-stop, and clock controls.

## Important APIs, Types, And Functions
The macros name KMD mode, completion queue enable/address/data/AWUSER/AXI, completion message threshold/AXI, writeback AXI, error config/status, WBC/RSB/MRSB outstanding/rate-limit/inflight/occupancy/info/monitor registers, MSS halt/status/mask registers for SEI/SPI, pad calculation disable, QMAN config, clock enable, and MSS status.

## Control Flow
There is no C logic. Driver flow uses these addresses to enable the rotator, configure completion writes, tune buffering, detect and mask interrupts, force-stop QMAN when needed, poll idle/empty state, and halt/resume the MSS sub-blocks during recovery.

## State, Persistence, And Dependencies
State is persistent hardware configuration and status. It depends on `rot0_masks.h` for bit meanings and on descriptor/QMAN headers for the work-submission path. Reset clears or reinitializes these registers according to hardware defaults.

## Integration Points
This is the top-level rotator MMIO block used by initialization, error handling, completion processing, power/reset management, and security register-range definitions.

## Risks
Incorrect completion queue configuration can lose job completion notifications. Force-stop and halt controls can strand in-flight memory writes. Error-status interpretation depends on the matching masks and interrupt polarity. Clock controls can make later MMIO polling unreliable if used at the wrong time.

## Test Signals
Signals include KMD-mode enable readback, completion message delivery, WBC/RSB/MRSB idle status after jobs, SEI/SPI status/mask behavior, QMAN force-stop recovery, and clean reset of rotator 0 without affecting rotator 1.
