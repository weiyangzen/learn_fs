# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/Makefile

## Purpose
Build map for Broadcom thermal drivers. It turns Kconfig symbols into the corresponding object files.

## Important APIs, Types, and Functions
No runtime APIs. Object mappings are `bcm2711_thermal.o`, `bcm2835_thermal.o`, `brcmstb_thermal.o`, `ns-thermal.o`, and `sr-thermal.o`.

## Control Flow
Kbuild expands `obj-$(CONFIG_...)` entries during kernel builds. Enabled symbols compile and link their matching object into the module or built-in image.

## State and Persistence
No runtime state. Build outputs persist in the build tree according to Kbuild.

## Dependencies and Integration Points
This file is consumed by the parent thermal Makefile. It must stay synchronized with symbol names in Broadcom Kconfig and source filenames.

## Risks and Edge Cases
A symbol/object typo silently prevents a selected driver from building or causes build failure. File renames require updates here and in Kconfig.

## Test Signals
Build tests with each Broadcom thermal symbol enabled individually and together should produce the expected objects.
