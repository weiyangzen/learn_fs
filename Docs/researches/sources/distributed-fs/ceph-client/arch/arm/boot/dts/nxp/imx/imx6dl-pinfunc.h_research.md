# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6dl-pinfunc.h

## Purpose
`imx6dl-pinfunc.h` is the device-tree pin-function binding table for the NXP/Freescale i.MX6 DualLite/Solo IOMUX controller. It gives DTS authors symbolic names for pad mux alternatives so board files can populate `fsl,pins` arrays with readable tokens instead of raw register offsets.

Each macro expands to the five-cell tuple documented at the top of the file: `<mux_reg conf_reg input_reg mux_mode input_val>`. The Linux i.MX pinctrl binding consumes those cells, while each board DTS appends the sixth pad-control word that encodes electrical configuration such as pull, keeper, drive strength, hysteresis, and open-drain behavior.

## Important APIs, Types, And Functions
There are no C functions, structs, enums, or runtime APIs. The exported interface is a preprocessor namespace of 1,074 `#define` macros across 197 physical pad names.

The macro naming convention is the important contract: `MX6QDL_PAD_<PAD_NAME>__<FUNCTION_NAME>`. The `MX6QDL` prefix is shared with i.MX6Q family DTS content, but this file carries the i.MX6DL/Solo register map. The pad name identifies the external ball or pad group, and the function name identifies the mux target selected by `mux_mode` plus optional daisy-chain `input_reg/input_val`.

Major covered signal families include IPU1 display and CSI, EIM, EPDC, ENET/RGMII, NAND, SD1 through SD4, ECSPI1 through ECSPI4, I2C1 through I2C4, UART1 through UART5, ESAI/AUD, KEY matrix, PWM/GPT/EPIT, USB, HDMI DDC/CEC, SPDIF, FLEXCAN, SDMA events, GPIO banks 1 through 7, boot strap `SRC_BOOT_CFG*`, trace/JTAG, and watchdog outputs. GPIO alternatives are consistently present on most pads, which makes the header the authoritative map from named pads to GPIO controller/line numbers.

## Control Flow
The file has no executable control flow. Its compile-time flow is inclusion guarded by `__DTS_IMX6DL_PINFUNC_H`, followed by a flat list of macro definitions and a closing `#endif`.

At DTS preprocessing time, a pinctrl group such as `MX6QDL_PAD_EIM_D21__I2C1_SCL 0x40010878` expands to the five cells from this header plus the board-supplied pad-control value. The device-tree compiler emits those cells into the DTB, and the kernel `pinctrl-imx` driver later interprets the tuple by programming IOMUXC mux, pad-control, and select-input registers.

## State, Persistence, And Dependencies
The header itself stores no mutable state and persists no data. Its values describe SoC hardware state that will be programmed at boot or when pinctrl states are selected.

It depends on the i.MX pinctrl device-tree binding contract and the SoC-specific IOMUXC register layout. Nonzero `input_reg` values describe daisy-chain select-input registers for shared peripheral inputs, while `input_reg` equal to `0x000` means no select-input programming is needed for that function. The file must remain synchronized with the i.MX6DL/Solo reference manual and the Linux `pinctrl-imx` tuple parser.

## Integration Points
`imx6dl.dtsi` includes this header, and i.MX6DL/Solo board DTS files consume the exported macros inside pinctrl groups. Examples in this source tree include `imx6dl-alti6p.dts`, which uses the definitions for audio clocks/data, CAN, SPI, ENET, HDMI, I2C, UART, USB, and SD pin groups.

The file is also coupled to the sibling `imx6q-pinfunc.h` because both expose the `MX6QDL_PAD_*` namespace. The names intentionally let common `imx6qdl-*.dtsi` board fragments refer to the same logical pads across Quad/DualLite variants, while the included SoC dtsi chooses the correct register offsets and select-input values.

## Risks
Because each entry is raw hardware data, a single wrong cell can silently route a signal to the wrong mux mode, write an invalid IOMUXC offset, or select the wrong daisy-chain input. These faults often show up as board-specific peripheral failures rather than compile errors.

The shared `MX6QDL` namespace is useful but risky: copying values between the i.MX6Q and i.MX6DL headers is unsafe because many equivalent names have different register offsets and select-input values. DTS include ordering must ensure the SoC-appropriate header is visible.

Several pads expose boot strap, watchdog reset, USB ID/over-current/power, and clock-output alternatives. Misusing those macros in board pinctrl can affect boot mode sampling, reset behavior, clocking, or external power switching. GPIO alternatives also require matching GPIO controller/line references in board nodes; mismatches can compile but behave incorrectly.

## Test Signals
Build all i.MX6DL/Solo DTBs that include `imx6dl.dtsi` with `make dtbs` and run `dtbs_check` for pinctrl binding validation. Useful source-level checks include verifying every macro has exactly five numeric cells, no duplicate macro names, legal mux modes for the SoC, and register offsets/select-input values matching the reference manual.

Runtime signals are board-specific: boot logs should show successful pinctrl state application, affected peripherals should probe, and hardware smoke tests should cover ENET/RGMII link, I2C scans, SPI transfers, UART console/flow control, SD/eMMC enumeration, USB ID/OC behavior, GPIO interrupts, display/camera pins, and wake/reset lines that use these macros.
