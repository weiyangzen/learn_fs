<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/Makefile

## Purpose
This Makefile selects PowerPC floating-point and SPE math emulation objects based on kernel configuration.

## Important APIs, types, and functions
`math-emu-common-objs` includes dispatcher and hardware-unimplemented helpers. `CONFIG_MATH_EMULATION_FULL` adds full soft-float instruction handlers, loads/stores, FPSCR moves, and conversions. `CONFIG_SPE` adds `math_efp.o`.

## Control flow
Kbuild object lists conditionally add the common, full, and SPE object sets. It disables builtin `fabs` assumptions for `fabs.o` and `math.o`, removes warning flags by default, and re-adds them for extra warning builds.

## State and persistence behavior
No runtime state exists; the file controls build composition and compiler flags.

## Dependencies and integration points
It integrates with arch PowerPC Kconfig options and soft-fp handler sources in the same directory.

## Risks and edge cases
Duplicating `math.o` in full and common lists is intentional through object aggregation but should be watched during Kbuild changes. Compiler builtin optimization for `fabs` must remain disabled.

## Test signals
Build success under `CONFIG_MATH_EMULATION_HW_UNIMPLEMENTED`, `CONFIG_MATH_EMULATION_FULL`, and `CONFIG_SPE` is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/Makefile -->
