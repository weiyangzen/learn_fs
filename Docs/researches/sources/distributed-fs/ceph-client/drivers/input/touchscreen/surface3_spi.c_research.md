<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/surface3_spi.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/surface3_spi.c

## Purpose
`surface3_spi.c` drives N-trig/Microsoft Surface 3 touch and pen reports over SPI. It creates two input devices, one direct multitouch touchscreen and one pen device with pen/rubber/stylus state, then decodes fixed-size interrupt-driven SPI packets.

## Important APIs, Types, And Functions
`struct surface3_ts_data` stores the SPI device, two reset GPIO descriptors, touch and pen input devices, current pen tool, and a cacheline-aligned 264-byte read buffer. Packed report structures represent finger and pen payloads. `surface3_spi_read()` reads a full packet. `surface3_spi_process()` checks the static header and dispatches by report type (`0xd2` touch, `0x16` pen). `surface3_spi_report_touch()` uses tracking IDs as MT slot keys; `surface3_spi_report_pen()` reports proximity, touch, stylus, rubber/pen tool switching, X/Y, and pressure.

## Control Flow
Probe configures SPI mode 0 and 8 bits/word, allocates state, gets two indexed reset/power GPIOs, toggles power true/false/true, registers touch and pen input devices with fixed Surface 3 coordinate ranges/resolutions, and requests a threaded IRQ. Each IRQ reads one full packet and parses it. Touch processing starts at byte 17 and scans up to 13 finger records until a status end marker. Pen processing reads a pen record at byte 15 and syncs the pen input device.

## State And Persistence
The driver holds only runtime state: reset GPIOs, current pen tool, and input slots. Power is controlled by two GPIOs. Suspend disables IRQ and powers off; resume powers on and enables IRQ. There is no firmware upload or sysfs state.

## Dependencies And Integration Points
It integrates with SPI core, ACPI matching (`MSHW0037`), GPIO consumer APIs, threaded IRQs, input MT, and simple sleep PM. It sets Microsoft vendor/product IDs manually on the input devices.

## Risks
The header mismatch path logs an error but does not return, so a packet with a bad header is still dispatched by `data[9]`. Fixed offsets and coordinate ranges are hardware-specific. `input_report_key(dev, BTN_TOUCH, st & 0x12)` passes a bitmask rather than a normalized boolean, relying on input core boolean semantics. Tool switching fakes proximity-out to change between pen and rubber.

## Test Signals
Test touch and pen report packets, header-corrupt packets, up to ten touch slots despite scanning 13 records, pen/rubber switching, suspend/resume GPIO sequencing, IRQ storm behavior, and ACPI enumeration on Surface 3 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/surface3_spi.c -->
