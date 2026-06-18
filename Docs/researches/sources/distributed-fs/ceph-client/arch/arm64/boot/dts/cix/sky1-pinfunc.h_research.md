<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-pinfunc.h

### Purpose
This header defines CIX Sky1 pin-function constants for DTS pinctrl nodes. It maps each pad/function choice to an encoded value of `(pad_index << 8 | mux_function)`.

### Important APIs, Types, And Functions
The file exports 390 macros under `__CIX_SKY1_H`, mainly named `CIX_PAD_<pad>_FUNC_<function>`. It covers GPIO001-GPIO153 plus alternate functions for SFI I2C/I3C/SPI/GPIO, SPI, USB over-current/VBUS, UART, I2C, I2S, HDA, GMAC, PM GPIO, and other Sky1 pad groups.

### Control Flow
There is no runtime logic. DTS pinctrl properties use these macros; the preprocessor emits encoded integers that the Sky1 pinctrl driver decodes into pad index and mux selection.

### State, Persistence, And Dependencies
The header has no storage. The encoded values are binding constants and depend on the Sky1 pin controller driver and hardware register layout using the same pad numbering and mux values.

### Integration Points
Sky1 board DTS files include this header for pin groups used by serial, SPI, I2C/I3C, USB, audio, Ethernet, and GPIO consumers. It is a key integration layer between board wiring and the CIX pinctrl driver.

### Risks
The compact bit encoding makes pad-index or mux-value errors compile cleanly but configure the wrong pin function at runtime. Pads often have several valid functions, so duplicate-looking macros must not be normalized without checking the hardware manual.

### Test Signals
Build Sky1 DTBs, run dt-schema checks for pinctrl properties, and validate peripheral I/O on hardware. Pinmux debugfs output and failed driver probe due to missing pins are useful runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-pinfunc.h -->
