<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.h -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.h

## Purpose
`irq-riscv-imsic-state.h` defines the internal IMSIC state model and function contract shared by the early and platform IMSIC drivers.

## Important APIs, Types, and Functions
It defines `IMSIC_IPI_ID`, `IMSIC_NR_IPI`, `struct imsic_vector`, `struct imsic_local_priv`, and `struct imsic_priv`. It declares global `imsic_noipi` and `imsic`, EIx update helpers, local sync/delivery, vector mask/unmask/move/allocation/free/debug APIs, CPU online/offline hooks, `imsic_setup_state()`, and `imsic_irqdomain_init()`.

## Control Flow
The header has no runtime flow, but it separates the early handler/IPI path from MSI-domain allocation. Early code initializes state and local delivery; platform code allocates vectors and composes MSI messages through this interface.

## State and Persistence
`struct imsic_vector` is the unit of MSI identity allocation and migration. `struct imsic_local_priv` keeps local lock, dirty bitmap, optional synchronization timer, and vector table. `struct imsic_priv` holds firmware identity, global hardware config, per-CPU state, matrix allocator, and base domain pointer.

## Dependencies and Integration Points
The contract depends on RISC-V IMSIC public definitions, irqdomain, fwnode, timers, seq_file debug output when enabled, and Linux per-CPU/matrix infrastructure in the implementation.

## Risks and Edge Cases
Callers must obey locking expectations around vector enable and move fields. `imsic_vector_get_move()` returns `move_prev`, so users need to distinguish old and new vector roles. IPI ID reservation depends on `imsic_noipi`.

## Test Signals
Compile coverage with SMP, non-SMP, debugfs, ACPI, and DT configurations is key. Runtime validation comes through IMSIC early/platform tests for vector lifecycle, CPU hotplug, IPI reservation, and affinity migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-state.h -->
