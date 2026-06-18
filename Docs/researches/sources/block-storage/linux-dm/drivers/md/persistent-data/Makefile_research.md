# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/Makefile

## Purpose
Build recipe for the `dm-persistent-data` object.

## Main Definitions
- `obj-$(CONFIG_DM_PERSISTENT_DATA) += dm-persistent-data.o`
- `dm-persistent-data-objs` is composed from:
  - `dm-array.o`
  - `dm-bitset.o`
  - `dm-block-manager.o`
  - `dm-space-map-common.o`
  - `dm-space-map-disk.o`
  - `dm-space-map-metadata.o`
  - `dm-transaction-manager.o`
  - `dm-btree.o`
  - `dm-btree-remove.o`
  - `dm-btree-spine.o`

## Role in Repository
The Makefile assembles the whole persistent metadata library into one module/object selected by `DM_PERSISTENT_DATA`.
