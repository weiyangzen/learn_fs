# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/phy.h

## Purpose
`phy.h` is the public PHY interface and register-definition header for e1000e PHY support. It exposes the copper PHY helper functions implemented in `phy.c` and defines the family-specific PHY register offsets, page-encoding helpers, and bit masks needed by e1000e MAC implementations.

## Important APIs, types, and functions
The declarations cover reset blocking, PHY identification, address discovery, generic and family-specific register read/write functions, Kumeran accessors, link setup, forced speed/duplex, LPLU, polarity, downshift, cable length, PHY info, power up/down, BM wake-register access, HV page access, and 82577-specific helpers. The macros define `E1000_MAX_PHY_ADDR`, IGP page selection and AGC constants, BM/HV page and wake opcodes, Kumeran masks, IFE controls, and 82577 status/control/diagnostic masks.

## Control flow
This header does not implement runtime control flow, but it encodes key access conventions used by `phy.c`. `BM_PHY_REG(page, reg)` builds synthetic offsets containing page and register numbers. `BM_PHY_REG_PAGE` and `BM_PHY_REG_NUM` decode those offsets. The constants decide whether register access is direct MDIC, page-selected IGP/BM, wake-register opcode based, or HV debug-port based.

## State and persistence behavior
The header defines hardware register state, not storage. Its masks are used to mutate persistent PHY state such as wake enable bits, LPLU, SmartSpeed, Kumeran control, MDI/MDIX mode, polarity, speed, link status, and cable length. Because the macros define how page state is encoded, any mismatch with silicon expectations persists as wrong hardware programming.

## Dependencies and integration points
`phy.h` depends on `struct e1000_hw`, `enum e1000_phy_type`, `s32`, `u16`, `u32`, `bool`, and bit helpers from the e1000e/Linux include stack. It is included by e1000e source files that need PHY operations and by MAC-specific setup files that assign function pointers.

## Risks
The main risk is silent hardware misprogramming from incorrect constants. Register pages overlap by PHY family, and the BM/HV page encoding uses upper offset bits; a wrong shift or mask can access a valid but unintended PHY register. Prototype changes have broad blast radius because these functions are operation-table entry points.

## Test signals
Compile coverage across e1000e MAC variants is the first signal. Runtime signals include correct PHY type detection, link setup on each supported family, WoL register access on BM/HV PHYs, and ethtool PHY diagnostics matching expected speed, polarity, MDI-X, and cable length values.
