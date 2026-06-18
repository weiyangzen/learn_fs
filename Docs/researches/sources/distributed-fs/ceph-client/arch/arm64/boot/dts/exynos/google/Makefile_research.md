<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/Makefile

### Purpose
This Makefile registers Google GS101/Tensor board DTBs under the Exynos hierarchy.

### Important APIs, Types, And Functions
It exports `gs101-oriole.dtb` and `gs101-raven.dtb` under `CONFIG_ARCH_EXYNOS`.

### Control Flow
The parent Exynos Makefile descends into this directory, and these DTBs are compiled when Exynos support is enabled.

### State, Persistence, And Dependencies
State is generated DTB output. Dependencies include GS101 DTS files, `gs101-pinctrl.h`, DTC, and `CONFIG_ARCH_EXYNOS`.

### Integration Points
The DTBs describe Pixel 6 family boards and integrate GS101-specific pinctrl values with Exynos-derived platform support.

### Risks
Both targets share SoC support but differ by board. Incorrect target mapping can produce a booting kernel with wrong board-level peripherals, regulators, or GPIOs.

### Test Signals
Build GS101 DTBs, run schema checks, and boot-test both oriole and raven variants with attention to pinctrl, storage, display, modem-adjacent, and power behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/Makefile -->
