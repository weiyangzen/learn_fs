# sources/distributed-fs/ceph-client/drivers/power/supply/tps65090-charger.c

## Purpose
`tps65090-charger.c` is the TPS65090 charger child driver. It exposes AC presence as `tps65090-ac`, configures PMIC charger registers, optionally enables low-current charging, and handles VAC presence either by IRQ or by a fallback polling kthread.

## Important APIs, Types, And Functions
`struct tps65090_charger` stores parent device, online state, IRQ or poll task, passive-mode flag, power-supply pointer, and platform data. Register helpers from `linux/mfd/tps65090.h` are used by `tps65090_low_chrg_current()`, `tps65090_enable_charging()`, and `tps65090_config_charger()`. `tps65090_charger_isr()` is both the threaded IRQ handler and polling body. DT parsing recognizes `ti,enable-low-current-chrg`.

## Control Flow
Probe obtains parent platform data or DT-derived charger data, allocates state, registers the mains supply, gets an optional IRQ, configures charger registers unless in passive mode, checks initial charger status, enables charging when status indicates presence, and either requests a threaded IRQ or starts `ktps65090charger`. The ISR reads charger status, waits 75 ms, reads interrupt status, sets `ac_online`, enables charging when VACG is set, clears interrupts in active mode, and notifies userspace on online transitions. Remove stops the poll thread when no IRQ was available.

## State, Persistence, And Dependencies
Runtime state is `ac_online`, `prev_ac_online`, `passive_mode`, IRQ id, and optional kthread. Persistent hardware state includes charger-enable, low-current/no-termination, interrupt-mask, and interrupt-status registers. The driver depends on the TPS65090 MFD parent, platform data from the parent cell, optional OF child data, kthreads/freezer, and power-supply class.

## Integration Points
It is registered as platform driver `tps65090-charger` and matches `ti,tps65090-charger`. The parent MFD supplies the register accessors and likely the IRQ resource. `supplied_to` and fwnode metadata come from platform data/firmware.

## Risks
When no IRQ is present, `passive_mode` is set only after `tps65090_config_charger()` and initial status handling, so early register writes still occur even though later polling runs passive. `tps65090_charger_isr()` reads `CG_STATUS1` but uses only `INTR_STS` to decide VAC state; polling with no IRQ may misinterpret sticky interrupt status. `prev_ac_online` is updated only on property read and ISR entry paths, so notifications can be tied to userspace read timing. The ISR sleeps, so it must remain threaded or kthread-only.

## Test Signals
Validate platform-data and DT probes, low-current register programming, initial status detection, IRQ and no-IRQ polling paths, freezer behavior, transition notifications, interrupt clearing, and remove-time kthread shutdown. Hardware tests should include AC plug/unplug with both sticky and cleared interrupt statuses.
