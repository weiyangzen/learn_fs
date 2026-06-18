<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/olpc-ec.h -->
# sources/distributed-fs/ceph-client/include/linux/olpc-ec.h

## Purpose
This header declares OLPC XO embedded-controller command constants, SCI source bits, driver callbacks, and EC command/wakeup helpers.

## Important APIs, types, and functions
It defines XO EC command IDs such as firmware revision, SCI mask/query, WLAN reset/wakeup, DCON power, ebook mode, and SCI inhibit commands. SCI source masks cover game keys, battery events, ebook/WLAN, AC power, critical battery, and GP wake. `struct olpc_ec_driver` supplies suspend/resume, `ec_cmd`, and wakeup availability. APIs under `CONFIG_OLPC_EC` include `olpc_ec_driver_register()`, `olpc_ec_cmd()`, wakeup set/clear, SCI mask/query, wakeup availability, and `xo1_do_sleep()`.

## Control flow
Platform EC driver registers callbacks and private data. Subsystems issue EC commands through `olpc_ec_cmd()`, manipulate wakeup masks, query SCI status, and participate in suspend/resume. Disabled EC support makes command return `-ENODEV` and wakeup helpers no-op/false.

## State and persistence
EC hardware stores firmware state, SCI masks, wakeup bits, and sleep behavior. Kernel runtime state is the registered driver and callback argument in implementation code.

## Dependencies and integration points
It depends on bit macros and platform devices. It integrates OLPC laptop platform drivers with power, battery, WLAN, display controller, input/SCI, and suspend paths.

## Risks and test signals
Risks include command buffer length mismatches, SCI mask bit confusion between XO-1 and XO-1.5, sleep-state ABI issues, wakeup mask races, and disabled-config callers not handling `-ENODEV`. Test EC command transactions, firmware revision read, SCI query/mask, WLAN reset/wakeup, suspend/resume, wake source availability, and `!CONFIG_OLPC_EC` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/olpc-ec.h -->
