<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/artpec-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/artpec-pinctrl.h

### Purpose
This header defines Axis ARTPEC pinctrl constants used by DTS pin configuration nodes.

### Important APIs, Types, And Functions
It exports 19 macros: pull values `ARTPEC_PIN_PULL_NONE/DOWN/UP`, pin functions `INPUT`, `OUTPUT`, `FUNC_2` through `FUNC_6`, `EINT`, alias `FUNC_F`, and ARTPEC drive-strength values `ARTPEC_PIN_DRV_SR1` through `SR6` encoded as `0x8` through `0xd`.

### Control Flow
DTS preprocessing substitutes these constants into pin configuration properties. The pinctrl driver consumes the resulting numeric values during boot and pin-state changes.

### State, Persistence, And Dependencies
The header has no state. Its values depend on the ARTPEC pinctrl binding and driver interpretation of pull, mux, external interrupt, and drive-strength fields.

### Integration Points
ARTPEC DTSI/board files include this header for pin groups. It integrates with the ARTPEC pinctrl driver and with peripherals that request pin states.

### Risks
The constants resemble Exynos values but ARTPEC drive strengths are separate. Reusing generic Exynos drive macros could produce incorrect electrical characteristics.

### Test Signals
Build ARTPEC DTBs, run pinctrl schema checks, and test GPIO, EINT, serial, storage, and high-speed pins on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/artpec-pinctrl.h -->
