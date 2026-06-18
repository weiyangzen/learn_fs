<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/Makefile -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/Makefile

## Purpose
Defines how the persistent-data library is built into `dm-persistent-data.o` when `CONFIG_DM_PERSISTENT_DATA` is enabled.

## Important APIs, Types, And Functions
The object list includes `dm-array.o`, `dm-bitset.o`, `dm-block-manager.o`, `dm-space-map-common.o`, `dm-space-map-disk.o`, `dm-space-map-metadata.o`, `dm-transaction-manager.o`, `dm-btree.o`, `dm-btree-remove.o`, and `dm-btree-spine.o`. This ordering records the library components that collectively expose the persistent metadata API.

## Control Flow
Kbuild evaluates `obj-$(CONFIG_DM_PERSISTENT_DATA)` and links the listed implementation objects into one module or built-in object. Consumers see a single persistent-data library even though functionality is split across block manager, transaction manager, btree, array/bitset, and space-map layers.

## State And Persistence
The Makefile has no runtime state. It is significant for persistence because omitting one object would remove part of the transactional metadata stack and could leave exported APIs unresolved.

## Dependencies And Integration Points
The file integrates with the Linux Kbuild system and the Kconfig symbol in the same directory. It also documents layering: common structures and transaction/block management are linked with higher-level containers and allocation maps.

## Risks
The main risk is object list drift. A new source file that provides exported symbols must be added here, and deleting or renaming a source must be reflected here. Build-only validation catches most errors, but subtle module layout changes can affect symbol export availability for dm targets.

## Test Signals
Compile with the persistent-data library built-in and modular. Run `modpost`/link checks for unresolved symbols and build the dm targets that use this library.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/Makefile -->
