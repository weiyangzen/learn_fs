<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mm-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mm-pinfunc.h

### Purpose
This header defines i.MX8M Mini IOMUX and pad-control constants for DTS pinctrl states.

### Important APIs, Types, And Functions
It exports 649 macros under `__DTS_IMX8MM_PINFUNC_H`. Pad-control helpers include drive strength (`MX8MM_DSE_X1/X2/X4/X6`), slew rate, open drain, pull, hysteresis, pull enable, `MX8MM_SION`, and defaults such as `MX8MM_USDHC_DATA_DEFAULT` and `MX8MM_I2C_DEFAULT`. Function macros follow the tuple `<mux_reg conf_reg input_reg mux_mode input_val>`.

### Control Flow
DTS pinctrl entries expand macros into five-cell tuples consumed by the i.MX pinctrl driver. The driver writes mux, pad configuration, and select-input registers during boot and pin-state transitions.

### State, Persistence, And Dependencies
The header is stateless but encodes hardware register offsets and mux modes. It depends on the i.MX8MM IOMUXC binding and driver interpreting five-cell tuples and pad-control flags consistently.

### Integration Points
i.MX8MM DTS files in the Freescale Makefile include this header for GPIO, USDHC, ENET, ECSPI, SAI, NAND/QSPI, UART, I2C, PCIe clock request, watchdog, and clock pins.

### Risks
The tuple fields are positional; a wrong input-select value or mux mode compiles but breaks peripheral routing. Pad-control defaults combine multiple bits, so changes can affect signal integrity, pull behavior, and forced input behavior for I2C or storage.

### Test Signals
Build all i.MX8MM DTBs, run pinctrl schema checks, inspect generated DTS preprocessing for suspect tuples, and validate storage, Ethernet, serial/I2C/SPI, audio, PCIe clock request, and suspend/resume pin states on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mm-pinfunc.h -->
