# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/ti/Makefile

## Purpose
This Makefile registers Texas Instruments K3-family arm64 DTBs and overlays. Entries are grouped by SoC family and board class.

## APIs, Types, And Functions
The build interface includes 115 `dtb-$(CONFIG_ARCH_K3)` lines, 69 `*-dtbs :=` composition rules, 113 `.dtbo` mentions, and 311 `.dtb` mentions. Groups cover AM62x, AM62Ax, AM62Dx, AM62Lx, AM62Px, AM64x, AM65x, J7200, J721E, J721S2, J722S, J784S4, and J742S2. A build-time-test section uses `dtb- += ...` entries enabled by `CONFIG_OF_ALL_DTBS`, and the file sets global `DTC_FLAGS := -@` for overlay symbol support.

## Control Flow, State, And Persistence
Kbuild conditionally builds board DTBs and overlay-composed DTBs. There is no runtime state in the Makefile. The persistent outputs are direct DTBs, DTBOs, and composed DTBs.

## Dependencies And Integration
The file depends on TI K3 DTS/DTBO sources, `CONFIG_ARCH_K3`, `CONFIG_OF_ALL_DTBS`, and Kbuild overlay support. It is a central integration point for TI board enablement and overlay test coverage.

## Risks And Test Signals
Risks include incomplete composed-target coverage, missing `-@` symbols for overlays, stale board references, and `dtb-` build-test entries diverging from real overlay combinations. Test with `make ARCH=arm64 dtbs`, `make ARCH=arm64 dtbs_check`, and output checks for composed overlay DTBs.
