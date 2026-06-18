
# sources/distributed-fs/ceph-client/include/linux/platform_data/i2c-mux-reg.h

## Purpose
This header defines platform data for an I2C mux selected by writing a memory-mapped register.

## Important APIs And Types
`struct i2c_mux_reg_platform_data` contains parent and base adapter numbers, per-channel register values, channel count, endian flag, write-only flag, optional idle value and `idle_in_use`, MMIO register pointer, and register size.

## Control Flow, State, And Persistence
The mux driver selects a bus by writing one value to the mapped register, using endian and width information; if configured it writes idle value after use. If `write_only` is set, it must not attempt read-modify-write or verification reads. State is current hardware mux register value.

## Dependencies And Integration Points
It integrates I2C mux core, platform MMIO resources, and board-specific register mux hardware.

## Risks And Test Signals
Risks include wrong register size/endian, unsafe reads from write-only hardware, invalid MMIO pointer lifetime, and idle value selecting an active conflicting bus. Test signals include child adapter transfers, register write tracing, big/little-endian selection, write-only mode, idle behavior, and invalid channel handling.
