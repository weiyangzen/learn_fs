
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-ocores.h

## Purpose
This header defines platform data for the OpenCores I2C controller driver.

## Important APIs And Types
`struct ocores_i2c_platform_data` includes register shift, register I/O width, input clock in kHz, target bus clock in kHz, big-endian register flag, number of attached board devices, and pointer to an `i2c_board_info` array.

## Control Flow, State, And Persistence
No executable flow is included. The driver consumes this data to map register offsets/widths, compute timing divisors, configure endian-aware accessors, register the adapter, and instantiate listed I2C devices. Runtime state is controller registers and I2C adapter/device registration.

## Dependencies And Integration Points
It integrates OpenCores I2C platform devices with Linux I2C core, board-info device instantiation, and MMIO accessor selection.

## Risks And Test Signals
Risks include incorrect register shift or I/O width, clock mismatch causing wrong bus speed, endian mismatch, and stale device list lengths. Test signals include adapter registration, measured bus frequency, transfers to board-info devices, endian/access-width variants, and error handling for NAK/arbitration paths.
