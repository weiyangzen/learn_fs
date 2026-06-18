## sources/distributed-fs/ceph-client/drivers/input/keyboard/nspire-keypad.c

Purpose: TI-Nspire keypad MMIO driver. It configures continuous hardware scanning over an 8x11 matrix and reports changed bits.

Important APIs/types/functions: `struct nspire_keypad` stores register base, interrupt mask, input, clock, row shift, scan/row delays, cached row state, and active-low flag. `nspire_keypad_open()` programs scan timing and enables interrupts. `nspire_keypad_irq()` reads data rows, applies polarity, diffs state, and reports transitions.

Control flow: probe reads required `scan-interval` and `row-delay` DT properties, gets clock and MMIO, disables/acks keypad and unknown GPIO interrupts with the clock temporarily enabled, builds keymap, requests IRQ, and registers input. Open enables clock and continuous scanning; close masks/acks interrupts and disables clock. IRQ validates status, copies 8 row words from data registers, reports changed row/column bits, syncs, and acknowledges interrupt bits.

State/dependencies/integration: state is cached row bitmasks and hardware scan registers. Dependencies include OF properties, MMIO, clock, input matrix helpers, IRQ, and platform resources.

Risks and test signals: delay-cycle calculations warn but mask overflow, so invalid timing can silently truncate. The debug print swaps row_delay and scan_interval arguments. Test active-low polarity, timing property bounds, open/close clock balance, unknown interrupt disable, row/column map coverage, and spurious IRQ returning `IRQ_NONE`.
