# sources/distributed-fs/ceph-client/drivers/iio/chemical/mhz19b.c

## Purpose
`mhz19b.c` is a serdev IIO driver for Winsen MH-Z19B CO2 sensors. It exposes raw CO2 concentration and calibration sysfs controls for automatic baseline correction, zero point, and span point.

## Important APIs, Types, And Functions
`struct mhz19b_state` stores the serdev device, completion, receive index, and 9-byte command/response buffer. `mhz19b_get_checksum()` computes the protocol checksum. `mhz19b_serdev_cmd()` builds commands, writes them synchronously, and for read commands waits for a full response and validates checksum. `mhz19b_receive_buf()` appends received bytes and completes when nine bytes are collected. Attribute stores call calibration commands.

## Control Flow
Probe configures serdev at 9600 baud, no flow control, no parity; allocates IIO state; enables `vin`; and registers one CO2 channel. Runtime reads send command `0x86` and wait up to 100 ms. Calibration writes send no-response commands.

## State And Persistence
The receive buffer and completion are volatile. Sensor calibration commands alter device-side calibration state, but the driver does not cache it. No mutex serializes command/response access.

## Dependencies And Integration Points
It uses serdev, completions, regulator enable, unaligned big-endian helpers, IIO sysfs attrs, and OF matching.

## Risks
`mhz19b_receive_buf()` copies `len` bytes without bounding against remaining buffer space, so fragmented or oversized receive chunks can overflow `buf`. Concurrent reads/calibration commands can interleave because there is no lock and completion is not reinitialized before commands. The checksum formula returns two's complement of sum without the common `+1`, which should be verified against the protocol.

## Test Signals
Test fragmented and oversized RX frames, read timeout, checksum validation, concurrent reads, calibration argument bounds, regulator failure, and serial settings.
