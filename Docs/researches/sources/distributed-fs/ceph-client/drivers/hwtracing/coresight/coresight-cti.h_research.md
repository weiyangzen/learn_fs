# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti.h

## Purpose
`coresight-cti.h` defines CTI register offsets, trigger/connection/configuration structures, operation enums, and internal function prototypes shared by the CTI core, platform parser, and sysfs implementation.

## Important APIs, Types, And Functions
Register definitions cover CTI control, interrupt acknowledge, app set/clear/pulse, input/output enable arrays, trigger/channel status, gate, ASIC control, integration-test registers, and management affinity registers. `struct cti_trig_grp` describes a group of related trigger signals with a used-mask and per-signal type IDs. `struct cti_trig_con` connects a CTI to a CPU/CoreSight/other device and carries dynamic sysfs metadata.

`struct cti_device` stores CTI topology metadata: connection count, CTM ID, trigger connection list, CPU affinity, and sysfs group table. `struct cti_config` caches hardware programming and capability state. `struct cti_drvdata` is the top-level device state. Enums describe channel attach/detach, trigger direction, gate operations, and software channel set/clear/pulse operations. Prototypes expose CTI core/platform/sysfs functions within the CTI driver.

## Control Flow
The header has no direct control flow, but it defines the shared contract: platform parsing fills `cti_device`/connection data, sysfs mutates `cti_config`, and core enable writes the cached config to hardware.

## State And Persistence
The persistent runtime state is the combination of `cti_device` and `cti_config` inside `cti_drvdata`. Cached CTIINEN/CTIOUTEN, gate, app-set, ASIC control, filters, and selectors persist while the driver is bound and are replayed on enable.

## Dependencies And Integration Points
The header depends on CoreSight public/private headers, sysfs, lists, spinlocks, and kernel types. It is private to the CTI implementation family but central to all three CTI C files.

## Risks
`CTIINOUTEN_MAX` bounds arrays at 32; hardware values are clamped in core but all users must respect `nr_trig_max`. Flexible allocation of `cti_trig_grp.sig_types[]` requires exact sizes. Dynamic sysfs pointers in `cti_trig_con` must remain valid for the device lifetime.

## Test Signals
Compile coverage across CTI core/platform/sysfs is essential. Runtime tests should verify capability limits, flexible trigger group allocation, connection list lifetime, and cached config replay.
