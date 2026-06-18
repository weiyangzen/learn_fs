# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/Makefile

## Purpose
This Makefile defines how the `dm-vdo` composite object is built and which source files form the VDO target, including its indexer implementation.

## Important APIs, Types, And Functions
- `ccflags-y := -I$(src) -I$(src)/indexer` makes both the VDO root and indexer headers visible.
- `obj-$(CONFIG_DM_VDO) += dm-vdo.o` ties the object to the Kconfig option.
- `dm-vdo-objs` lists core VDO components such as admin state, action manager, block map, completion, dedupe, target glue, journal, slab depot, VIO, queues, logging, and many indexer files.

## Control Flow
Kbuild compiles each listed object and links them into `dm-vdo.o` when `CONFIG_DM_VDO` is enabled. Header lookup relies on local include paths rather than global kernel include directories.

## State And Persistence Behavior
The Makefile has no runtime state. It is the build manifest that determines which source modules participate in the VDO target binary.

## Dependencies And Integration Points
It integrates the VDO target into `drivers/md` Kbuild and explicitly pulls indexer subdirectory sources into the same module. The files researched here, `action-manager.o` and `admin-state.o`, are early entries in this object list.

## Risks
- Missing a source file from `dm-vdo-objs` can produce unresolved symbols or silently omit functionality.
- Include path changes can break local quoted includes across the root/indexer boundary.
- Object ordering usually should not matter for linking, but duplicate symbols or init ordering assumptions should be watched.

## Test Signals
Run kernel builds for `CONFIG_DM_VDO=m/y`, check that all listed objects compile, verify local header includes resolve, and run link/modpost checks for unresolved or duplicate symbols.
