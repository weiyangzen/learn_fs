
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/Makefile

## Purpose

This Makefile builds the HIBMCGE driver as a composite object from its lifecycle, hardware, MDIO, IRQ, TX/RX, ethtool, debugfs, error recovery, and diagnostics source files.

## Important APIs, Types, and Functions

- `ccflags-y += -I$(src)` ensures local headers are available.
- `obj-$(CONFIG_HIBMCGE) += hibmcge.o` selects the composite object.
- `hibmcge-objs` lists `hbg_main.o`, `hbg_hw.o`, `hbg_mdio.o`, `hbg_irq.o`, `hbg_txrx.o`, `hbg_ethtool.o`, `hbg_debugfs.o`, `hbg_err.o`, and `hbg_diagnose.o`.

## Control Flow

No runtime control flow exists. Kbuild links the listed objects into one module or built-in object.

## State and Persistence

Only build state is affected.

## Dependencies and Integration Points

The composite arrangement allows `hbg_main.c` to register the PCI driver while the other files provide helper symbols in the same final object.

## Risks and Edge Cases

The object list must include every file that defines non-static symbols used by the driver. Missing `hbg_trace.h` is expected because it is included by `hbg_txrx.c` for tracepoint generation rather than compiled directly.

## Test Signals

Build `CONFIG_HIBMCGE=m` and verify `hibmcge.ko` contains the module metadata from `hbg_main.c` and resolves helper symbols from all listed objects.
