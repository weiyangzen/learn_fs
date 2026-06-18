# sources/distributed-fs/ceph-client/drivers/power/supply/goldfish_battery.c

Purpose: exposes the Goldfish emulator battery and AC adapter MMIO interface as Linux power supplies named `battery` and `ac`.

Important APIs/types/functions: `struct goldfish_battery_data` holds the MMIO base, IRQ, spinlock, and two power supplies. Register offsets define interrupt status/enable and all battery/AC properties. `goldfish_ac_get_property()` and `goldfish_battery_get_property()` read MMIO registers directly. `goldfish_battery_interrupt()` handles status-change interrupts.

Control flow: probe maps the platform MMIO resource, gets the IRQ, registers AC and battery supplies, requests a shared IRQ, then enables battery and AC interrupt bits. Property reads perform `readl()` from the corresponding emulator register. The IRQ handler takes a spinlock, reads and masks interrupt status, calls `power_supply_changed()` for battery and/or AC, and returns handled only when a known bit was set.

State and persistence: state is emulator-owned MMIO. The driver caches only pointers and has no writable properties or persistent storage.

Dependencies and integration: depends on platform resources, OF compatible `google,goldfish-battery`, ACPI ID `GFSH0001`, MMIO accessors, shared IRQ registration, and power-supply core registration.

Risks and test signals: property values are trusted exactly as emulator registers provide them, so unit/enumeration correctness depends on the virtual device contract. Test MMIO mapping failures, missing IRQ, AC and battery property reads, interrupt status clearing, simultaneous battery/AC events, shared IRQ `IRQ_NONE` behavior, OF and ACPI matching, and that interrupt enable is written after supplies are registered.
