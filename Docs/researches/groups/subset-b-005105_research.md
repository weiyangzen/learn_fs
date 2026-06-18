# Research: subset-b-005105

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7269.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7269.c

## Purpose
This file is the Renesas SH7269 pin function controller descriptor for the shared SuperH/R-Mobile `sh_pfc` pinctrl driver. It contains no platform probe code of its own; instead it exports `sh7269_pinmux_info`, a static `struct sh_pfc_soc_info` that tells the common driver which pins exist, which GPIO and alternate-function states are legal, and which MMIO registers control mode, direction, and data for the SH7269 ports.

## Important APIs, Types, And Functions
The large top-level `enum` defines the PFC vocabulary: data tokens for ports A, B, C, D, E, F, G, H, and J; input/output tokens; mode tokens such as `PB22MD_000`; and function marks such as IRQ/PINT, SD/MMC, PWM, IEBus, watchdog, DMAC, ADC, BSC, TMU, SCIF, RSPI, IIC, SSI/SIOF/SPDIF, NAND, CAN, VDC, and LCD signals. `pinmux_data[]` maps each legal mark to the mode bits and, for GPIOs, direction/data states accepted by the core. `pinmux_pins[]` exposes GPIO pins with `PINMUX_GPIO()`, deliberately skipping port I and not exposing port H as normal GPIO pins because the source notes that port H lacks a data register. `pinmux_func_gpios[]` publishes legacy function-GPIO names through `GPIO_FN()`. `pinmux_config_regs[]` describes 16-bit `P?CR` mode registers and `P?IOR` direction registers under `0xfffe38xx`/`0xfffe39xx`; `pinmux_data_regs[]` describes `P?DR` data registers. The exported `sh7269_pinmux_info` connects all of those arrays to the common driver and includes `FORCE_IN`/`FORCE_OUT` fallback tokens for direction selection.

## Control Flow
Board or SoC setup registers this SoC info with the shared `sh_pfc` implementation. When a consumer requests a GPIO or function, the common driver searches `pinmux_data[]` for a valid combination, then uses `pinmux_config_regs[]` to program the relevant mode and direction fields. GPIO value reads/writes are routed through `pinmux_data_regs[]`. There are no file-local callbacks; all runtime control flow is table-driven after `sh7269_pinmux_info` is selected.

## State And Persistence
The file's state is immutable descriptor data. Runtime state, locking, GPIO registration, and MMIO access live in the common `sh_pfc` core. Hardware state persists in SH7269 PFC registers until reset or later pinctrl/GPIO changes. Mode registers encode alternate-function selection, I/O registers encode input/output direction, and data registers encode GPIO levels. Port H is a special risk area because the enum contains PH data/function tokens, but the descriptor excludes PH data registers and normal GPIO pins to match the hardware limitation.

## Dependencies And Integration Points
It depends on `<cpu/sh7269.h>` for pin IDs and register context plus `sh_pfc.h` for the PFC table macros and data contracts. It integrates with the Renesas/SuperH pinctrl core, gpiolib through exported `PINMUX_GPIO()` pins, and legacy function-GPIO users through `GPIO_FN()` names. Peripheral integration covers external bus and memory pins, SD/MMC, SCIF ports 0-7, CAN routes, IIC channels, RSPI, timers/PWM, DMA request/acknowledge, SSI/SIOF/SPDIF audio, NAND, digital video input, and LCD data/control routes on both PG and PJ pin banks.

## Risks
The main risk is table accuracy: every `PINMUX_DATA()` entry must match the hardware manual's mode field, or the shared driver will program the wrong alternate function without compile-time detection. Several entries combine multiple peripheral choices on one mode value or reuse marks across banks, such as LCD and digital-video pins on PG/PJ, so copy/paste errors are easy to miss. `PINMUX_CFG_REG_VAR()` field widths and reserved gaps must stay aligned with 16-bit register layouts. Port H has nonstandard data behavior and port I is absent; treating either as ordinary GPIO would expose unusable lines. There is no explicit IRQ map in this file, so interrupt routing depends on function selection plus external INTC/platform configuration.

## Test Signals
Useful signals include successful SH7269 PFC registration, expected GPIO count excluding port H and port I, debugfs pinmux listings showing function-GPIO names, GPIO direction/value tests on representative ports A/B/C/D/F/G/J, pinctrl application for SCIF, SD/MMC, CAN, IIC, RSPI, audio, LCD/VDC, and BSC routes, and register readback of `P?CR`, `P?IOR`, and `P?DR` fields after mux and GPIO operations. Hardware tests should include alternate pins for shared functions such as LCD data on PG vs PJ and CAN/IRQ routes on PC/PJ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7269.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh73a0.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh73a0.c

## Purpose
This file describes the Renesas SH73A0 PFC hardware block for the shared `sh_pfc` driver. It is more than a simple pin table: besides port/function/register metadata, it exposes generic pinctrl groups and functions, GPIO-to-IRQ mappings, pin bias hooks, and a small regulator used to control SDHI0 VCCQ MC0 through a PFC-related register bit.

