# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/Makefile

## Purpose
This Makefile composes DPAA2 Ethernet, MAC, PTP, and switch drivers.

## Important APIs, Types, and Functions
`fsl-dpaa2-eth` is built from `dpaa2-eth.o`, `dpaa2-ethtool.o`, `dpni.o`, `dpaa2-eth-devlink.o`, and `dpaa2-xsk.o`, with conditional additions for DCB and debugfs. `fsl-dpaa2-ptp` uses `dpaa2-ptp.o dprtc.o`. `fsl-dpaa2-switch` uses switch core, ethtool, DPSW, and flower files. `fsl-dpaa2-mac` includes `dpaa2-mac.o dpmac.o`. `CFLAGS_dpaa2-eth.o := -I$(src)` supports trace header generation.

## Control Flow
Kbuild selects composite objects based on `CONFIG_FSL_DPAA2_ETH`, `CONFIG_FSL_DPAA2_PTP_CLOCK`, `CONFIG_FSL_DPAA2_SWITCH`, `CONFIG_FSL_DPAA2_ETH_DCB`, and `CONFIG_DEBUG_FS`.

## State and Persistence
There is no runtime state in the Makefile.

## Dependencies and Integration Points
The file integrates the main DPAA2 Ethernet driver with MC command files (`dpni`, `dpmac`, `dprtc`, `dpsw`), optional debugfs/DCB sidecars, AF_XDP support, PTP, and switchdev support.

## Risks
Conditional object syntax must match Kbuild expectations; missing optional object entries would compile but silently omit features. Trace include flags must stay aligned with `dpaa2-eth-trace.h`.

## Test Signals
Build each symbol combination as module and built-in, especially DCB on/off and debugfs on/off, and confirm the expected objects are linked into each composite module.
