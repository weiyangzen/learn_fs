<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal.h

## Purpose
This header declares Linux OPAL firmware call wrappers and higher-level PowerNV OPAL subsystem initialization, async, notifier, console, sensor, dump, HMI, PCI, flash, secure variable, and MPIPL helpers.

## Important APIs, Types, And Functions
It defines `SG_ENTRIES_PER_NODE`, `OPAL_BUSY_DELAY_MS`, `opal_kobj`, `opal_node`, dozens of `opal_*` firmware call prototypes, initialization hooks such as `opal_elog_init()`, `opal_platform_dump_init()`, `opal_sys_param_init()`, `opal_msglog_init()`, `opal_async_comp_init()`, `opal_sensor_init()`, `opal_hmi_handler_init()`, console helpers, notifier registration, async token wait/release helpers, SG-list helpers, `opal_error_code()`, `opal_get_async_rc()`, and subsystem init helpers for powercap/PSR/sensor groups.

## Control Flow
Kernel subsystems call wrappers to enter OPAL, often looping on `OPAL_BUSY`/`OPAL_BUSY_EVENT` with the default delay or waiting for async completion messages. Init code discovers `/ibm,opal`, configures cores, and initializes service subsystems.

## State And Persistence Behavior
State spans firmware and kernel: OPAL device-tree node, sysfs kobject, async token ownership, pending logs, message queues, sensors, flash/dump state, secure variables, and firmware-maintained platform configuration.

## Dependencies And Integration Points
It depends on `opal-api.h`, notifier support, device tree, HVC console, PowerNV PCI/interrupts, RTC/NVRAM, sensors, HMI/MCE handlers, flash, sysfs, and dump infrastructure.

## Risks And Edge Cases
Async token leaks can stall firmware calls. Big-endian output buffers must be converted by callers. Busy-event loops must wake the OPAL poller. Machine-check/HMI handlers run in fragile contexts.

## Test Signals
Boot PowerNV, validate `/sys/firmware/opal`, HVC console, async completion, OPAL event polling, PCI/EEH, sensors, RTC/NVRAM, secure variables, dump/flash workflows, and HMI/MCE recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal.h -->
