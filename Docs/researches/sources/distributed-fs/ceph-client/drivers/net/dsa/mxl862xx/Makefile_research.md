# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/Makefile

## Purpose
Defines build objects for the MxL862xx DSA driver.

## Important APIs, Types, and Functions
Builds `mxl862xx_dsa.o` when `CONFIG_NET_DSA_MXL862` is enabled. The composite object contains `mxl862xx.o` and `mxl862xx-host.o`.

## Control Flow and State
No runtime flow. Build composition decides that the host command transport is linked with the main DSA driver implementation.

## Dependencies and Integration Points
Integrates with Kbuild and the Kconfig symbol from `Kconfig`. The source list must remain synchronized with driver files and any future feature split.

## Risks and Test Signals
Risks include omitting new objects or leaving stale object names after refactors. Test signals are clean module/built-in builds and modpost symbol resolution.
