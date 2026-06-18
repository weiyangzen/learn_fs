# sources/distributed-fs/ceph-client/include/linux/bcma/bcma.h

## Purpose
Defines the Broadcom AMBA (BCMA) bus core model: host operations, core/device IDs, bus/device structures, driver registration, MMIO access wrappers, core lookup, host hooks, and core power/IRQ/DMA helpers.

## Important APIs, types, and functions
- `enum bcma_hosttype`, `struct bcma_chipinfo`, `struct bcma_boardinfo`, and `enum bcma_clkmode` describe bus host and clock context.
- `struct bcma_host_ops` abstracts 8/16/32-bit register access, optional block I/O, and agent register access.
- `struct bcma_device` models a discovered core with device identity, MMIO addresses, wrapper address, IRQ, core index/unit, driver data, and list linkage.
- `struct bcma_driver` is the BCMA driver binding object with probe/remove/suspend/resume/shutdown callbacks and `module_bcma_driver()` helper.
- `struct bcma_bus` aggregates host info, chip/board info, core list, mapped core, and embedded driver state for chipcommon, PCI/PCIe2, MIPS, GMAC common, and shared SPROM.
- Inline accessors wrap host ops and read/modify/write helpers.

## Control flow and state
Host code registers a BCMA bus, enumerates cores into `bus->cores`, and binds `bcma_driver` instances through the device model. Drivers call `bcma_read*()`/`bcma_write*()` on their core, use `bcma_find_core()` for companion cores, and manage core enable/disable, clock mode, PLL, DMA translation, and IRQ mapping through exported helpers.

## State and persistence behavior
BCMA state is runtime bus enumeration and MMIO/device state. Shared SPROM reflects persistent board calibration but is cached in the bus object. Core power and clock changes affect hardware state immediately.

## Dependencies and integration points
Depends on PCI, module device tables, BCMA driver-specific headers, SSB SPROM sharing, and common BCMA registers. Integrated by Broadcom wireless, ethernet, PCI host/endpoint, SoC, and platform drivers.

## Risks
Register accessors assume `bus->ops` is valid and mapped to the current core. Read/modify/write helpers are not inherently locked, so shared registers need caller-side serialization. Core IDs and chip IDs are ABI-like constants for driver matching. Host-specific stubs return `-ENOTSUPP` only for PCI host IRQ control on PCI hosts.

## Test signals
Probe on PCI and SoC hosts, enumerate multiple core units, bind/unbind BCMA drivers, exercise register access wrappers, core enable/disable, IRQ mapping, SPROM fallback, and DMA translation for known chips.
