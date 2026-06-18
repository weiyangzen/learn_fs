# sources/distributed-fs/ceph-client/drivers/hid/hid-steelseries.c

Purpose: supports SteelSeries SRW-S1 wheel and Arctis 1/9 wireless headsets. SRW-S1 gets a replacement descriptor and LED class devices for RPM LEDs; Arctis headsets get power_supply battery reporting, wireless status updates, and periodic battery queries.

Important APIs/types/functions: `struct steelseries_device` tracks headset HID device, quirks, delayed battery work, removal flag, power_supply descriptor, capacity, connection, and charging state. `struct steelseries_srws1_data` tracks SRW-S1 LED state and LED classdevs. Key callbacks include `steelseries_probe`, `steelseries_remove`, `steelseries_srws1_report_fixup`, and `steelseries_headset_raw_event`. Helpers cover SRW-S1 LED output reports and Arctis battery request/parsing.

Control flow: SRW-S1 report fixup replaces the descriptor when a known byte pattern is seen, exposing hidden dials under Generic Desktop usages. SRW-S1 probe validates output report values, starts HID, initializes all LEDs off, then registers one "all" LED and 15 individual RPM LEDs; brightness writes update a bitmask and send an output report. Headset probe parses HID, validates Arctis 9 vendor usage page, starts and opens hardware, registers a battery power_supply, sends an initial query, and schedules retries for Arctis 9. Raw events parse Arctis 1/9 formats, update connection/capacity/charging, call `power_supply_changed()`, set USB wireless status, and schedule the next query unless removed.

State and persistence: SRW-S1 LED bitmask persists in driver data and hardware until changed. Headset state persists capacity, connection, charging, delayed-work status, and a `removed` flag protected by spinlock. Power_supply names are allocated per headset instance.

Dependencies/integration: depends on HID raw requests, HID output reports, LED class, power_supply, USB wireless status, delayed work, and SteelSeries IDs. Arctis support assumes USB transport for wireless-status integration.

Risks: SRW-S1 LED report assumes the first output report has at least 16 values; probe validates this before use. LED state updates are not separately locked, so concurrent sysfs LED writes could interleave. Headset raw parsing is model-specific; malformed events can keep scheduling battery requests. `hid_hw_open()` failure after `hid_hw_start()` returns without stopping hardware in probe, which is a cleanup-risk pattern. Battery capacity mapping for Arctis 9 is empirical.

Test signals: SRW-S1 descriptor should show dials as RX/RZ-style desktop axes and all 16 LED class devices should control hardware; Arctis 1 should report connected status and raw capacity from matching response; Arctis 9 should map raw capacity and charging status; unplug/remove should cancel delayed work and stop rescheduling; power_supply properties should update on raw events.
