# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/imx/imx6ull-pinfunc.h

## Purpose
This header extends the i.MX6UL pin-function catalog for i.MX6ULL. It includes `imx6ul-pinfunc.h`, fixes a small set of shared i.MX6UL/i.MX6ULL signal definitions with `#undef` plus replacement `#define`, and adds i.MX6ULL-only alternate routes. It is included by `imx6ull.dtsi` together with `imx6ull-pinfunc-snvs.h`.

The file contains 64 macro definitions: five replacement `MX6UL_PAD_*` macros for shared signals whose input-select values differ on i.MX6ULL, and 59 `MX6ULL_PAD_*` macros for i.MX6ULL-only routes. The added route families are dominated by EPDC display/power/control signals and ESAI audio signals, plus UART5 alternatives on UART1 pads.

## Important APIs, Types, and Functions
The API is a layered preprocessor contract. The file includes the base i.MX6UL header, undefines five inherited UART5-related macros, redefines those same `MX6UL_PAD_*` names with i.MX6ULL-correct tuples, then adds new `MX6ULL_PAD_*__*` macros. All macros use `<mux_reg conf_reg input_reg mux_mode input_val>`, with board DTS supplying the final config cell.

The replacements are important because shared i.MX6UL/i.MX6ULL board sources can continue using `MX6UL_PAD_*` names while receiving i.MX6ULL-specific UART5 daisy values. Most new i.MX6ULL-only definitions use mux mode `0x9`; nine definitions have nonzero input-select registers.

## Control Flow
There is no runtime control flow, but include order is significant. `imx6ull.dtsi` includes the i.MX6UL base and then this header, so the `#undef`/replacement definitions are visible to i.MX6ULL board DTS compilation. `dtc` emits the resulting six-cell `fsl,pins` entries, and the same generic i.MX pinctrl path parses them as normal `FSL_PIN_SIZE` entries.

At runtime, `pinctrl-imx.c` parses tuple cells, stores mux/config/input metadata, writes mux registers, optionally writes input select registers, and applies pad control when clients select pinctrl states.

## State and Persistence Behavior
The header stores no runtime state. Its persistent behavior is that i.MX6ULL DTBs encode a combined macro universe: base i.MX6UL routes, corrected shared routes, and i.MX6ULL-only routes. The same symbolic `MX6UL_PAD_*` macro can expand differently depending on whether the DTS include graph is i.MX6UL or i.MX6ULL.

## Dependencies and Integration Points
It depends on `imx6ul-pinfunc.h`, is included by `imx6ull.dtsi`, and is consumed by i.MX6ULL and shared i.MX6UL/i.MX6ULL board files. Runtime parsing is through `drivers/pinctrl/freescale/pinctrl-imx.c` and matching through `pinctrl-imx6ul.c`. Structural validation is through `fsl,imx35-pinctrl.yaml`. Peripheral integration is mainly EPDC, ESAI, and corrected UART5 DCE/DTE routing.

## Risks
The main risks are include-order and variant drift. Losing a replacement macro can make i.MX6ULL boards inherit i.MX6UL UART5 daisy values while still compiling. Using `MX6ULL_PAD_*` routes on pure i.MX6UL hardware is invalid. EPDC ALT9 routes are spread across LCD, ENET, UART, and CSI-origin pads, so pin conflicts are likely if board groups are copied casually. Pad config values remain board-specific and can still be electrically wrong.

## Test Signals
Build i.MX6ULL DTBs, inspect expanded tuples for the five replacement UART5 macros, and run `dtbs_check` against `fsl,imx35-pinctrl.yaml`. Runtime tests should include UART5 DCE/DTE behavior, EPDC display bring-up, ESAI audio if wired, and pinctrl debugfs group checks. For replacement edits, compare generated DTBs for shared i.MX6UL/i.MX6ULL DTSI users.
