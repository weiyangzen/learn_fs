## sources/distributed-fs/ceph-client/drivers/input/keyboard/omap4-keypad.c

Purpose: OMAP4/OMAP5 keypad controller driver. It reads hardware full-code registers, reports matrix transitions, and uses runtime PM to handle auto-idle and wake.

Important APIs/types/functions: `struct omap4_keypad` stores input, base, IRQ, scan mutex, dimensions, revision offsets, row shift, no-autorepeat flag, cached key bitmap, keymap, and function clock. `omap4_keypad_scan_keys()` diffs bitmaps and reports releases before presses. `omap4_keypad_irq_thread_fn()` reads full-code registers. `omap4_keypad_runtime_suspend()` works around erratum i689 by clearing stuck releases after idle.

Control flow: probe enables runtime PM, reads revision to choose register offsets, stops hardware interrupts, allocates input/keymap, requests threaded IRQ, registers input, and sets wake IRQ. Open resumes runtime PM, enables clock, programs control/debounce/IRQ/wakeup registers, and enables IRQ. IRQ top half wakes the thread only if IRQSTATUS is nonzero; thread resumes device, reads low/high key bitmaps, scans changes, clears pending IRQs, and autosuspends. Close disables IRQs and clock.

State/dependencies/integration: state is cached 64-bit key bitmap, runtime PM state, hardware registers, and wake IRQ registration. Dependencies include OF matrix properties, clock, MMIO, input core, threaded IRQ, runtime PM, and PM wakeirq.

Risks and test signals: erratum handling relies on runtime suspend seeing an idle state machine before forcing all keys up. Revision offset handling must be correct for OMAP4 vs OMAP5. Test missed key-up recovery, runtime PM autosuspend, open/close clock balance, wake IRQ setup, no-autorepeat property, and unsupported revision rejection.
