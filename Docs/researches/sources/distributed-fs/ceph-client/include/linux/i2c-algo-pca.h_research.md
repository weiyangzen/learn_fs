# sources/distributed-fs/ceph-client/include/linux/i2c-algo-pca.h

## Purpose
Defines the algorithm interface and register constants for NXP PCA9564/PCA9665 I2C bus controller adapters.

## APIs, Control Flow, and State
The header exposes chip IDs, PCA9564 clock constants, direct/indirect register offsets, control bits, and PCA9665 bus modes. `struct pca_i2c_bus_settings` records derived mode, low/high SCL periods, and clock frequency. `struct i2c_algo_pca_data` supplies low-level byte read/write, wait, reset callbacks, selected clock, chip type, and bus settings. `i2c_pca_add_bus()` and `i2c_pca_add_numbered_bus()` attach the algorithm to adapters. State persists in adapter `algo_data` and hardware registers.

## Dependencies, Integration, Risks, and Tests
Depends on I2C core structures supplied by including translation units. Integrates with platform drivers wrapping PCA9564/PCA9665 register access. Risks include wrong oscillator assumptions, unsupported clock selection, wait callback timeouts, reset ordering, and mixing direct PCA9564 registers with PCA9665 indirect registers. Test signals include controller probe, selected bus frequency validation, transfer completion interrupts/polling, timeout recovery, and register access tracing.
