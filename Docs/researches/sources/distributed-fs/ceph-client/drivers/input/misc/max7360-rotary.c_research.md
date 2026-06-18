# sources/distributed-fs/ceph-client/drivers/input/misc/max7360-rotary.c

Purpose: MAX7360 MFD child driver that reports rotary encoder movement as relative or absolute input events.

Important APIs/types/functions: parent regmap, `fwnode_irq_get_byname`, input ABS/REL, threaded shared IRQs, and wake IRQ helpers. `struct max7360_rotary` stores input, regmap, debounce, position, steps, axis, relative mode, and rollover. Main routines are report, IRQ, hardware init, probe, and remove.

Control flow: probe gets parent regmap and named `inti` IRQ, reads parent rotary properties, validates debounce, configures input, requests IRQ, registers input, writes rotary configuration, and enables wakeup. IRQ reads rotary counter, ignores zero, sign-extends the 8-bit count, reports REL steps or updates/clamps/rolls ABS position, and syncs.

State/persistence: absolute position is RAM-only. Debounce/interrupt configuration is written once at probe. Remove clears wake IRQ and wakeup.

Dependencies/integration: MAX7360 parent MFD, parent firmware-node properties, generic rotary encoder bindings, input axes.

Risks: ABS max is set to `steps` while reported positions are `0..steps-1`. Input registration precedes hardware init. Shared IRQ returns `IRQ_NONE` on zero/read error.

Test signals: relative/absolute modes, rollover/clamp, negative counts, debounce bounds, missing regmap/IRQ, wake setup, and zero counter handling.
