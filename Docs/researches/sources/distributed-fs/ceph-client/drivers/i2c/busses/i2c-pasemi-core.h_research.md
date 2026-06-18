# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-core.h

## Purpose
Defines the PA Semi SMBus shared state and exported entry points for glue drivers.

## Important APIs, Types, And Functions
`PASEMI_HW_REV_PCI` marks original PCI controllers that lack a hardware revision register. `struct pasemi_smbus` contains the parent device, I2C adapter, MMIO base, clock divisor, hardware revision, IRQ mode flag, and IRQ completion. `pasemi_i2c_common_probe()` and `pasemi_irq_handler()` are declared for shared use.

## Control Flow
This header has no standalone runtime flow. Glue drivers allocate/fill `struct pasemi_smbus`, then call `pasemi_i2c_common_probe()`; IRQ-capable glue can route interrupts to `pasemi_irq_handler()`.

## State And Persistence
It defines in-memory state only. Adapter registration and controller state are managed by the core implementation using this struct.

## Dependencies And Integration Points
Includes Linux atomic, clock, I2C, SMBus alert, IO, device, completion, and kernel headers. It is included by the shared core and PCI wrapper.

## Risks
Glue must initialize `dev`, `ioaddr`, `clk_div`, and `hw_rev` correctly before common probe. If `use_irq` is set without a requested IRQ and handler, transfers may wait forever until timeout. The header does not enforce ownership or lifecycle rules.

## Test Signals
Compile tests for all glue users, probe tests confirming initialized fields, IRQ handler linkage if IRQ mode is enabled, and static analysis for missing `ioaddr` or invalid clock divisors.
