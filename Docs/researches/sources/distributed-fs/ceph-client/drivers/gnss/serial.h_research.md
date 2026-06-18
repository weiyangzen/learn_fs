# sources/distributed-fs/ceph-client/drivers/gnss/serial.h

## Purpose
`serial.h` declares the private GNSS serial helper interface used by serial chipset drivers.

## Important APIs, Types, and Functions
`struct gnss_serial` stores the serdev device, GNSS core device, baud speed, optional `struct gnss_serial_ops`, and flexible driver data. `enum gnss_serial_pm_state` defines `OFF`, `ACTIVE`, and `STANDBY`. `struct gnss_serial_ops` currently exposes `set_power()`. The header declares allocation, free, register, deregister, exported PM ops, and `gnss_serial_get_drvdata()`.

## Control Flow and State
The header has no runtime flow. It defines how chipset drivers attach their private state to the generic serial helper and provide power transitions.

## Dependencies and Integration Points
It depends on termbits for `speed_t`, PM types, and opaque GNSS/serdev types supplied by includers. MTK and UBX use it directly.

## Risks and Test Signals
The flexible array driver data requires callers to request enough private bytes during allocation. Compile tests should catch prototype drift between header and implementation. Runtime tests should verify power callback ordering across register, open, close, suspend, and deregister.
