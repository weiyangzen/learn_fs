# sources/distributed-fs/ceph-client/include/dt-bindings/clock/samsung,exynos7870-cmu.h

## Purpose
`samsung,exynos7870-cmu.h` defines clock IDs for Exynos7870 CMU domains. It is split by hardware clock-controller domain rather than one global namespace.

## Important APIs, types, and functions
The header exports `CLK_*` IDs plus domain count macros: `MIF_NR_CLK`, `DISPAUD_NR_CLK`, `FSYS_NR_CLK`, `G3D_NR_CLK`, `ISP_NR_CLK`, `MFCMSCL_NR_CLK`, and `PERI_NR_CLK`. Sections include MIF, DISPAUD, FSYS, G3D, ISP, MFCMSCL, and PERI clocks, covering bus dividers, CMU interconnect outputs, display/audio, USB/MMC, GPU, camera/ISP, codec/scaler, UART, SPI, I2C, PWM, ADC, TMU, and watchdog clocks.

## Control flow
The header supplies constants for DT clock specifiers. Runtime behavior is implemented by Exynos7870 CMU provider instances; each provider interprets IDs in its own domain.

## State and persistence
The header has no state. Domain count macros bound driver arrays and DT-visible IDs, so changing them or reordering IDs can break ABI and provider table indexing.

## Dependencies and integration points
It integrates with Exynos7870 device trees, Samsung CMU driver data, MIF/FSYS/DISPAUD/G3D/ISP/MFCMSCL/PERI providers, and peripheral drivers for display, audio, USB, MMC, GPU, camera, video, UART/I2C/SPI/PWM, thermal, and watchdog.

## Risks and test signals
Risks include provider-domain mixups, incorrect `*_NR_CLK` values, and clock IDs that look globally unique but are only local. Test signals include DT validation, each CMU domain registering its declared clock count, boot logs free of clock lookup failures, and smoke tests for display/audio/storage/USB/GPU/camera and PERI serial devices.
