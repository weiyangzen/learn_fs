<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpiosxf.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpiosxf.h

## Purpose
`acpiosxf.h` declares the ACPICA OS Services Layer (OSL): the callbacks and services the host OS must provide so the OS-independent ACPICA core can initialize, map tables, allocate memory, synchronize, schedule work, access I/O and PCI config space, install interrupts, print diagnostics, and interact with debugger/table-provider facilities.

## Important APIs, types, and functions
Important types and constants include `acpi_execute_type`, `ACPI_NO_UNIT_LIMIT`, `ACPI_MUTEX_SEM`, `ACPI_SIGNAL_FATAL`, `ACPI_SIGNAL_BREAKPOINT`, and `struct acpi_signal_fatal_info`. Function groups include initialization (`acpi_os_initialize`, `acpi_os_terminate`), table override/discovery, spinlocks and raw spinlocks, semaphores, mutexes, allocation and cache APIs, physical memory mapping, interrupt handler install/remove, thread/work execution (`acpi_os_execute`, `acpi_os_wait_events_complete`), sleep/stall, port/memory/PCI access, pointer readability/writability, timers, sleep entry, formatted output, debugger command hooks, trace points, table lookup by name/index/address, and directory iteration for tools.

## Control flow
ACPICA calls into these functions whenever it needs host services. Initialization asks the OS for the root pointer and table overrides, table management maps/unmaps physical memory, event code installs interrupt handlers and schedules notify/GPE work, interpreter synchronization uses OSL locks/semaphores/mutexes, and hardware access paths use OSL port/memory/PCI functions. `ACPI_USE_ALTERNATE_PROTOTYPE_*` allows an environment to substitute prototypes.

## State and persistence behavior
This header owns no state, but OSL implementations maintain locks, caches, mappings, scheduled work, interrupt registrations, and output destinations. Table overrides may redirect persistent firmware inputs to OS-provided replacement tables for the current boot.

## Dependencies and integration points
It depends on ACPICA platform environment and types. In Linux, implementation lives in ACPI OSL code and bridges ACPICA to kernel allocators, spinlocks, workqueues, IRQ APIs, ioremap, PCI config access, printk/debugging, and firmware table override mechanisms.

## Risks and test signals
Risks include deadlocks from wrong lock semantics, sleeping in atomic paths, mismatched map/unmap lifetimes, incorrect access widths, PCI config failures, interrupt removal races, workqueue draining issues, table override lifetime bugs, and debugger hooks compiled into unsuitable environments. Test signals include ACPICA initialization/termination, table override tests, lock/semaphore timeout behavior, GPE/notify work execution, memory and I/O operation-region access, PCI config region access, sleep/stall timing, interrupt install/remove stress, and builds with alternate prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpiosxf.h -->