## Important APIs, Types, And Functions
`CPU_ALL_PORT()` and `CPU_ALL_NOGP()` provide the SoC-specific port range expansion used by the generic macros in `sh_pfc.h`; the non-GPIO pin is `A11` at ball `F26`. The enum defines `PORT0` through `PORT309` data/input/output/function tokens, `MSEL2CR`, `MSEL3CR`, and `MSEL4CR` selector tokens, and many function marks from the hardware manual. `pinmux_data[]` starts with `PINMUX_DATA_ALL()` for GPIO mode and then maps function marks to `PORTx_FNy` states plus extra MSEL constraints where required. `pinmux_pins[]` uses SH73A0-specific helpers to attach input/output and pull-up/pull-down capabilities to each pin. `pinmux_groups[]` and `pinmux_functions[]` expose modern pinctrl groups/functions for BSC, FSI, I2C, IrDA, keyscan, LCD/LCD2, MMC0, MSIOF, SCIFA/SCIFB, SDHI, TPU, and USB. `pinmux_config_regs[]` lists per-port `PORTxCR` registers and MSEL registers; `pinmux_data_regs[]` groups 32-bit data registers by port ranges. `pinmux_irqs[]` maps IRQ0-IRQ31 to one or more GPIO-capable port numbers.

The file also defines the VCCQ MC0 regulator path: `sh73a0_vccq_mc0_endisable()` updates bit 28 at `pfc->windows[1].virt + 4` under `pfc->lock`; the regulator ops wrap enable, disable, is-enabled, and fixed 3.3 V voltage reporting. `sh73a0_pin_to_portcr()` translates a pin number to a PORTCR offset using `sh73a0_portcr_offsets[]`. `sh73a0_pinmux_soc_init()` registers the `vccq_mc0` regulator, and `sh73a0_pfc_ops` wires init plus `rmobile_pinmux_get_bias()`/`rmobile_pinmux_set_bias()` into the common driver.

## Control Flow
The common PFC driver selects `sh73a0_pinmux_info`, calls `.ops->init`, and registers the VCCQ MC0 regulator with consumers named `vqmmc` for `sh_mobile_sdhi.0` and `ee100000.sdhi`. Pinctrl group selection then resolves a named group/function pair to the relevant pins and mux marks, and the common driver programs `PORTxCR` and any required MSEL bits. GPIO value access uses the range-based data register table. Bias configuration routes through the R-Mobile helper callbacks after translating the logical pin to its port control register offset. GPIO IRQ setup uses `pinmux_irqs[]` to associate external IRQ numbers with candidate GPIO pins.

## State And Persistence
Most state is static table data. Mutable state is in `struct sh_pfc`, the regulator core, and the hardware registers. The VCCQ regulator mutates one hardware bit under the same spinlock used by the PFC core, so regulator changes and pinmux register updates are serialized at the PFC level. Pin mux, data, pull, and MSEL state persist in MMIO registers until reset or later reconfiguration. The regulator exposes only enable/disable status and fixed voltage, not dynamic voltage selection.

## Dependencies And Integration Points
The file depends on Linux MMIO, module, generic pinconf, regulator, slab, and `sh_pfc.h` APIs. It integrates with device-tree or board pinctrl consumers through named groups and functions rather than only legacy `GPIO_FN()` names. Major consumer domains include BSC/NAND-style external bus pins, FSI audio, I2C2/I2C3, IrDA, keyscan, LCD and LCD2, MMC0, MSIOF0-3, SCIFA0-7, SCIFB, SDHI0-2, TPU timers, USB VBUS, GPIO interrupts, and SDHI voltage signaling through the regulator.

## Risks
SH73A0 has dense positional tables. A wrong group-to-mux array pair, `SH_PFC_FUNCTION()` membership list, or MSEL dependency can produce a valid-looking but electrically wrong pin state. MSEL bits are shared global selectors, so one function choice can affect routes outside the local port field. The VCCQ regulator assumes `pfc->windows[1]` is present and that bit 28 at offset `+4` is the SDHI0 VCCQ control; an incorrect resource layout would turn regulator operations into unrelated MMIO writes. Bias support depends on `sh73a0_pin_to_portcr()` staying consistent with the non-contiguous port ranges generated by `CPU_ALL_PORT()`. IRQ9 maps to two candidate pins, so tests must cover the intended board route.

## Test Signals
Expected signals include successful probe and regulator registration, visible `vccq_mc0` supply for SDHI0, correct pinctrl groups/functions in debugfs, GPIO direction/value tests across several port ranges, pull-up/pull-down pinconf tests on pins with advertised bias capability, SDHI0 operation with VCCQ enable/disable, group apply tests for BSC, LCD/LCD2, MSIOF, SCIFA/SCIFB, SDHI, I2C, keyscan, TPU, and USB, IRQ tests for all mapped external IRQs including the dual-pin IRQ9 route, and register readback of `PORTxCR`, MSEL2/3/4, and data registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh73a0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7720.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pfc-sh7720.c -->
