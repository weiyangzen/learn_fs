# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max14577.c

## Purpose
`extcon-max14577.c` supports the MUIC block in Maxim MAX14577 and MAX77836 devices, reporting USB, charger, and jig extcon states and switching internal USB/UART paths.

## Important APIs, types, and functions
`struct max14577_muic_info` stores parent MFD state, extcon, previous ADC/charger classifications, status bytes, IRQ metadata, coalescing flags, work items, mutex, and default USB/UART paths. Core helpers are `max14577_muic_get_cable_type()`, `max14577_muic_set_path()`, `max14577_muic_adc_handler()`, `max14577_muic_chg_handler()`, `max14577_muic_irq_handler()`, `max14577_muic_irq_work()`, and `max14577_muic_detect_accessory()`.

## Control flow
Probe chooses the IRQ list for MAX14577 or MAX77836, maps nested regmap IRQs to virqs, requests each threaded IRQ, registers the extcon device, sets default USB/UART paths, reads initial status to route UART jig early, reads revision, sets ADC debounce, and queues delayed cable detection after boot. Nested IRQ handlers only classify whether ADC and/or charger work is needed, then schedule work. Work reads two MUIC status registers under a mutex and invokes ADC and charger handlers. ADC handling supports jig USB/UART cables and logs unsupported accessories. Charger handling reports USB SDP, DCP, CDP, special slow/fast chargers, and path switching for USB.

## State and persistence behavior
State is runtime-only: cached previous ADC and charger type allows detach reporting when hardware returns open/none, while status bytes are refreshed per event. Hardware control registers hold path and debounce configuration.

## Dependencies and integration points
It depends on the MAX14577 MFD/regmap/irq-domain support, extcon provider APIs, workqueues, mutexes, and platform/OF IDs for both MAX14577 and MAX77836 MUIC variants.

## Risks and edge cases
Delayed detection uses a long default 17 second delay to wait for platform boot. Unsupported ADC accessories return `-EAGAIN` and only log. IRQ coalescing uses boolean flags, so repeated events before work runs collapse into one status read. Correct detach reporting depends on previous type caches. MAX77836 has extra IRQs and must use the right parser.

## Test signals
Test MAX14577 and MAX77836 IRQ mapping, USB/JIG/DCP/CDP/slow/fast charger attach/detach, UART jig early path setup, delayed boot detection, simultaneous ADC and charger IRQs, unsupported ADC accessories, and regmap failure paths.
