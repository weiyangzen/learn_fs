# sources/distributed-fs/ceph-client/drivers/net/can/mscan/Kconfig

## Purpose
This Kconfig file controls support for Freescale/Motorola MSCAN based controllers and the MPC5xxx onboard CAN driver.

## Important APIs, Types, And Functions
- `CAN_MSCAN` is a PPC-only tristate for the generic MSCAN support.
- `CAN_MPC5XXX` is available under `CAN_MSCAN`, depends on `PPC_MPC52xx || PPC_MPC512x`, and builds support for MPC5200/MPC5200B/MPC5121 controllers.

## Control Flow
The child option is only visible when `CAN_MSCAN` is enabled. Selecting `CAN_MPC5XXX` builds the combined generic MSCAN core and MPC5xxx platform glue as a module or built-in object.

## State And Persistence
The file controls build-time availability only.

## Dependencies And Integration Points
The PPC dependency reflects register layout, clock, and SoC support assumptions in `mscan.h` and `mpc5xxx_can.c`.

## Risks And Edge Cases
- The generic MSCAN core is not built standalone by this Makefile; it is linked into the MPC5xxx module.
- The help text lists support only for MPC5121 revision 2 and later, but runtime revision checking is limited to compatible matching and clock/register behavior.

## Test Signals
Check PPC randconfig/allmodconfig builds, dependency visibility for MPC52xx/MPC512x, and module naming as `mscan-mpc5xxx.ko`.
