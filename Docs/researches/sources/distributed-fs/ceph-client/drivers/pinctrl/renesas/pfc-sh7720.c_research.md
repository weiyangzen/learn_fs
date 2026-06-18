# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7720.c

## Purpose
This file is the Renesas SH7720 pinmux descriptor for the shared `sh_pfc` core. It exports `sh7720_pinmux_info`, which describes GPIO pins, alternate-function marks, mode-selector bits, control registers, and data registers for the SH7720 port banks PTA through PTV.

## Important APIs, Types, And Functions
The top enum defines data/input/output tokens for ports PTA, PTB, PTC, PTD, PTE, PTF, PTG, PTH, PTJ, PTK, PTL, PTM, PTP, PTR, PTS, PTT, PTU, and PTV, followed by per-pin function tokens and selector tokens for `PSELA`, `PSELB`, `PSELC`, and `PSELD`. Function marks cover BSC, LCDC, AFE, IIC, DAC/ADC, USB, INTC, PCC, HUDI/JTAG-like debug, DMAC, SIOF0/1, SCIF0/1, TPU, SIM, MMC, and status signals. `pinmux_data[]` maps normal GPIO states and alternate marks to per-pin function mode plus optional PSEL selector values. `pinmux_pins[]` exposes each GPIO-capable pin through `PINMUX_GPIO()`. `pinmux_func_gpios[]` publishes legacy function-GPIO names with `GPIO_FN()`. `pinmux_config_regs[]` describes the 16-bit `P?CR` control registers at `0xa4050100` onward; most use 2-bit fields for function/output/input, while partial-width banks use `PINMUX_CFG_REG_VAR()`. `pinmux_data_regs[]` maps 8-bit `P?DR` data registers for each bank.

## Control Flow
The common SuperH PFC driver receives `sh7720_pinmux_info` from SoC setup. For GPIO requests, the core validates the requested input/output state through `pinmux_data[]`, writes the corresponding `P?CR` field, and reads or writes the matching `P?DR` bit. For alternate functions, the core applies the pin function token and any needed `PSELx` selector state before exposing the requested `GPIO_FN()` signal. There are no custom callbacks in this file; runtime behavior is entirely driven by the static arrays.

## State And Persistence
The source file contains immutable descriptor data only. Runtime state and synchronization are owned by the shared `sh_pfc` driver. Hardware mode and level state persist in SH7720 PFC registers until reset or later pinctrl/GPIO operations. Several pins are input-only in the GPIO table, notably parts of PTE and most of PTF, and the config-register tables reflect those missing output states with zero placeholders.

## Dependencies And Integration Points
It depends on `<cpu/sh7720.h>` for pin numbering and `sh_pfc.h` for table macros. Integration points include gpiolib via `PINMUX_GPIO()` pins and legacy SuperH function GPIO consumers via `GPIO_FN()`. Peripheral integration covers external bus data/address/control, LCD data and sync signals, analog front-end pins, IIC, DAC/ADC, USB1/USB2 control, external interrupts, PC Card controller pins, audio/HUDI/debug pins, DMA handshakes, SIOF, SCIF, TPU timers, SIM, MMC, and status pins.

## Risks
The main risk is selector coupling: many alternate functions require both a pin function state and a `PSELA`/`PSELB`/`PSELC`/`PSELD` value, so missing the selector produces the wrong peripheral even when the pin is in function mode. The control registers use compact 2-bit encodings with reserved states; zero placeholders must remain aligned to prevent exposing invalid output modes. Some pins intentionally lack output capability, and marking them as output-capable would create invalid GPIO behavior. Because the file uses legacy function-GPIO exposure rather than modern named groups/functions, consumers have less structural validation of complete bus pin sets.

## Test Signals
Useful validation includes successful SH7720 PFC registration, expected GPIO count across PTA-PTV, GPIO input/output tests that confirm input-only pins reject or fail output as expected, pinmux tests for BSC data/address, LCDC data/control, IIC, USB, PCC, SCIF0/1, SIOF0/1, TPU, SIM, and MMC functions, and register readback of `P?CR`, `PSELx`, and `P?DR` values after applying representative functions. Debugfs should show the function-GPIO catalogue and correct per-pin mux ownership.
