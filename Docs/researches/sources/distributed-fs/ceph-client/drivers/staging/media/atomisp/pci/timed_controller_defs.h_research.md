# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/timed_controller_defs.h

## Purpose
Defines register layout constants for the AtomISP timed controller block.

## Important APIs, Types, and Functions
Exports `_HRT_TIMED_CONTROLLER_CMD_REG_IDX` and `_HRT_TIMED_CONTROLLER_REG_ALIGN`.

## Control Flow
No execution. Timed-controller access code uses the command-register index and register alignment.

## State and Persistence Behavior
Constants encode stable hardware layout.

## Dependencies and Integration Points
No includes. Integrates with HRT/timed-controller low-level register helpers.

## Risks
Changing alignment or command index breaks register access.

## Test Signals
Timed-controller command programming should hit the expected register offset.
