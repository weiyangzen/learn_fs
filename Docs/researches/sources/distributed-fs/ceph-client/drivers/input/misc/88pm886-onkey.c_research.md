# sources/distributed-fs/ceph-client/drivers/input/misc/88pm886-onkey.c

## Purpose

This platform driver reports the ONKEY status of Marvell 88PM886 PMICs as a Linux `KEY_POWER` input event. It is a small MFD child driver using the parent chip regmap and IRQ resource.

## Important APIs, Types, and Functions

`struct pm886_onkey` stores the input device and parent chip pointer. `pm886_onkey_irq_handler()` reads `PM886_REG_STATUS1`, masks `PM886_ONKEY_STS1`, reports the power key state, and syncs. `pm886_onkey_probe()` allocates state/input, gets the platform IRQ, sets input identity/capability, requests a threaded IRQ with `IRQF_ONESHOT | IRQF_NO_SUSPEND`, registers input, and exposes platform ID matching.

## Control Flow

Probe is invoked for platform ID `88pm886-onkey`. It obtains the parent `pm886_chip`, configures an input device, attaches an IRQ handler, and registers input. Interrupt flow reads current PMIC status rather than relying on edge direction, so both press and release depend on the PMIC status bit at handler time.

## State and Persistence Behavior

No key state is cached in software; PMIC status is sampled on each IRQ. Resources are devm-managed. `IRQF_NO_SUSPEND` keeps IRQ delivery active during suspend, but there are no explicit local PM hooks.

## Dependencies and Integration Points

It depends on the 88PM886 MFD parent, regmap, platform IRQ resources, input power-key events, and platform device ID matching.

## Risks and Edge Cases

The driver does not call `device_init_wakeup()` or `enable_irq_wake()`, so suspend wake behavior must be provided by parent IRQ configuration despite `IRQF_NO_SUSPEND`. Status read errors return `IRQ_NONE`, which may affect shared interrupt accounting. Long-press or reset-related PMIC features are not configured here.

## Test Signals

Test platform ID autoload, IRQ retrieval failures, regmap read failures, press/release status sampling, suspend IRQ behavior, input registration failure, and parent MFD teardown.
