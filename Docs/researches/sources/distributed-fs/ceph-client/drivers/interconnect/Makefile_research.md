# sources/distributed-fs/ceph-client/drivers/interconnect/Makefile

## Purpose
`drivers/interconnect/Makefile` maps interconnect Kconfig symbols to the generic framework objects, provider subdirectories, clock wrapper, and KUnit test object.

## Important APIs, Types, And Functions
`CFLAGS_core.o := -I$(src)` gives `core.o` access to local headers. `icc-core-objs` groups `core.o`, `bulk.o`, and `debugfs-client.o` into the `icc-core.o` composite object. `obj-$(CONFIG_INTERCONNECT*)` entries select the core, provider directories, `icc-clk.o`, and `icc-kunit.o`.

## Control Flow
During kbuild, enabled configuration symbols expand `obj-y` or `obj-m` entries. The core object is built when `CONFIG_INTERCONNECT` is enabled, provider directories are recursed when their symbols are set, and tests build when `CONFIG_INTERCONNECT_KUNIT_TEST` is enabled.

## State And Persistence
The file has no runtime state. It controls build artifacts only.

## Dependencies And Integration Points
It depends on kbuild composite object syntax and must match symbols defined by `drivers/interconnect/Kconfig` and provider subdirectory Kconfigs.

## Risks
Adding a provider in Kconfig without a Makefile entry, or vice versa, causes configuration/build drift. The local include path is specific to `core.o`, so other objects needing local headers would require their own flags or includes.

## Test Signals
Test all relevant config combinations, module versus built-in builds, provider directory recursion, KUnit object build, and clean builds after adding/removing provider symbols.
