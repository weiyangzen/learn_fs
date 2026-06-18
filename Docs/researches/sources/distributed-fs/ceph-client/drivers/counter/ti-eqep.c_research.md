# sources/distributed-fs/ceph-client/drivers/counter/ti-eqep.c

Purpose: TI Enhanced Quadrature Encoder Pulse counter driver, exposing one position counter with quadrature, pulse-direction, increase, and decrease modes plus overflow/underflow/direction-change events.

Important APIs/types/functions: `struct ti_eqep_cnt` holds separate 32-bit and 16-bit regmaps because the hardware register file changes width. Counter callbacks implement count read/write, function read/write, action read, event mask configuration, watch validation, ceiling, enable, and direction. IRQ handler `ti_eqep_irq_handler()` maps QFLG bits to Generic Counter events.

Control flow: probe maps MMIO, initializes 32-bit regmap at the base and 16-bit regmap at base + 0x24, requests a threaded IRQ, fills counter metadata, enables runtime PM and the clock, and registers with plain `counter_add()`. Function writes update QDECCTL.QSRC. Action reads derive counted edges from QSRC, signal ID, and XCR. `events_configure()` builds QEINT from active watches; ISR reads QFLG, pushes overflow/underflow/direction-change on channel 0, and writes QCLR.

State and persistence: hardware registers hold position, max, control, interrupt enable/flags, and direction. Driver holds only regmap pointers. Runtime PM is enabled at probe and disabled in remove; no suspend context is implemented here.

Dependencies and integration: uses platform MMIO, regmap, runtime PM, clock framework, OF compatibles `ti,am3352-eqep` and `ti,am62-eqep`, Generic Counter, and char-device event infrastructure.

Risks: probe uses non-devm `counter_add()` and manual remove; errors after `pm_runtime_get_sync()` and clock enable must unwind correctly. Runtime PM get result is ignored. No mutex serializes multi-register operations, though most writes are single regmap operations. Events are global channel 0 only.

Test signals: probe/remove balance runtime PM and counter unregister, count write rejected above `QPOSMAX`, all four function modes map to QDECCTL.QSRC, action reports for XCR and signal combinations, enable toggles QEPCTL.PHEN, ceiling range checks, QEINT mask changes from watches, and IRQ flags produce userspace events then clear.
