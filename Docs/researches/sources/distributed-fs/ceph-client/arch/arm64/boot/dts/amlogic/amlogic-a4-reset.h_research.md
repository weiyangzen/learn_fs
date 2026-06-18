<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a4-reset.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a4-reset.h

### Purpose
This header defines Amlogic A4 reset-controller IDs for device-tree `resets` cells. It maps named peripherals and bus bridges onto sparse numeric reset lines across RESET0 through RESET5.

### Important APIs, Types, And Functions
The API is 48 `RESET_*` macros, including USB, USB PHY, audio, DDR, video output, Ethernet, MMC arbitration, IR, SPI, ADC, watchdog, PWM, UART, I2C, SD/eMMC, and AO/main/audio NIC bridge resets. There are no functions or data structures; the include guard is `__DTS_AMLOGIC_A4_RESET_H`.

### Control Flow
There is no runtime control flow in the header. DTS preprocessing substitutes symbolic reset names with integer IDs, and the reset-controller driver later interprets those IDs when kernel consumers request reset assertion or deassertion.

### State, Persistence, And Dependencies
The header has no persistent state. The numeric values encode hardware reset-line positions and depend on the A4 reset-controller binding and driver using the same ID layout.

### Integration Points
A4 board and SoC DTSI files include this header for `resets = <&reset RESET_...>` references. Downstream drivers for USB, audio, Ethernet, MMC, serial, I2C, PWM, and bridge fabrics indirectly depend on these constants resolving to the proper hardware lines.

### Risks
Sparse numbering leaves reserved holes; adding a macro in the wrong slot can reset an unrelated block. Similar macro names across A4/A5/T7 are not interchangeable, so includes must match the SoC-specific compatible.

### Test Signals
Compile all A4 DTBs with `make ARCH=arm64 dtbs`; DTC catches unknown macro references. Hardware validation should exercise each consumer through probe, suspend/resume, and reset recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a4-reset.h -->
