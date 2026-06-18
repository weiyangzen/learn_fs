## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx95-pinfunc.h

### Purpose
This is the i.MX95 pin-function binding catalog. It maps each SoC pad/function combination to the five-cell tuple consumed by the Freescale/NXP IOMUXC pinctrl driver: `<mux_reg conf_reg input_reg mux_mode input_val>`.

### Important APIs, Types, And Functions
There are no C functions or types. The exported API is 726 `IMX95_PAD_*__*` macros. Each macro describes one alternate function for a physical pad, including DAP/JTAG, GPIO banks, ENET/NETC, CAN, FLEXIO, LPI2C/I3C, LPSPI, LPUART, SAI, PDM, USDHC, FLEXSPI/XSPI, MIPI/display/audio support, and wake/AON-mix signals.

### Control Flow
There is no executable control flow. DTS pinctrl groups reference these macros, the C preprocessor expands them into cells, and the pinctrl driver writes mux, pad configuration, and input-select registers when the state is applied during probe, suspend/resume, or pinctrl state changes.

### State, Persistence, And Dependencies
The header itself stores no state. Its values persist in compiled DTBs and become hardware register programming inputs. It depends on the i.MX95 IOMUXC register map, input select register layout, mux mode encoding, and the Freescale pinctrl binding that expects exactly five cells per pin function.

### Integration Points
Integration points include i.MX95 SoC and board DTSI pinctrl nodes, the `pinctrl-imx` family driver, and every peripheral node selecting a pinctrl state. It also intersects with clock and power-domain setup because many alternate functions belong to mixes such as AONMIX, NETCMIX, HSIO, display, and wakeup.

### Risks
The highest risk is an incorrect tuple: a wrong mux offset, input-select offset, mux mode, or daisy value can produce a board that boots but has one dead peripheral. `0x0000` input registers are meaningful for output-only or non-daisy paths, so validation must distinguish intentional zeros from missing input-select data. Shared pads with JTAG, boot media, watchdog, and wake pins have board-level risk if pin groups override critical functions.

### Test Signals
Useful signals include `dtbs_check`, successful pinctrl probe without malformed property warnings, scope or loopback tests for UART/I2C/SPI/CAN/SAI/USDHC/ENET/FLEXSPI pins, suspend/resume pin retention tests, and comparing generated tuples against the NXP reference manual. Source reading signal: 865 lines; 726 `#define` entries; five-cell tuple format; no includes or functions.
