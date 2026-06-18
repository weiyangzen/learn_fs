# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max3355.c

## Purpose
`extcon-max3355.c` supports Maxim MAX3355 USB OTG role detection using GPIOs. It reports USB host vs simulated USB peripheral state through extcon.

## Important APIs, types, and functions
`struct max3355_data` stores the extcon device, ID GPIO, and shutdown GPIO. `max3355_id_irq()` reads the ID pin and updates `EXTCON_USB_HOST` and `EXTCON_USB`. Probe gets GPIOs, registers extcon, requests a both-edge threaded IRQ, and performs initial detection. Remove drives shutdown low.

## Control flow
Probe requests `"id"` as input and `"maxim,shdn"` as output high, registers extcon cables for USB and USB_HOST, maps the ID GPIO to IRQ, requests a no-suspend both-edge IRQ, stores driver data, and calls the IRQ handler once. The handler treats ID high as host detached and simulates USB peripheral attached; ID low clears USB peripheral and reports USB host.

## State and persistence behavior
Runtime state is entirely GPIO and extcon state. Shutdown GPIO level changes at probe/remove; no persistent state exists.

## Dependencies and integration points
It depends on GPIO descriptors, platform devices, OF match `maxim,max3355`, IRQs, and extcon provider APIs.

## Risks and edge cases
Because the chip only exposes ID role, the driver simulates peripheral attach when host is absent; this may be wrong if nothing is connected. IRQ is marked `IRQF_NO_SUSPEND`, so it can run during suspend. Shutdown GPIO polarity/configuration must match board wiring.

## Test signals
Test ID high/low transitions, initial state, shutdown GPIO on remove, GPIO-to-IRQ failure, suspend behavior, and consumer reaction to simulated USB peripheral state.
