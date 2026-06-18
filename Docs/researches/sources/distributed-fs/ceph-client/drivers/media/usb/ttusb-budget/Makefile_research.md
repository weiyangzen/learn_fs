
# sources/distributed-fs/ceph-client/drivers/media/usb/ttusb-budget/Makefile

## Purpose
The Makefile builds the TTUSB budget DVB driver and adds the DVB frontend include path.

## Important APIs, Types, and Functions
It maps `obj-$(CONFIG_DVB_TTUSB_BUDGET) += dvb-ttusb-budget.o` and adds `-I $(srctree)/drivers/media/dvb-frontends`.

## Control Flow
Kbuild compiles `dvb-ttusb-budget.c` when the Kconfig symbol is enabled. The include path resolves frontend configuration headers such as `stv0299.h`, `tda1004x.h`, and `ves1820.h`.

## State and Persistence
This is build-only state.

## Dependencies and Integration Points
It depends on the `DVB_TTUSB_BUDGET` Kconfig symbol and the in-tree DVB frontend headers.

## Risks and Edge Cases
Moving frontend headers or renaming the Kconfig symbol will break the build. Additional split objects would need explicit Makefile updates.

## Test Signals
Compile with `CONFIG_DVB_TTUSB_BUDGET=m` and confirm the frontend include headers resolve and `dvb-ttusb-budget.ko` links.
