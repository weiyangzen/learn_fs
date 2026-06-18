# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/usb_834x.c

## Purpose
`usb_834x.c` configures MPC834x USB DR and MPH clock/pinmux routing.

## Important APIs, Types, and Functions
`mpc834x_usb_cfg()` maps IMMR, reads current SCCR/SICRL/SICRH values, scans `"fsl-usb2-dr"` for `phy_type` and `dr_mode`, marks whether DR owns port0/port1, scans `"fsl-usb2-mph"` for `port0`/`port1`, warns on port conflicts, and writes back final clock and mux registers.

## Control Flow, State, and Persistence
No local state persists. The hardware SCCR/SICR bits persist for the boot session.

## Dependencies and Integration Points
It depends on OF USB nodes/properties, MPC834x bit definitions in `mpc83xx.h`, and board setup files such as ASP834x and MPC834x ITX.

## Risks and Test Signals
Risks include conflicting DR/MPH port declarations, unsupported PHY types, and writing shared USB clock settings for both controllers. Test signals are DR and MPH controller probe, correct port ownership, expected warnings on conflicting DT, and functional UTMI/serial/ULPI modes.
