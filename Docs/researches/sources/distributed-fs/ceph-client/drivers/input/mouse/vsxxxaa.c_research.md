<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vsxxxaa.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/vsxxxaa.c

## Purpose
`vsxxxaa.c` is a serio RS232 driver for DEC VSXXX-AA/GA mice and VSXXX-AB tablets. It buffers serial bytes, resynchronizes packet streams, decodes relative mouse, absolute tablet, and power-on-reset packets, and reports Linux input events.

## Important APIs, Types, and Functions
`struct vsxxxaa` stores the input device, serio port, 15-byte buffer, detected version/country/type, and name/phys strings. Buffer helpers are `vsxxxaa_queue_byte()`, `vsxxxaa_drop_bytes()`, and `vsxxxaa_check_packet()`. Packet handlers are `vsxxxaa_handle_REL_packet()`, `vsxxxaa_handle_ABS_packet()`, and `vsxxxaa_handle_POR_packet()`. Driver lifecycle uses `vsxxxaa_connect()`, `vsxxxaa_interrupt()`, `vsxxxaa_disconnect()`, and `module_serio_driver()`.

## Control Flow
Connect allocates state and input device, advertises key/relative/absolute capabilities, opens the serio port, sends `T` to request self-test, and registers input. Every incoming byte is queued and `vsxxxaa_parse_buffer()` repeatedly drops non-header bytes, checks whether a known packet type and length are available, validates that continuation bytes are not headers, handles complete packets, and drops stray bytes when a broken packet is detected. POR packets identify the device and then force standard format, incremental streaming, and a 72 samples/sec rate by writing `S`, `R`, and `L`.

## State and Persistence
The byte buffer preserves partial packets across interrupts. Device identity fields are updated after POR/self-test. There is no persistent configuration outside the live serio session; mode/rate commands are reissued after POR.

## Dependencies and Integration Points
The driver integrates with serio RS232 device matching (`SERIO_VSXXXAA`), Linux input, and module serio registration. It exposes both relative mouse and absolute tablet capabilities on one input device.

## Risks and Edge Cases
Serial streams can lose sync, so the parser aggressively drops bytes and logs errors. `vsxxxaa_drop_bytes()` uses `BUFLEN - num` in `memmove`, which copies more than the remaining valid byte count but stays inside the fixed buffer; correctness depends on `count` being adjusted afterward. Hardware mode forcing uses `mdelay()` in packet handling after POR, which can stall processing. The adapter/power requirements described in comments are unusual and hardware failures may look like protocol noise.

## Test Signals
Test relative packets, absolute tablet packets, POR/self-test identification, hot-plug recovery, broken-packet resynchronization, and disconnect during active serial traffic. `evtest` should show three buttons, `BTN_TOUCH`, `REL_X/Y`, and `ABS_X/Y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/vsxxxaa.c -->
