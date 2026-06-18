# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_state_machines.h

## Purpose

`gpib_state_machines.h` defines small enums describing the GPIB talker and listener function states tracked by controller-specific cores.

## Important APIs and Types

- `enum talker_function_state`: `talker_idle`, `talker_addressed`, `talker_active`, and `serial_poll_active`.
- `enum listener_function_state`: `listener_idle`, `listener_addressed`, and `listener_active`.

## Control Flow and Integration

The NEC7210 and TMS9914 private structures include these enums. Interrupt/status update paths set them based on hardware address-status bits and then mirror the result into `board->status` bits such as TACS and LACS.

## State and Persistence Behavior

These enums are per-board in-memory state. They are recalculated from hardware status and are not persisted beyond driver attachment.

## Dependencies

No external dependencies beyond the include guard. It is included by chip-controller headers.

## Risks and Test Signals

Incorrect transitions would break talker/listener status reporting and wait conditions. Test signals are address/unaddress command handling, serial poll active state, and correct TACS/LACS updates after ATN/address changes.
