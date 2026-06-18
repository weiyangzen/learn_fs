# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ul-pinfunc.h

## Purpose
This header is the Devicetree pin-function catalog for the NXP/Freescale i.MX6UL IOMUX controller. It exposes `MX6UL_PAD_*__*` macros that expand to the five-cell `PIN_FUNC_ID` tuple used inside board DTS `fsl,pins` properties, followed by a separate pad configuration cell supplied by the board file. The header is included by `imx6ul.dtsi` and indirectly by i.MX6UL board DTS files.

The file contains 943 pin-function macros across 124 physical pad names. It covers boot mode pins, SNVS tamper pins, JTAG, GPIO1, UART, ENET, LCD, NAND, SD, and CSI pad banks. Function coverage includes EIM, CSI, USDHC, LCDIF, ENET, GPIO, SRC, UART, I2C, ECSPI, SAI, PWM, GPT, SDMA, USB, watchdog, and clock output routes.

## Important APIs, Types, and Functions
The public API is the macro namespace, not callable C code. Each macro has the form `MX6UL_PAD_<pad>__<signal>` and expands as `<mux_reg conf_reg input_reg mux_mode input_val>`. Board DTS entries use it as `<PIN_FUNC_ID CONFIG>`, so one pin consumes six `u32` cells in `fsl,pins`. This contract is documented by `Documentation/devicetree/bindings/pinctrl/fsl,imx-pinctrl.txt` and the i.MX35/i.MX5x/i.MX6 pinctrl YAML, which lists `fsl,imx6ul-iomuxc`.

`mux_reg` and `conf_reg` are IOMUXC offsets, `input_reg` is the daisy/select-input offset or zero, `mux_mode` is the ALT value, and `input_val` is the daisy value. The file has 317 macros with nonzero input select registers and 626 without select-input programming.

## Control Flow
The header has no executable control flow. At build time, `dtc` expands board `fsl,pins` entries into integer cells. At boot, the `fsl,imx6ul-iomuxc` device matches `drivers/pinctrl/freescale/pinctrl-imx6ul.c`, and generic `pinctrl-imx.c` validates each entry as `FSL_PIN_SIZE` (24 bytes). `imx_pinctrl_parse_pin_mmio()` reads the tuple plus board config, moves SION from config into the mux mode, and stores mux/config/input metadata. When a state is selected, `imx_pmx_set_one_pin_mmio()` writes mux and optional input-select registers; pinconf writes pad control.

## State and Persistence Behavior
The file stores no mutable runtime state. Its persistent effect is ABI-like source stability: DTS files store macro names and compiled DTBs store numeric tuples. Runtime state is the IOMUXC mux, select-input, and pad-control register contents written during boot or pinctrl state changes.

## Dependencies and Integration Points
It is included by `imx6ul.dtsi`, reused by `imx6ull-pinfunc.h`, consumed by many i.MX6UL/i.MX6ULL board files, parsed by `pinctrl-imx.c`, matched through `pinctrl-imx6ul.c`, and described by `fsl,imx35-pinctrl.yaml` plus the common i.MX pinctrl text binding. Peripheral drivers integrate indirectly through board pinctrl states for UART, I2C, SDHC, ENET, LCDIF, NAND, CSI, SPI, SAI, PWM, and USB.

## Risks
Wrong offsets can write the wrong IOMUXC registers; wrong mux modes route pads to wrong peripherals; wrong input registers or daisy values break RX/card-detect/MDIO-style input paths while output muxing may look correct. Other risks are i.MX6UL/i.MX6ULL variant confusion, DCE/DTE UART confusion, treating zero input registers as real daisy registers, unsafe board pad config cells, and macro rename/removal breaking DTS builds.

## Test Signals
Build i.MX6UL/i.MX6ULL DTBs with `make ARCH=arm dtbs`; run `dtbs_check` against `Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml`; boot-test UART/I2C/SDHC/ENET/LCD/NAND/CSI routes; inspect pinctrl debugfs and GPIO/input behavior. For tuple edits, compare generated DTB cells and cross-check offsets against the i.MX6UL reference manual.
