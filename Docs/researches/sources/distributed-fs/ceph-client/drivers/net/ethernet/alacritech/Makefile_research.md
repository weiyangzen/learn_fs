# sources/distributed-fs/ceph-client/drivers/net/ethernet/alacritech/Makefile

## Purpose
The Makefile wires the Alacritech SLIC driver into kbuild.

## Important build rules
- `obj-$(CONFIG_SLICOSS) += slicoss.o` builds `slicoss.c` as the module or built-in object selected by Kconfig.

## Control flow and integration
kbuild evaluates `CONFIG_SLICOSS` and includes or omits the driver object accordingly. There are no composite objects or generated files in this directory.

## State and persistence behavior
No runtime state exists. The file affects build artifacts only.

## Dependencies and integration points
It depends on `Kconfig` for `CONFIG_SLICOSS` and on `slicoss.c`/`slic.h` for the actual driver source.

## Risks and edge cases
The rule is intentionally minimal. Renaming the C file or config symbol requires updating this line or the driver will silently disappear from builds.

## Test signals
Build with `CONFIG_SLICOSS=y` and `m`, confirm `slicoss.o` or `slicoss.ko` is produced, and verify `CONFIG_SLICOSS=n` omits it.
