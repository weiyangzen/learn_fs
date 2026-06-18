# sources/distributed-fs/ceph-client/drivers/net/can/mscan/Makefile

## Purpose
This Makefile builds the MSCAN MPC5xxx driver from the generic MSCAN core and platform glue.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CAN_MPC5XXX) += mscan-mpc5xxx.o` creates the final driver object/module.
- `mscan-mpc5xxx-objs := mscan.o mpc5xxx_can.o` links generic MSCAN logic with MPC5xxx platform support.

## Control Flow
Kbuild includes both object files in one module when `CAN_MPC5XXX` is enabled.

## State And Persistence
No runtime state is defined here.

## Dependencies And Integration Points
The composition means exported symbols between `mscan.c` and `mpc5xxx_can.c` remain internal to the final module unless exported elsewhere.

## Risks And Edge Cases
Build failures in either generic core or platform glue prevent the single module from linking. There is no separate module for generic MSCAN.

## Test Signals
Run module and built-in builds for `CONFIG_CAN_MPC5XXX`, and confirm `mscan.o` plus `mpc5xxx_can.o` are linked into `mscan-mpc5xxx`.
