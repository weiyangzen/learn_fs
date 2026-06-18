# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hif.h

## Purpose
`hif.h` defines the host interface abstraction for ath11k. It lets core, HAL, HTC, CE, debug, power-management, and bus-independent code call bus-specific operations through `ab->hif.ops`.

## Important APIs, types, and data
`struct ath11k_hif_ops` is the core vtable. It contains operations for register read/write, memory range read, IRQ and CE IRQ control, start/stop, power up/down, suspend/resume, HTC service-to-pipe mapping, MSI vector/address lookup, CE MSI index lookup, and coredump download.

Inline wrappers dispatch to the vtable and provide optional fallbacks for absent operations such as power up/down, suspend/resume, memory read, MSI helpers, and coredump download.

## Control flow
Most wrappers directly dispatch to `ab->hif.ops`. Optional operations either no-op or return `-EOPNOTSUPP`; suspend/resume default to success when absent. Core boot/shutdown, HAL register programming, HTC service connection, debugfs, and coredump code all pass through this abstraction.

## State and persistence behavior
This header owns no state. It routes calls through `struct ath11k_base`, whose HIF ops and bus-private state persist for the device lifetime. Side effects are register access, IRQ state, power state, MSI configuration, and coredump transfer.

## Dependencies and integration points
It includes `core.h` and expects `ab->hif.ops` to be initialized before wrappers are used. PCI and AHB backends populate concrete ops. HAL uses read/write wrappers; HTC uses service-to-pipe mapping; core and WoW paths use power/IRQ/suspend/resume wrappers.

## Risks
Mandatory wrappers do not null-check all operations. Optional fallbacks can hide missing bus behavior until runtime. Register wrappers provide no synchronization. Incorrect service-to-pipe mapping breaks HTC/WMI/HTT traffic.

## Test signals
Boot on each bus, firmware start, HTC target ready, WMI/HTT pipe mapping, interrupts/MSI, suspend/resume, debugfs memory reads, coredump download, and clean shutdown are the main signals.
