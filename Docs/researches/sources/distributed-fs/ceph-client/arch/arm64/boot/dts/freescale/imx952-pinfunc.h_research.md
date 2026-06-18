## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx952-pinfunc.h

### Purpose
This is the i.MX952 pin-function binding catalog. It gives board DTS files symbolic names for pad mux alternatives and expands each one to the five-cell Freescale/NXP IOMUXC tuple `<mux_reg conf_reg input_reg mux_mode input_val>`.

### Important APIs, Types, And Functions
There are no functions or types. The API consists of 728 `IMX952_PAD_*__*` macros. Compared with i.MX95, the names emphasize mix prefixes such as `WAKEUPMIX_TOP`, `AONMIX_TOP`, `NETCMIX_TOP`, `HSIOMIX_TOP`, `CCMSRCGPCMIX_TOP`, and `VPUMIX_TOP`. The catalog covers GPIO, DAP/JTAG, CAN, FLEXIO, LPI2C/I3C, LPSPI, LPUART, SAI/PDM/TDM, USB/HSIO, USDHC, XSPI/FLEXSPI, NETC timer, watchdog, and debug/observe functions.

### Control Flow
There is no executable control flow. DTS pin groups expand the macros to register cells; pinctrl applies the selected state by programming mux, config, and input-select registers.

### State, Persistence, And Dependencies
The header stores no runtime state. The register offsets and mux/daisy values persist in compiled DTBs. It depends on the i.MX952 IOMUXC layout and on consumers using the Freescale pinctrl binding with exactly five cells per selected pin.

### Integration Points
Integration points are i.MX952 SoC/board DTSI files, the `pinctrl-imx` driver family, peripheral pinctrl states, wakeup and always-on mix configuration, and subsystem nodes for NETC, HSIO, audio, display, storage, serial buses, and GPIO.

### Risks
Tuple mistakes are silent until hardware use. The i.MX952 offsets differ from i.MX95, so reusing i.MX95 pin macros or DTS fragments is unsafe even when pad names look similar. Wakeup and AON pads can affect suspend/resume behavior; HSIO USB over-current/power pins and boot-media pins need board-level electrical validation.

### Test Signals
Useful signals include `dtbs_check`, pinctrl probe logs, hardware loopback or bus enumeration for UART/I2C/SPI/CAN/USDHC/USB/NETC/audio, suspend/resume wake testing, and reference-manual comparison of mux and input-select cells. Source reading signal: 867 lines; 728 `#define` entries; no includes or functions.
