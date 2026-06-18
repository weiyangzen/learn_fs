# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sh73a0-clock.h

## Purpose
`sh73a0-clock.h` defines clock IDs for the Renesas SH73A0 CPG and MSTP module-stop controllers.

## Important APIs, types, and functions
All macros use the `SH73A0_CLK_*` namespace. The CPG section defines root and derived clocks such as `MAIN`, `PLL0` through `PLL3`, DSI PHY clocks, and bus clocks. MSTP sections `MSTP0` through `MSTP5` define module clock bits for peripherals including I2C/IIC, SCIFA, SDHI, MMCIF, USB, FSI, CEU/CSI, TPU, KEYSC, and interrupt controller blocks. Values in MSTP sections are bit positions rather than one global monotonic index.

## Control flow
The header provides constants for device-tree clock specifiers. Runtime enable/disable flows through the SH73A0 CPG/MSTP clock provider, which interprets the ID according to the referenced provider/register group.

## State and persistence
The header is stateless. CPG and MSTP hardware registers hold the actual clock and module-stop state. ABI stability is required because DTS consumers depend on these numeric IDs or bit positions.

## Dependencies and integration points
It integrates with SH73A0 DTS, Renesas CPG/MSTP drivers, serial, storage, USB, camera, audio, timer, keypad, and interrupt-controller related devices.

## Risks and test signals
Risks include treating MSTP bit numbers as global IDs, using a clock under the wrong provider, and changing values that correspond to hardware register bits. Test signals include DT validation, CPG/MSTP provider registration, serial console, SDHI/MMCIF, USB, FSI audio, camera, keypad, and timer operation.
