# sources/distributed-fs/ceph-client/drivers/media/rc/winbond-cir.c

Purpose: PNP driver for Winbond WPCD376I consumer IR hardware. It supports raw IR receive, transmit, carrier reporting, LED feedback, and shutdown/suspend wake-on-CIR matching for NEC/RC5/RC6-family protocols.

Important APIs and functions: `struct wbcir_data` stores resource bases, IRQ mask, rc device, LED, RX/TX state, carrier-report state, TX buffer/cursor/mask/carrier, and lock. Major functions include bank/register helpers, `wbcir_irq_handler`, RX/TX interrupt handlers, `wbcir_idle_rx`, carrier report, TX carrier/mask/send callbacks, wake pattern `wbcir_shutdown`, `wbcir_init_hw`, PNP probe/remove, and suspend/resume.

Control flow: probe validates three PNP I/O regions and IRQ, registers LED and raw rc device, claims regions/IRQ, enables wake, and initializes hardware. RX IRQ drains run-length encoded FIFO bytes into raw pulse/space events and tracks pulse duration for carrier reports. TX converts durations to 10 us units and fills the hardware FIFO incrementally from interrupt context until end-of-transmission. Shutdown/suspend translates the configured wake scancode and mask into hardware compare/mask bytes, enables CEIR wake matching when valid, then disables runtime IRQs.

State and persistence: volatile driver state is in `wbcir_data`; hardware register state spans wake, enhanced, and serial-port register banks. Wake filter settings live in `rc_dev` and are programmed into wake registers on shutdown/suspend; they are not stored on disk.

Dependencies and integration points: depends on PNP resources, port I/O, IRQs, LED class, bit reversal helpers, rc-core raw RX/TX, and rc-core wake filter sysfs. Default keymap is `RC_MAP_RC6_MCE`.

Risks and edge cases: `wbcir_irq_tx` contains a duplicated `kfree(data->txbuf)` in this snapshot, which is a serious double-free risk when transmission finishes. `wbcir_suspend` has a duplicate `return 0`, harmless but untidy. Wake RC6_6A_20 appears referenced inside a case group that does not include it, making that branch unreachable. TX/RX sharing depends on `txandrx` and interrupt masking; changing it can cause underruns or RX loss. Direct port I/O requires exact PNP resources.

Test signals: PNP probe on WEC1022, RX event decoding, carrier report accuracy, TX send completion and underrun handling, KASAN/slab validation for TX completion double-free, LED feedback, wake filter programming for NEC/RC5/RC6, suspend/resume, shutdown wake from S-state, and remove cleanup of regions/IRQ.
