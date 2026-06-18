# sources/distributed-fs/ceph-client/drivers/input/keyboard/cypress-sf.c

## Purpose

`cypress-sf.c` is an I2C driver for Cypress StreetFighter touchkey controllers. It powers the controller with two regulators, reads a button status register on IRQ, and reports configured keycodes.

## Important APIs, Types, and Functions

- `struct cypress_sf_data` stores the I2C client, input device, `vdd`/`avdd` regulators, keycode array, last keystate bitmap, and key count.
- `cypress_sf_irq_handler()` reads `CYPRESS_SF_REG_BUTTON_STATUS`, diffs against previous state, reports changed keys, syncs, and stores new state.
- `cypress_sf_probe()` reads optional `linux,keycodes`, applies defaults, enables regulators, registers input, and requests a threaded IRQ.
- Suspend/resume disable IRQ around regulator power-down/up.

## Control Flow

Probe allocates state, gets regulators, determines key count from `linux,keycodes` or defaults to two, reads keycodes or uses Back/Menu defaults, enables supplies with a devm cleanup action, registers input capabilities, then requests an IRQ thread. On interrupt, the thread reads one byte over SMBus, diffs the configured number of key bits, reports only changed states, and syncs.

## State and Persistence Behavior

`keystates` persists the last status byte for change detection. Regulators remain enabled while active and are disabled during suspend and devm cleanup. No nonvolatile state is used.

## Dependencies and Integration Points

It depends on I2C SMBus byte reads, regulator bulk APIs, input core, threaded IRQs, PM sleep ops, and OF compatible `cypress,sf3155`. The main firmware contract is `linux,keycodes`.

## Risks and Edge Cases

The status register is one byte, so more than eight configured keys would not be representable despite the dynamic key count. If reading keycodes fails for a count greater than two, only the first two defaults are initialized. IRQ is disabled before regulator shutdown, but wakeup behavior is not implemented. A negative SMBus read returns `IRQ_NONE`, which may matter for shared IRQ diagnostics.

## Test Signals

Test default and custom keycodes, key counts from one to eight, SMBus read failures, regulator get/enable/disable failures, suspend/resume IRQ ordering, repeated interrupts with unchanged state, and OF/I2C matching.
