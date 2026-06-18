# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5592r-base.h

## Purpose
`ad5592r-base.h` defines the common contract shared by the AD5592R SPI wrapper, AD5593R I2C wrapper, and the base mixed-signal driver. It centralizes register IDs, control-bit definitions, transport operations, shared driver state, and exported probe/remove prototypes.

## Important APIs, Types, And Functions
- `enum ad5592r_registers` defines common register addresses, including DAC/ADC enable, GPIO, pull-down, powerdown, LDAC, tristate, and reset registers.
- `AD5592R_REG_PD_EN_REF`, `AD5592R_REG_CTRL_ADC_RANGE`, and `AD5592R_REG_CTRL_DAC_RANGE` define shared control bits.
- `struct ad5592r_rw_ops` is the bus abstraction with callbacks for DAC write, ADC read, generic register read/write, and GPIO read.
- `struct ad5592r_state` is the shared private state used by base and transport code, including IIO/GPIO state, caches, channel modes, and DMA-aligned SPI buffers.
- `ad5592r_probe()` and `ad5592r_remove()` are declared for bus drivers.

## Control Flow
This header does not execute logic. Its main control-flow role is shaping how bus wrappers call into `ad5592r_probe()` with an operations table and how the base driver calls back into SPI/I2C-specific register functions.

## State And Persistence
The declared `ad5592r_state` persists cached DAC values, cached control register, channel modes/off-states, GPIO direction/value maps, regulator pointer, and synchronization primitives. It also contains SPI-specific buffers even though the base is bus-neutral, allowing the SPI wrapper to reuse the common allocation.

## Dependencies And Integration Points
The header depends on Linux types, cache alignment, mutexes, gpiolib, and IIO. It is included by `ad5592r-base.c`, `ad5592r.c`, and `ad5593r.c`, and its exported namespace is declared by the C files rather than in the header.

## Risks And Edge Cases
- The state structure is shared by transport and base logic, so layout changes can break both buses.
- Bus-neutral code contains SPI transfer buffers; future non-SPI expansion should avoid assuming those buffers are meaningful.
- GPIO and IIO caches are byte-sized, which matches the eight-channel hardware but should be revisited if support for variants with different channel counts is added.

## Test Signals
Compile coverage for both SPI and I2C wrappers is important after any signature or state changes. Tests should validate that every callback in `ad5592r_rw_ops` is provided before probe and that channel count assumptions remain eight-wide.
