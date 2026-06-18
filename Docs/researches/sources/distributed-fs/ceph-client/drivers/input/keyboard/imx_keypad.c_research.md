## sources/distributed-fs/ceph-client/drivers/input/keyboard/imx_keypad.c

Purpose: i.MX keypad-port matrix driver for `fsl,imx21-kpp`. It scans up to an 8x8 hardware matrix and reports key transitions through the input matrix-keypad API.

Important APIs/types/functions: `struct imx_keypad` holds clock, input device, MMIO base, IRQ, debounce timer, enabled flag, row/column masks, keycodes, and stable/unstable column states. Core functions are `imx_keypad_scan_matrix()`, `imx_keypad_check_for_events()`, `imx_keypad_fire_events()`, `imx_keypad_irq_handler()`, `imx_keypad_open()`, and `imx_keypad_close()`.

Control flow: probe builds a matrix keymap, derives enabled row/column masks from non-reserved keys, inhibits hardware until opened, requests IRQ, and enables wakeup. Open enables the clock, configures rows/columns, clears status bits, and enables key-depress interrupts. IRQ disables KDI/KRI and starts a near-term timer. The timer repeatedly scans until three stable readings, reports changed keys with `MSC_SCAN`, then either re-enables key-depress IRQ when all keys are released or polls/re-enables release IRQ while keys remain down.

State/dependencies/integration: runtime state lives in the debounce timer and matrix arrays; hardware state is in KPCR/KPSR/KDDR/KPDR. Dependencies include platform resources, `clk`, MMIO, timers, `matrix_keypad_build_keymap()`, and noirq PM wake handling.

Risks and test signals: scan timing is sensitive to capacitance discharge delays and open-drain sequencing. The open sanity check treats all enabled row lines low as hardware misconfiguration. Test multi-key press/release, debounce stability, clock enable/disable balance, noirq suspend with wake enabled, and matrix masks generated from sparse keymaps.
