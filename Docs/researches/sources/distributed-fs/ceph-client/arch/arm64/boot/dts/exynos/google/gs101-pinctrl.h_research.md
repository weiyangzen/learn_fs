<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/gs101-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/gs101-pinctrl.h

### Purpose
This header defines GS101 pinctrl binding constants for Google Tensor/Pixel DTS files.

### Important APIs, Types, And Functions
It exports 17 macros: pull values, power-down modes, drive strengths in mA (`2_5`, `5`, `7_5`, `10`), and function constants for input, output, alternate functions 2/3, and external interrupt.

### Control Flow
DTS preprocessing expands constants in pin configuration states; the GS101/Exynos pinctrl driver applies the numeric values when selecting active or sleep pin states.

### State, Persistence, And Dependencies
The header is stateless. Values are part of the GS101 DTS binding contract and must match the driver and SoC register encodings.

### Integration Points
`gs101-oriole` and `gs101-raven` DTS files include this header for GPIO/peripheral pin states. It integrates Pixel board descriptions with the Exynos pinctrl subsystem.

### Risks
GS101 drive strength uses explicit mA-level names, unlike generic Exynos level names. Mixing headers or copying pin states across SoCs can produce incorrect electrical behavior.

### Test Signals
Build GS101 DTBs, run pinctrl schema checks, and validate GPIO interrupts, serial/storage/display-related pins, and suspend/resume pin states on both board variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/gs101-pinctrl.h -->
