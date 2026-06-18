<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/Makefile

## Purpose
Top-level TI ARM devicetree Kbuild router. It delegates TI board DTB builds to `davinci`, `keystone`, and `omap` subdirectories.

## Important APIs/types/functions
- `subdir-y += davinci`
- `subdir-y += keystone`
- `subdir-y += omap`

## Control flow
Kbuild descends into all three subdirectories whenever this directory is visited by the ARM DT build.

## State and persistence behavior
No runtime state. The persistent behavior is source-tree organization: TI DTB target lists live in child Makefiles rather than this router.

## Dependencies and integration points
Depends on child directories and their Makefiles. Integrates with `arch/arm/boot/dts/Makefile` recursion.

## Risks and edge cases
Adding a new TI DT subdirectory without updating this file prevents normal `dtbs` traversal. Removing a subdirectory without removing the line breaks the build.

## Test signals
Run `make ARCH=arm dtbs` and verify Kbuild visits `ti/davinci`, `ti/keystone`, and `ti/omap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/Makefile -->
