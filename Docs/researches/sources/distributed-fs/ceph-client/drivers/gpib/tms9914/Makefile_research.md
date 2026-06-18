# sources/distributed-fs/ceph-client/drivers/gpib/tms9914/Makefile

## Purpose
This Kbuild file builds the shared TMS9914 GPIB support object when `CONFIG_GPIB_TMS9914` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_GPIB_TMS9914) += tms9914.o`. There are no runtime APIs in the Makefile itself.

## Control flow
Kbuild includes `tms9914.o` only when the TMS9914 config symbol is selected. The object exports helper symbols used by board-specific TMS9914-based drivers.

## State and persistence behavior
The file affects build composition only and stores no runtime state.

## Dependencies and integration points
It depends on Kbuild and `CONFIG_GPIB_TMS9914`. The compiled object integrates with board drivers through exported GPL/non-GPL symbols in `tms9914.c`.

## Risks and edge cases
If TMS9914 board drivers are enabled without this object, exported helper references would fail at link or module load time.

## Test signals
Build with `CONFIG_GPIB_TMS9914=y` and `=m`, and build a dependent board driver to confirm the exported symbols resolve.
