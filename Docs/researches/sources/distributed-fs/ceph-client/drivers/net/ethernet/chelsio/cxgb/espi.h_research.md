# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/espi.h

## Purpose
`espi.h` is the public interface for the cxgb ESPI module. It exposes the opaque `struct peespi` handle, ESPI interrupt counter shape, lifecycle functions, interrupt controls, and monitor-counter accessors used by the adapter, ethtool, and SGE workaround code.

## Important APIs, Types, and Functions
`struct espi_intr_counts` contains six software counters: DIP4 errors, RX drops, TX drops, RX overflow, RAM parity errors, and DIP2 parity errors. `struct peespi` is forward-declared to keep implementation state private. The lifecycle API is `t1_espi_create()`, `t1_espi_destroy()`, and `t1_espi_init()`. Interrupt APIs are `t1_espi_intr_enable()`, `t1_espi_intr_clear()`, `t1_espi_intr_disable()`, `t1_espi_intr_handler()`, and `t1_espi_get_intr_counts()`. Monitor APIs are `t1_espi_get_mon()` and `t1_espi_get_mon_t204()`.

## Control Flow
The typical flow is: create the ESPI object during software module setup, initialize it during hardware bring-up with MAC type and port count, enable/clear/disable interrupts as part of adapter-wide interrupt control, call the handler from the slow interrupt path when PL reports ESPI activity, and expose the accumulated counters through ethtool. T2-specific timers in `sge.c` may call the monitor accessors while the adapter is running.

## State and Persistence
The header itself has no state. It defines access to `espi.c` state: a heap-allocated ESPI object tied to an adapter and a set of monotonically increasing software interrupt counters. State is runtime-only and is freed on module teardown.

## Dependencies and Integration Points
It includes `common.h` for `adapter_t` and kernel integer types. `cxgb2.c` uses the counter getter for ethtool statistics. `subr.c` and adapter interrupt code call the interrupt functions. `sge.c` calls monitor functions for T2 ESPI stuck-packet workarounds.

## Risks
Since `struct peespi` is opaque, callers must respect lifecycle ordering and not call interrupt or monitor operations before create/init or after destroy. The monitor APIs expose a `wait` argument; using non-waiting mode requires handling a zero or negative return as lock contention rather than a meaningful counter. Counter fields are plain unsigned integers and can wrap on long-running systems.

## Test Signals
Signals include successful build of all users after prototype changes, adapter initialization with an ESPI object, ethtool ESPI stats matching handler increments, slow interrupt dispatch invoking `t1_espi_intr_handler()`, and SGE workaround timers receiving valid monitor values on T2/T204 without deadlock.
