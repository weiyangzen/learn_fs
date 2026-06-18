# sources/distributed-fs/ceph-client/drivers/hid/hid-kysona.c

## Purpose

`hid-kysona.c` adds support for Kysona M600 and VXE Dragonfly mouse battery reporting. It periodically sends vendor output reports requesting online and battery information, parses matching raw input reports, and exposes the data through a `power_supply` device while leaving normal HID input connected.

## Important APIs, Types, and Functions

- `struct kysona_drvdata`: per-device state with HID pointer, online flag, power-supply descriptor/device, capacity, charging flag, voltage, and delayed work.
- `kysona_battery_get_property(...)`: reports status, present, capacity, scope, model name, voltage, and online state.
- `kysona_m600_fetch_online(...)` / `kysona_m600_fetch_battery(...)`: allocate request buffers and send fixed output reports through `hid_hw_raw_request`.
- `kysona_battery_timer_tick(...)`: periodic polling worker that requests online and battery reports every five seconds.
- `kysona_battery_probe(...)`: initializes defaults, registers the power supply, does initial fetches, and schedules polling.
- `kysona_probe(...)`: validates USB transport, allocates state, parses/starts HID, and only registers battery support on USB interface number 1.
- `kysona_raw_event(...)`: parses fixed-size online and battery reports, updating cached power data.
- `kysona_remove(...)`: cancels battery work if registered and stops HID hardware.

## Control Flow

Probe requires a USB HID device, stores devres-managed state, parses the descriptor, and starts with `HID_CONNECT_DEFAULT`. For interface 1 it registers a battery power supply and starts polling. Each timer tick sends online and battery request reports, then reschedules itself. When the device replies, `raw_event` identifies reports by size, report id, and second byte, then updates `online`, capacity, charging, and voltage fields.

## State and Persistence Behavior

Battery state is cached in `kysona_drvdata` and exposed via power-supply reads. Defaults are capacity 100 and voltage 4200 mV until reports arrive. Polling persists through delayed work until remove cancels it. There is no explicit `power_supply_changed()` call after raw updates, so userspace may observe updates by polling properties rather than receiving immediate change notifications.

## Dependencies and Integration Points

The driver depends on USB HID parent interfaces, HID raw requests/events, delayed work, devres allocation, and power-supply APIs. It matches Kysona and VXE USB IDs and delegates regular mouse input to the generic HID stack.

## Risks and Edge Cases

- Battery support is hard-wired to USB interface number 1; changed interface layouts will skip power support.
- Request and response formats are fixed 17-byte packets with magic trailing bytes.
- `kysona_probe` logs a stale `ret` value if `kysona_battery_probe` fails because it does not assign the call result.
- Raw-event updates do not notify the power-supply core, which can delay userspace visibility.
- The driver rejects non-USB transport even if future devices expose the same protocol elsewhere.
- Polling every five seconds creates recurring output reports; suspend/resume behavior is not explicitly handled.

## Test Signals

Hardware tests should verify interface 1 creates `kysona-*-battery`, capacity/online/charging/voltage update after reports, normal mouse input still works, and remove cancels polling cleanly. Negative tests should cover short raw requests, malformed reports, non-interface-1 devices, non-USB matches, and unplug during delayed work.
