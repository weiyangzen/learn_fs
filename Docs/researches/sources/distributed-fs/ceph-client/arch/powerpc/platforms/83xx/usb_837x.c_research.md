# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_837x.c

## Purpose
`usb_837x.c` configures MPC837x USB DR clock and pinmux for ULPI or serial PHY modes.

## Important APIs, Types, and Functions
`mpc837x_usb_cfg()` finds an available `"fsl-usb2-dr"` node, validates `phy_type` as `"ulpi"` or `"serial"`, maps IMMR, programs SCCR USB clock bits, and muxes USB pins through SICRL.

## Control Flow, State, and Persistence
It writes IMMR registers once during board setup and releases mappings/node references.

## Dependencies and Integration Points
It depends on `mpc83xx.h`, OF USB properties, `get_immrbase()`, and MPC837x board setup such as `mpc837x_rdb.c`.

## Risks and Test Signals
Risks include rejecting DTs without expected `phy_type`, pinmux conflicts with SD/USBB usage, and fixed clock ratio assumptions. Test signals are USB DR probe on ULPI and serial boards, proper interaction with RDB SD muxing, and no warnings for supported DTs.
