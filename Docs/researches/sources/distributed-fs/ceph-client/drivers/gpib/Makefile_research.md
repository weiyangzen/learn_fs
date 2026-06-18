# sources/distributed-fs/ceph-client/drivers/gpib/Makefile

## Purpose
This Makefile routes GPIB Kconfig symbols to board and helper subdirectories and adds the common include path.

## Important Entries
`subdir-ccflags-y += -I$(src)/include` exposes shared GPIB headers. Each board or helper symbol adds its subdirectory, including Agilent, CB7210, CEC, common, NEC7210, TMS9914, and TNT4882 families.

## Control Flow and State
There is no runtime state. Kbuild evaluates `obj-$(CONFIG_...)` entries to descend into selected subdirectories.

## Dependencies and Integration Points
This file integrates the staging-style GPIB tree with Kbuild and shared headers under `drivers/gpib/include`.

## Risks and Test Signals
Missing subdir entries would silently omit modules even when Kconfig is enabled. Build tests should cover each selected subdirectory and confirm include path availability.
