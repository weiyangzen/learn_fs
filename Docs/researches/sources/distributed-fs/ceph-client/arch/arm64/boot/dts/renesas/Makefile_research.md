# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/renesas/Makefile

## Purpose
This Makefile declares Renesas arm64 DTBs and overlay compositions across R-Car, RZ/G, RZ/V, and related families. It uses many SoC-specific Kconfig guards.

## APIs, Types, And Functions
The build interface consists of 145 `dtb-$(CONFIG_...)` assignments and 39 `*-dtbs :=` composition rules. It references 66 `.dtbo` overlays and 223 `.dtb` names. It also sets a specific DTC warning suppression, `DTC_FLAGS_r8a779g3-sparrow-hawk += -Wno-spi_bus_bridge`, for a named board.

## Control Flow, State, And Persistence
Kbuild evaluates targets according to the enabled Renesas SoC symbols. Overlay composition rules build combined board variants. The Makefile does not hold runtime state; built DTBs persist as boot artifacts.

## Dependencies And Integration
Dependencies include the named DTS/DTBO files, Renesas Kconfig symbols, and Kbuild composition rules. The file is the bridge between board DTS additions and the arm64 build.

## Risks And Test Signals
Risks include incorrect SoC guards, missing overlay components, and DTC warning suppression hiding a real binding issue if overused. Test with `make ARCH=arm64 dtbs`, focused `dtbs_check` for changed boards, and verification that composed board variants appear in the build output.
