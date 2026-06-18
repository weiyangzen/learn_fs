# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-octeon-core.h

## Purpose
Defines the shared OCTEON TWSI register model, status constants, `struct octeon_i2c`, inline MMIO accessors, chip-identification helper, and exported function prototypes used by OCTEON I2C glue drivers.

## Important APIs, Types, And Functions
`struct octeon_i2c_reg_offset` abstracts register layout differences. `struct octeon_i2c` carries adapter, clock, IRQs, MMIO, frequency, feature flags, callback hooks, atomic IRQ enable counters, and SMBus alert fields. Inline helpers implement indirect core register access through `SW_TWSI`, TWSI interrupt register access, and write flushing. Prototypes expose ISR, transfer, low-level init, clock setup, and recovery info.

## Control Flow
The header does not execute standalone control flow, but it shapes all core operations. Indirect register reads/writes set `SW_TWSI_V`, poll until hardware clears it, and optionally signal `-EIO` on read timeout. Glue code fills register offsets and interrupt callbacks before invoking the shared core.

## State And Persistence
The header defines in-memory and MMIO state only. Atomic counters are used by glue drivers to balance IRQ enable/disable calls on hardware where interrupts are explicitly enabled via Linux IRQ lines. No persistent storage is involved.

## Dependencies And Integration Points
Includes Linux atomic, bitfield, clk, I2C, SMBus alert, PCI, and raw IO facilities. `octeon_i2c_is_otx2()` inspects PCI subsystem bits for OcteonTX2-specific clock programming. `octeon_i2c_recovery_info` integrates with the Linux I2C bus recovery framework.

## Risks
The inline indirect accessors use bounded spin loops and silently return from writes when hardware never clears `SW_TWSI_V`, making caller-side status checks important. Register-offset macros assume glue initialized all used offsets. Raw 64-bit MMIO and endianness must match the platform. The struct includes both platform and PCI-oriented fields, so glue must initialize only valid combinations.

## Test Signals
Compile coverage from both platform and any PCI glue, static analysis for initialized offsets/callbacks, recovery callback use, timeout paths in indirect reads, OcteonTX2 detection, and IRQ counter balancing on CN7890-style dual-interrupt hardware.
