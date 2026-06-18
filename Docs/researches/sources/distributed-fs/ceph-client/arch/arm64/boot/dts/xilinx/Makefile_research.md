# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/Makefile

## Purpose
This Makefile registers Xilinx ZynqMP and Versal Net arm64 DTBs, including composed Kria starter-kit variants.

## APIs, Types, And Functions
The build API contains 35 `dtb-$(CONFIG_ARCH_ZYNQMP)` entries, 14 `*-dtbs :=` composition rules, 14 `.dtbo` mentions, and 63 `.dtb` mentions. It lists Ultra96, ZCU, ZC, K24/K26 SOM/starter-kit, and Versal Net board targets.

## Control Flow, State, And Persistence
Kbuild builds direct targets and combines SOM base DTBs with starter-kit overlays into composed DTBs. No runtime state exists in the Makefile.

## Dependencies And Integration
The file depends on ZynqMP/Versal DTS and DTBO sources and `CONFIG_ARCH_ZYNQMP`. It integrates with Kbuild overlay composition for Kria board variants.

## Risks And Test Signals
Risks include stale revision-specific target names, invalid base-plus-overlay composition, and missing board coverage. Test with `make ARCH=arm64 dtbs`, ensure composed K24/K26 outputs build, and run `dtbs_check` for changed boards.
