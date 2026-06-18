# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn66xx_device.h

## Purpose
This header declares CN6XXX/CN66XX LiquidIO chip state, PCIe MPS/MRRS enums, and common helper APIs shared by CN66XX and CN68XX implementations.

## Important APIs, Types, And Functions
`struct octeon_cn6xxx` stores interrupt summary/enable pointers, interrupt mask, configuration pointer, and a spinlock protecting DROQ interrupt-enable register access. `enum octeon_pcie_mps` and `enum octeon_pcie_mrrs` define PCIe payload/read-request settings. Function declarations cover reset, error reporting, PCIe tuning, global/queue setup, queue enable/disable, interrupt processing, BAR1, read-index updates, register binding, clock/tick conversion, CN66XX setup, and configuration validation.

## Control Flow
Chip setup files include this header to install common function pointers into `octeon_device`. CN68XX reuses most CN6XXX helpers while overriding reset and device-register setup.

## State And Persistence
The header defines in-memory chip state and function contracts only. Register pointers map BAR0; no persistent storage is involved.

## Dependencies And Integration Points
It depends on LiquidIO core types such as `octeon_device`, `octeon_config`, `octeon_instr_queue`, and `octeon_reg_list`, plus kernel IRQ and spinlock types from included compilation units.

## Risks
The common structure is used for multiple chip variants, so variant-specific fields must not be silently added without all setup paths initializing them. The MPS/MRRS enums use `-1` for default, so callers must pass the enum type and not unsigned storage.

## Test Signals
Compile CN66XX and CN68XX users, verify all declared functions are defined once in the core object, and test PCIe enum default and explicit values through setup paths.
