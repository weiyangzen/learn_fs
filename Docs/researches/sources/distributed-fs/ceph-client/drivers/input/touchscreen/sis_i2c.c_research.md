<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sis_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/sis_i2c.c

## Purpose
`sis_i2c.c` drives SiS 9200-family I2C touch panels. It parses variable-length controller packets, validates CRC for touch reports, handles optional area/pressure/scan-time fields, supports multi-packet reports, and emits up to ten direct multitouch slots.

## Important APIs, Types, And Functions
`struct sis_ts_data` stores the I2C client, input device, optional attention/reset GPIOs, and a 64-byte packet buffer. `sis_read_packet()` receives one maximum-sized packet, validates length, determines report type, verifies CRC for touch packets, adjusts the contact count index for CRC/scan-time fields, and computes contact size from area/pressure flags. `sis_ts_report_contact()` maps controller contact IDs to input slots and reports slot state, X/Y, pressure, and touch major/minor. `sis_ts_handle_packet()` drains one or more packets until all contacts in the report are consumed.

## Control Flow
Probe allocates state, gets optional `attn` and `reset` GPIOs, toggles reset, allocates a `SiS Touchscreen` input device with 4095 X/Y, pressure, and area axes, initializes ten direct MT slots, requests a threaded IRQ, and registers input. On IRQ, the handler repeatedly calls `sis_ts_handle_packet()` while the optional attention GPIO remains asserted. A first packet's contact count becomes the remaining count; later tail packets must report zero contacts in their count field.

## State And Persistence
The driver holds no persistent settings. Packet parsing state is local to `sis_ts_handle_packet()`, and per-contact tracking is maintained by input MT slots keyed by controller contact ID. Optional reset is performed only at probe.

## Dependencies And Integration Points
It uses I2C `i2c_master_recv()`, CRC-ITU-T, GPIO consumer APIs, threaded IRQs, input MT helpers, OF matching (`sis,9200-ts`), and I2C IDs (`sis_i2c_ts`, `9200-ts`).

## Risks
The packet format is dense and variable; bad length/count indices can desynchronize parsing. Tail-packet logic assumes at most five contacts per non-all-in-one packet before continuation. The IRQ loop depends on attention GPIO polarity if present. There is no explicit I2C functionality check and no power-management path. `gpiod_set_value()` is used for reset rather than the cansleep variant, so reset GPIO provider constraints matter.

## Test Signals
Inject or capture packets with CRC errors, HIDI2C report IDs, area/pressure/scantime combinations, and multi-packet ten-contact frames. Validate attention GPIO drain behavior, reset timing, input slot reuse by contact ID, and release packets with status `SIS_STATUS_UP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sis_i2c.c -->
