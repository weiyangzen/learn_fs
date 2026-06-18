# sources/distributed-fs/ceph-client/drivers/input/keyboard/goldfish_events.c

## Purpose

`goldfish_events.c` is the Goldfish emulator event-device driver. It imports an emulator-provided input device name, capability bitmaps, and ABS parameters from MMIO pages, then forwards triples of input events read from the device on IRQ.

## Important APIs, Types, and Functions

- Page/register constants define `REG_READ`, `REG_SET_PAGE`, `REG_LEN`, `REG_DATA`, `PAGE_NAME`, `PAGE_EVBITS`, and `PAGE_ABSDATA`.
- `struct event_dev` stores input device, IRQ, MMIO base, and flexible device name.
- `events_import_bits()` reads capability bitmaps from emulator pages into input bit arrays.
- `events_import_abs_params()` reads ABS min/max/fuzz/flat values.
- `events_interrupt()` reads type/code/value triples and emits `input_event()` plus sync.
- `events_probe()` maps MMIO, imports metadata/capabilities, requests IRQ, and registers input.

## Control Flow

Probe obtains IRQ and memory resource, maps 4 KiB, selects the name page to size/copy the device name, allocates input/state, imports capability pages for all major input event bitmaps, imports ABS params for enabled ABS codes, requests IRQ, and registers the input device. Each interrupt reads three consecutive MMIO words and forwards them directly to the input core.

## State and Persistence Behavior

The driver stores static imported capabilities and name in the input device. It does not track event state beyond what input core tracks. The emulator device controls all event values and page contents.

## Dependencies and Integration Points

It depends on platform bus, OF compatible `google,goldfish-events-keypad`, ACPI ID `GFSH0002`, MMIO raw access, IRQs, and Linux input. It is intended for Android/Goldfish virtual hardware.

## Risks and Edge Cases

MMIO-provided lengths are trusted enough to allocate/copy a name and import bitmap bytes; very large name lengths could inflate allocation. Events are forwarded without validating type/code against imported capabilities. Raw accessors assume emulator endian/order. Missing resources fail probe.

## Test Signals

Validate imported capabilities, ABS parameter ranges, name handling, IRQ event forwarding for key/rel/abs/sw/msc/led/snd/ff bits, malformed length pages, out-of-capability event triples, and OF/ACPI matching in emulator boots.
