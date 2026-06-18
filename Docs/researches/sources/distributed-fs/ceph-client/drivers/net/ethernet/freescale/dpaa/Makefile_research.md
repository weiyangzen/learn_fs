# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa/Makefile

## Purpose
This Makefile builds the DPAA1 Ethernet driver and exposes FMan headers to its sources.

## Important APIs, Types, and Functions
It sets `FMAN = $(srctree)/drivers/net/ethernet/freescale/fman`, adds `-I$(FMAN)` to `ccflags-y`, builds `fsl_dpa.o` when `CONFIG_FSL_DPAA_ETH` is set, and composes it from `dpaa_eth.o`, `dpaa_ethtool.o`, and `dpaa_eth_sysfs.o`. `CFLAGS_dpaa_eth.o := -I$(src)` supports local trace header inclusion.

## Control Flow
Kbuild evaluates the `obj-$(CONFIG_FSL_DPAA_ETH)` line, then links the listed objects into the composite driver. The local include path is required because `dpaa_eth.c` creates tracepoints using `dpaa_eth_trace.h`.

## State and Persistence
There is no runtime state; build artifacts are the only output.

## Dependencies and Integration Points
The file connects DPAA source files with FMan headers and the tracing framework's include expectations.

## Risks
Incorrect include paths break FMan type resolution or trace event generation. Adding new DPAA source files requires extending `fsl_dpa-objs`.

## Test Signals
Build `CONFIG_FSL_DPAA_ETH=m` and `=y`, confirm `fsl_dpa` contains all three objects, and verify tracepoint compilation.
