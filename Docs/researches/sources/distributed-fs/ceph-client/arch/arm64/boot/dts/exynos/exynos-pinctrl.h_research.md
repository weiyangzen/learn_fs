<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos-pinctrl.h

### Purpose
This header provides Samsung Exynos DTS pinctrl constants for pull configuration, power-down behavior, drive strength, and mux function selection.

### Important APIs, Types, And Functions
It exports 49 macros under `__DTS_ARM64_SAMSUNG_EXYNOS_PINCTRL_H__`: pull values, power-down modes, drive-strength sets for Exynos5420-family, Exynos5433, Exynos7, Exynos7 FSYS1, Exynos850 HSI, and function values `INPUT`, `OUTPUT`, `FUNC_2` through `FUNC_6`, `EINT`, and alias `FUNC_F`.

### Control Flow
There is no C flow. DTS pinctrl states expand these macros into numeric cells; the Exynos pinctrl driver interprets them while applying default, sleep, or runtime pin states.

### State, Persistence, And Dependencies
The header stores no state. The values are hardware/binding constants and must match Exynos pinctrl driver tables and SoC-specific register encodings.

### Integration Points
Exynos DTSI and board files include this header for GPIO, external interrupt, storage, serial, audio, display, and other pin groups. It is part of the common include-time ABI for many Exynos platforms.

### Risks
Drive-strength encodings differ between SoCs and even blocks such as Exynos7 FSYS1 or Exynos850 HSI. Choosing the wrong macro can compile but yield signal-integrity or boot-device failures.

### Test Signals
Build Exynos DTBs, run dt-schema pinctrl checks, and exercise boot-critical pins, GPIO interrupts, suspend/resume pin states, and high-speed interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos-pinctrl.h -->
