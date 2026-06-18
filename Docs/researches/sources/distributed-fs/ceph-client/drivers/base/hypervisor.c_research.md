# sources/distributed-fs/ceph-client/drivers/base/hypervisor.c

## Purpose
`hypervisor.c` creates the global `/sys/hypervisor` kobject used as the top-level anchor for hypervisor-specific sysfs interfaces.

## Important APIs, Types, And Functions
It defines and exports `struct kobject *hypervisor_kobj`. `hypervisor_init()` creates the kobject with `kobject_create_and_add("hypervisor", NULL)`.

## Control Flow, State, And Persistence
During driver core initialization, `hypervisor_init()` creates the root kobject. The pointer persists globally for architecture or hypervisor code that needs to add child kobjects or attributes below `/sys/hypervisor`.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies are kobjects, device headers, exports, and init ordering from `driver_init()`. Risks are allocation failure and consumers using the pointer before initialization. Test signals include boot presence of `/sys/hypervisor`, exported symbol use by hypervisor-specific code, and clean error return under allocation-failure injection.
