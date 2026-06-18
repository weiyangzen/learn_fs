# sources/distributed-fs/ceph-client/drivers/input/tablet/Makefile

## Purpose
This Makefile maps tablet Kconfig symbols to the driver object files that implement each supported tablet family.

## Important APIs, types, and functions
The file has six `obj-$(CONFIG_...)` assignments: `acecad.o`, `aiptek.o`, `hanwang.o`, `kbtab.o`, `pegasus_notetaker.o`, and `wacom_serial4.o`.

## Control flow
Kbuild evaluates each assignment according to the corresponding Kconfig tristate. Built-in selections compile into the kernel image, module selections produce loadable modules, and unset symbols omit the object.

## State and persistence
There is no runtime state. Build state is derived from `.config` and Kbuild's generated objects.

## Dependencies and integration points
The Makefile integrates the tablet directory with the kernel build system and must remain aligned with `drivers/input/tablet/Kconfig` symbol names and with source filenames.

## Risks
Misspelled symbols or object names silently break driver builds for a configuration. Adding a driver requires updating both Kconfig and this Makefile.

## Test signals
Build each tablet symbol as `m` and `y`, check generated module names, and run `make drivers/input/tablet/` or allmodconfig-style builds.
