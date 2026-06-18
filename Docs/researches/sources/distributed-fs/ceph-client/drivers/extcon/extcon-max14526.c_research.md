# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max14526.c

## Purpose
`extcon-max14526.c` supports the Maxim MAX14526 MUIC over I2C, reporting USB device, USB host, fast charger, and MHL extcon states while programming MUIC switch paths.

## Important APIs, types, and functions
`struct max14526_data` stores the I2C client, extcon device, regmap, regmap fields, last raw state, and current cable. `max14526_ap_usb_mode()` programs D+/D- to USB and enables charge pump/ADC. `max14526_interrupt()` delays for MUIC status stabilization, reads interrupt status, maps raw state to extcon cable, and updates state. Probe sets up regmap fields, verifies vendor ID, registers extcon, configures USB mode, enables interrupts, and triggers initial detection with `irq_wake_thread()`.

## Control flow
On IRQ, the handler sleeps 100 ms, reads `MAX14526_INT_STAT`, ignores duplicate state, clears the previous extcon cable, switches on composite status values such as USB, charger, OTG, MHL, or none, then sets the new extcon cable and records `last_state`. Resume wakes the IRQ thread to refresh state.

## State and persistence behavior
The driver keeps `last_state` and current cable in memory, and writes MUIC control registers for switch path and detection. There is no persistent storage.

## Dependencies and integration points
It depends on I2C, regmap/regmap fields, extcon provider APIs, threaded IRQs, and OF/I2C IDs for `maxim,max14526`.

## Risks and edge cases
The vendor-ID mismatch path calls `dev_err_probe()` but does not return, so unsupported IDs continue probing. `dev_err_probe(dev, (IS_ERR(priv->edev)), ...)` passes a boolean instead of the real error code on extcon allocation failure. Raw state matching relies on enum values ORed with status bits; unexpected bit combinations map to `EXTCON_NONE`.

## Test signals
Verify ID/revision detection, USB/charger/OTG/MHL/no-cable state mapping, duplicate IRQ suppression, initial IRQ thread wake, resume refresh, regmap read/write failures, and unsupported vendor ID behavior.
