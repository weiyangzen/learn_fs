# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-i2c.c

## Purpose
`cx88-i2c.c` provides the primary bit-banged I2C adapter for Conexant cx2388x/cx88 cards. It exposes the chip's internal I2C pins through Linux `i2c-algo-bit` so tuner, demodulator, EEPROM, audio, RTC, and IR helper drivers can be discovered and controlled by the rest of the cx88 media stack.

## Important APIs, Types, And Functions
The module parameters are `i2c_debug`, `i2c_scan`, and `i2c_udelay`; the last is clamped to at least 5 usec before adapter registration. The low-level callbacks `cx8800_bit_setscl()`, `cx8800_bit_setsda()`, `cx8800_bit_getscl()`, and `cx8800_bit_getsda()` manipulate `MO_I2C` through `core->i2c_state`. `cx8800_i2c_algo_template` packages those callbacks for `i2c_bit_add_bus()`. `do_i2c_scan()` probes all 7-bit addresses and prints known device hints from `i2c_devs`. The exported initializer is `cx88_i2c_init()`.

## Control Flow
Initialization copies the algorithm template into `core->i2c_algo`, wires `core->i2c_adap` to the PCI device and V4L2 device, creates a synthetic `core->i2c_client`, drives SCL/SDA high, and calls `i2c_bit_add_bus()`. If registration succeeds, selected Hauppauge HVR boards receive a four-byte transfer to the analog/digital tuner at address `0xc2 >> 1` to enable the analog demodulator. Optional scan mode then performs zero-length reads for diagnostic discovery.

## State, Persistence, And Dependencies
The lasting state is in `struct cx88_core`: adapter/client objects, `i2c_algo`, `i2c_state`, and `i2c_rc`. There is no persistent storage; bus state is hardware register state. The file depends on `cx88.h` register helpers, `MO_I2C`, Linux I2C core, `i2c-algo-bit`, PCI parent device lifetime, and V4L2 adapter data.

## Integration Points
This adapter is created by cx88 core setup before board-specific subdevices are attached. Other files use `core->i2c_rc` to skip I2C work on registration failure, and use `core->i2c_adap` for V4L2 I2C subdevice creation, IR receiver probing, WM8775/tvaudio probing, and tuner/demodulator access.

## Risks
The bit state cache must remain synchronized with `MO_I2C`; direct register writes elsewhere could confuse subsequent bit operations. Too-low `i2c_udelay` is guarded, but high bus capacitance or board wiring may still need slower timing. `do_i2c_scan()` is diagnostic only and may produce side effects on fragile devices. The Hauppauge tuner write is board-specific magic and lacks transfer result handling.

## Test Signals
Useful signals are successful `i2c_bit_add_bus()` registration, visible tuner/EEPROM subdevice probes, `i2c_scan=1` output on known cards, verified HVR analog tuner enablement, no I2C timeout regressions at default delay, and clean failure behavior when the adapter cannot register.
