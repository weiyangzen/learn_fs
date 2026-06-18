<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/prom.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/prom.c

## Purpose
Provides the OpenRISC early device-tree scan hook.

## Important APIs, Types, And Functions
`early_init_devtree(void *params)` calls `early_init_dt_scan(params, __pa(params))` and then enables memblock resizing.

## Control Flow
`or1k_early_setup()` passes an FDT pointer here before `setup_arch()` unflattens and copies the device tree.

## State And Persistence
Initializes global early OF data and memblock memory reservations.

## Dependencies And Integration Points
Depends on `of_fdt`, `memblock`, and `__pa()` translation.

## Risks
The FDT pointer must be valid under early translation rules. Bad physical address conversion prevents memory and CPU discovery.

## Test Signals
Boot with external and built-in DTB, reserved-memory parsing, and memblock dump consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/prom.c -->
