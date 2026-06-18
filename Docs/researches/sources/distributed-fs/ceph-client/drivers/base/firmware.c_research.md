# sources/distributed-fs/ceph-client/drivers/base/firmware.c

## Purpose
`firmware.c` creates the global `/sys/firmware` kobject used as the top-level anchor for firmware-related kernel interfaces.

## Important APIs, Types, And Functions
It defines and exports `struct kobject *firmware_kobj`. The only function is init-only `firmware_init()`, which calls `kobject_create_and_add("firmware", NULL)`.

## Control Flow, State, And Persistence
During `driver_init()`, `firmware_init()` creates the top-level kobject. The pointer remains globally available to other subsystems and modules that need to place firmware-oriented sysfs nodes under `/sys/firmware`.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies are limited to kobjects, module export support, init annotations, and `base.h`. It integrates with early driver-core initialization before platform, CPU, memory, and other bus setup. Risks are simple but fundamental: allocation failure returns `-ENOMEM`, and users must not assume the pointer exists before driver core init. Test signals are boot-time presence of `/sys/firmware`, successful export consumers, and failure-path propagation if kobject allocation is forced to fail.
