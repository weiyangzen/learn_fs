## sources/distributed-fs/ceph-client/drivers/input/keyboard/lpc32xx-keys.c

Purpose: NXP LPC32xx key scan interface driver for square matrices from 1x1 to 8x8. It uses the SoC scanner hardware and reports changed matrix bits.

Important APIs/types/functions: `struct lpc32xx_kscan_drv` stores input, clock, MMIO base, matrix size, debounce/scan delays, row shift, keymap, and last column states. `lpc32xx_parse_dt()` reads matrix properties and NXP timing properties. `lpc32xx_mod_states()` converts a changed hardware column byte into input events. `lpc32xx_kscan_irq()` scans all columns and clears IRQ.

Control flow: probe parses DT, allocates a keymap, configures input, maps resources, obtains clock, writes scanner debounce/scan/clock/matrix registers with the clock temporarily enabled, requests IRQ, and registers input. Open enables the clock and clears IRQ; close clears IRQ and disables the clock. Suspend/resume mirror clock handling when input is enabled.

State/dependencies/integration: state is lastkeystates and clock state. Dependencies include platform resources, DT `matrix-keypad` properties, `nxp,debounce-delay-ms`, `nxp,scan-delay-ms`, MMIO, clk, PM, and input matrix helpers.

Risks and test signals: only square matrices are accepted. The IRQ handler reads `matrix_sz` columns regardless of sparse keymap content. Test DT validation, key state diffing, clock balance across open/close/suspend/resume, IRQ clear behavior, and 1x1/8x8 limits.
