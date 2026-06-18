# sources/distributed-fs/ceph-client/drivers/fwctl/Makefile

## Purpose
This Makefile wires the fwctl core and provider subdirectories into Kbuild.

## Important Entries
`obj-$(CONFIG_FWCTL) += fwctl.o` builds the core from `main.o`. Provider directories are included for `CONFIG_FWCTL_BNXT`, `CONFIG_FWCTL_MLX5`, and `CONFIG_FWCTL_PDS`.

## Control Flow and State
There is no runtime control flow. The file affects object selection and link composition.

## Dependencies and Integration Points
The provider directories each produce their own module object and import the fwctl namespace exported by the core.

## Risks and Test Signals
Build failures here would appear as missing provider objects or unresolved fwctl symbols. Test signals are allmodconfig and per-provider modular builds.
