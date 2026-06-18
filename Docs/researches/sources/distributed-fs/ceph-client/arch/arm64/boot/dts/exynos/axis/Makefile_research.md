<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/Makefile

### Purpose
This Makefile registers Axis ARTPEC ARM64 DTBs under the Exynos DTS hierarchy.

### Important APIs, Types, And Functions
It exports two targets under `CONFIG_ARCH_ARTPEC`: `artpec8-grizzly.dtb` and `artpec9-alfred.dtb`.

### Control Flow
The parent Exynos Makefile descends into this directory, and Kbuild compiles both ARTPEC DTBs when `CONFIG_ARCH_ARTPEC` is enabled.

### State, Persistence, And Dependencies
Generated DTBs are the output. Dependencies include ARTPEC DTS files, `artpec-pinctrl.h`, DTC, and the ARTPEC Kconfig option.

### Integration Points
The DTBs describe Axis ARTPEC platforms and integrate Samsung-derived pinctrl constants with Axis board hardware.

### Risks
The directory sits under `exynos`, so parent recursion must remain intact. ARTPEC pinctrl constants differ from generic Exynos enough that using the wrong header can misconfigure pins.

### Test Signals
Build ARTPEC DTBs, run schema checks, and validate pinctrl/peripheral probing on grizzly/alfred hardware or CI fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/Makefile -->
