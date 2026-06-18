<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/dts/Makefile

## Purpose
Builds Xtensa device-tree blobs for configurations that use Open Firmware flattened device trees.

## Important APIs, Types, And Functions
Defines `dtb-$(CONFIG_OF) += $(addsuffix .dtb, $(CONFIG_BUILTIN_DTB_NAME))` and `dtb-` for `CONFIG_OF_ALL_DTBS` wildcard coverage.

## Control Flow
When OF is enabled, the configured built-in DTB name is converted to a `.dtb` target. The wildcard `dtb-` list supports all-DTB test builds without selecting a specific built-in DTB.

## State And Persistence
No runtime state. Build output is DTB artifacts.

## Dependencies And Integration Points
Depends on `CONFIG_OF`, `CONFIG_BUILTIN_DTB_NAME`, DTS files in the directory, and generic dtc rules.

## Risks And Edge Cases
An empty or wrong built-in DTB name yields missing DTB artifacts. Wildcard coverage only sees local `.dts` files.

## Test Signals
Build with `CONFIG_USE_OF=y` and a real built-in DTB name, and run all-DTB build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/dts/Makefile -->
