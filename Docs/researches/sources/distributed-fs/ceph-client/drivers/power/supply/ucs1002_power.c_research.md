# sources/distributed-fs/ceph-client/drivers/power/supply/ucs1002_power.c

## Purpose
`ucs1002_power.c` drives the Microchip/SMSC UCS1002 programmable USB port power controller. It exposes the port as a USB power-supply device and a fixed 5 V VBUS regulator, reporting attachment, delivered charge/current, current limit, USB charging type, and health.

## Important APIs, Types, And Functions
`struct ucs1002_info` holds I2C/regmap state, power-supply pointer, regulator descriptor/device, presence/health state, output-disable flag, and delayed health poll. Property helpers include `ucs1002_get_online()`, `ucs1002_get_charge()`, `ucs1002_get_current()`, `ucs1002_get_max_current()`, `ucs1002_set_max_current()`, `ucs1002_set_usb_type()`, and `ucs1002_get_usb_type()`. IRQ handlers are `ucs1002_charger_irq()` for attach detect and `ucs1002_alert_irq()` for health polling. Regulator operations wrap regmap enable/disable.

## Control Flow
Probe creates an 8-bit regmap, reads DT IRQs `a_det` and `alert`, verifies product ID `0x4e`, enables charge rationing, ignores mode pins and defaults active mode to BC1.2 CDP, sets a safe 500 mA current limit, registers the USB power supply, reads pin status to determine regulator enable polarity, registers the VBUS regulator, initializes health state and delayed work, then requests optional attach and alert IRQs. Property reads pull live register values or cached `present`/`health`; writable properties update current-limit and active USB mode registers.

## State, Persistence, And Dependencies
The chip keeps persistent/current hardware state in general config, switch config, current limit, accumulated charge, and status registers. Driver state caches health, present, and output-disable. It depends on I2C, regmap, OF IRQ naming, regulator framework, power-supply USB type APIs, and delayed work.

## Integration Points
It matches `microchip,ucs1002`. The regulator named `ucs1002-vbus` shares the same switch config register as the power-supply current limit and uses DT regulator constraints. `CURRENT_MAX=0` intentionally disables output logically until a nonzero current limit restores it.

## Risks
`regmap_bulk_read()` reads a `u32` into native memory and then applies `be32_to_cpu`; this assumes regmap bulk byte order and alignment match the charge-register layout. `ucs1002_set_max_current()` disables via `info->rdev` before checking that `rdev` is registered; current probe calls it before regulator registration with nonzero current, but future callers should preserve that ordering. `present` is initialized only by IRQ, not a synchronous probe read. Health polling only reschedules while error state remains bad and relies on alert IRQs to restart.

## Test Signals
Validate product-ID mismatch, default mode/current programming, all current-limit values and rejection of unsupported values, `CURRENT_MAX=0` regulator interaction, USB type set/get mappings, charge/current unit conversions, attach IRQ notification, alert-to-health mapping, missing IRQ operation, and regulator polarity from `F_SEL_PIN`.
