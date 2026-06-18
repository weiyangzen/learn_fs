# sources/distributed-fs/ceph-client/drivers/power/supply/max8903_charger.c

Purpose: implements a GPIO-driven MAX8903 USB/adapter charger driver. It registers one power supply whose type changes between mains, USB, and battery depending on DC/USB input GPIO state, and reports status/online/health from charger and fault pins.

Important APIs/types/functions: `struct max8903_data` stores all GPIO descriptors, live `usb_in`/`ta_in`/`fault` state, and the mutable `power_supply_desc`. `max8903_setup_gpios()` acquires optional and required GPIOs, sets initial CEN/DCM output levels, and samples initial input state. IRQ handlers `max8903_dcin()`, `max8903_usbin()`, and `max8903_fault()` update state on GPIO edges. `max8903_get_property()` exposes status, online, and health.

Control flow: probe allocates state, sets up GPIOs, initializes the supply descriptor type from sampled input state, registers the power supply, and requests threaded edge IRQs for DC, USB, and fault pins when present. DC/USB IRQs update input booleans, enable/disable the charger via CEN depending on remaining power sources, switch DCM for DC preference, update the descriptor type, and call `power_supply_changed()` if type changes. Fault IRQ updates the health flag.

State and persistence: all state is runtime GPIO state plus output lines driven by the driver. There is no register persistence. The descriptor type is mutated after registration to reflect the active source.

Dependencies and integration: depends on gpiod descriptors, IRQs from GPIOs, OF compatible `maxim,max8903`, and power-supply core. Correct GPIO polarity flags in firmware are central to behavior.

Risks: `cen` is acquired unconditionally even though the comment says CEN is compulsory only when DOK is present, so USB-only designs still need a CEN GPIO. Fault changes do not call `power_supply_changed()`, so health updates may not notify userspace. Mutating `psy_desc.type` at runtime is unusual and can surprise consumers caching type. Test signals include DC-only/USB-only/both-present DTs, GPIO active-low polarity, CEN/DCM output behavior during plug/unplug, fault health notifications, and initial-state detection before IRQs fire.
