# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_zt5550.h

## Purpose
Defines the ZT5550 CompactPCI host-controller register offsets and bit masks used by `cpcihp_zt5550.c`. It is the hardware register contract for direct CSRs, indexed host-controller CSRs, interrupt masks, and the legacy ENUM# input port.

## Important APIs, Types, and Functions
There are no functions or types. Direct register offsets include `CSR_HCINDEX`, `CSR_HCDATA`, `CSR_INTSTAT`, `CSR_INTMASK`, counter command/count registers, and direct interrupt masks such as `ENUM_INT_MASK` and `ALL_DIRECT_INTS_MASK`. Indexed-register selectors include `HC_INT_MASK_REG`, `HC_STATUS_REG`, `HC_CMD_REG`, arbiter/isolation/fault/watchdog/diagnostic/serial registers, and `ALL_INDEXED_INTS_MASK`. `ENUM_PORT` and `ENUM_MASK` define the digital I/O source for ENUM#.

## Control Flow
The header has no runtime control flow. The C file writes `HC_INT_MASK_REG` via the index/data pair to mask indexed interrupts, writes `CSR_INTMASK` to mask or unmask direct ENUM interrupts, reads `CSR_INTSTAT` in the shared IRQ checker, and reads `ENUM_PORT` via `inb_p()` to answer core ENUM queries.

## State and Persistence Behavior
These constants encode hardware state locations. Changing them changes which MMIO bytes and I/O port the driver reads/writes. The header itself stores no state and has no persistence.

## Dependencies and Integration Points
Integrated only by the ZT5550 driver and indirectly by the generic cPCI hotplug core through the driver's operations. Values are tied to the ZT5550 HC data sheet and to the Linux PCI/I/O accessors used in the C implementation.

## Risks
The register ABI is brittle: wrong offsets or masks can leave interrupts enabled, disable required events, or read the wrong ENUM# state. `ENUM_PORT` is a fixed legacy I/O port and can conflict with platform assumptions if reused outside the intended board.

## Test Signals
Compile coverage of `cpcihp_zt5550.c`, MMIO traces showing expected writes to `HC_INT_MASK_REG` and `CSR_INTMASK`, ENUM# reads changing with hardware events, IRQ masking/unmasking behavior, and no I/O port conflicts during module init are the main signals.
