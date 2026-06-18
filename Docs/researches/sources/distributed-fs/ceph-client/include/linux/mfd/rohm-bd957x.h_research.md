# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd957x.h

## Purpose

This 140-line header defines the ROHM BD957x/BD9576 PMIC regulator IDs, interrupt topology, watchdog, regulator trigger, voltage tuning, and fault threshold registers. It is mainly consumed by MFD, regulator, watchdog, and interrupt child drivers.

## Important APIs, Types, and Functions

It exports regulator IDs `BD957X_VD50` through `BD957X_VOUTS1`, top-level BD9576 IRQ IDs, `IRQS_SILENT_MS`, main and sub interrupt register addresses/masks, valid masks for under/over-voltage detection, watchdog config, power trigger registers, regulator enable/disable values, tune registers, OVD/UVD threshold registers, over-current warning/protection registers, and `BD957X_MAX_REGISTER`.

## Control Flow

No code executes here. The long comment describes expected IRQ flow: regmap-irq handles only the main status register, while sub-drivers inspect fine-grained fault status and may disable an IRQ briefly before delayed re-enable to avoid loops from level-asserted fault lines.

## State and Persistence Behavior

Runtime state is stored in PMIC status, mask, watchdog, trigger, and voltage registers. Interrupt state can persist while a hardware fault remains present, so sub-device handlers must acknowledge and clear the condition before enabling the line again.

## Dependencies and Integration Points

The header depends on common kernel bit macros and is integrated with regmap IRQ handling, regulator fault reporting, watchdog configuration, and power sequencing for BD957x platforms.

## Risks and Edge Cases

Fine-grained IRQs are only partly maskable and the hardware line remains asserted until the physical condition clears. Incorrect mask values can create interrupt storms or hide voltage/thermal faults. Tune and threshold masks differ by rail width.

## Test Signals

Build tests for BD957x MFD/regulator/watchdog drivers, interrupt storm regression tests for thermal/fault IRQs, regmap mask assertions for each fault class, and hardware fault-injection or lab tests that verify delayed IRQ re-enable behavior.
