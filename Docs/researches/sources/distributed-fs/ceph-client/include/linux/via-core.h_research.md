# sources/distributed-fs/ceph-client/include/linux/via-core.h

## Purpose
This header defines shared VIA framebuffer/core structures, port configuration, power-management hooks, interrupt helpers, and register/bit constants.

## Important APIs, types, and functions
Key enums are `via_port_type`, `via_port_mode`, and `viafb_i2c_adap`. Important types are `via_port_cfg`, `viafb_pm_hooks`, and `viafb_dev`. APIs include `viafb_pm_register()`, `viafb_pm_unregister()`, `viafb_irq_enable()`, and `viafb_irq_disable()`. It also defines interrupt status/mask bits and MMIO helpers/state fields.

## Control flow, state, and persistence
VIA subdrivers share `viafb_dev` for PCI device, MMIO base, engine state, I2C adapters, port configuration, spinlocks, and PM hooks. Interrupt helpers modify video interrupt masks; PM hooks let subcomponents suspend/resume. State is runtime device and display configuration.

## Dependencies and integration points
It depends on types, IO, spinlocks, and PCI. It integrates VIA framebuffer, I2C, display output, capture, and power management code.

## Risks and test signals
Risks include shared MMIO lock misuse, stale PM hook pointers, wrong interrupt mask bits, and inconsistent port configuration. Tests should cover subdriver registration, IRQ enable/disable, suspend/resume callbacks, I2C adapter lookup, and register access under lock.
