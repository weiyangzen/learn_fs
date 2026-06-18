# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkmp.h

## Purpose
This header declares the N*K/M/P PLL class used by CPU and peripheral PLL descriptors.

## Important APIs, Types, And Functions
It defines `struct ccu_nkmp`, `SUNXI_CCU_NKMP_WITH_GATE_LOCK`, conversion helper, and `ccu_nkmp_ops`.

## Control Flow
There is no runtime control flow. Static descriptors are interpreted by `ccu_nkmp.c`.

## State And Persistence
Descriptor state includes enable/lock bits, N/K multiplier fields, M/P divider fields, optional fixed postdivider, optional max rate, and common metadata.

## Dependencies And Integration Points
It depends on CCF and common/div/mult headers. Integration is with PLL-heavy SoC CCU files such as V3s and A80.

## Risks
The P field is power-of-two encoded in the implementation. Width-zero fields are legal for some hardware and must be handled carefully.

## Test Signals
PLL programming tests, CPU clock changes, and clock-summary rate checks validate it.
