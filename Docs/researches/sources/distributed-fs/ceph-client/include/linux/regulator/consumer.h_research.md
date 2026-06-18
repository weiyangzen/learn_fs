# sources/distributed-fs/ceph-client/include/linux/regulator/consumer.h

## Purpose

`consumer.h` declares the regulator framework API used by device drivers that consume power rails. It covers supply acquisition, enable/disable, voltage/current/load/mode control, bulk operations, notifier registration, suspend configuration, OF lookup, and stubs for builds without regulator support.

## Important APIs, Types, and Functions

Generic modes are `REGULATOR_MODE_FAST`, `NORMAL`, `IDLE`, and `STANDBY`; error flags describe under-voltage, over-current, regulation failure, general failure, over-temperature, and warning variants. `struct pre_voltage_change_data` is notifier payload. `struct regulator_bulk_data` pairs supply names with acquired consumer handles and initial load.

Acquisition APIs include `regulator_get()`, `devm_regulator_get()`, exclusive and optional variants, `devm_regulator_get_enable*()`, OF variants, supply alias registration, and bulk get helpers. Control APIs include `regulator_enable()`, disable/force/deferred disable, `regulator_is_enabled()`, voltage list/map/set/get/sync/time/tolerance helpers, current limit APIs, power budget APIs, mode/load/bypass/error APIs, hardware VSEL/regmap queries, and hardware enable.

Notification and metadata APIs include notifier register/unregister/devm helpers, suspend voltage/enable/disable helpers, drvdata get/set, bulk supply-name helpers, and `regulator_is_equal()`. When `CONFIG_REGULATOR` is disabled, stubs return success for many optional operations, `NULL` for normal get, `ERR_PTR(-ENODEV)` for optional/exclusive get, or negative errors for queries that cannot be faked.

## Control Flow

A consumer gets one or more supplies, optionally sets load or voltage/current constraints, enables supplies before hardware access, and disables/frees them during shutdown. Bulk helpers perform these steps over arrays and unwind on errors in implementation. Notifier users subscribe to events from the regulator core. OF helpers resolve supplies from a given device node.

Voltage convenience helpers first try a target-only range and then a wider fallback range (`regulator_set_voltage_triplet()` and `_tol()`).

## State and Persistence Behavior

Consumer handles track open/use counts, enable votes, voltage/current/load requests, bypass requests, and notifier registrations in regulator core state. The requested state affects hardware rail configuration and can persist while consumers are bound or, depending on hardware and bootloader, across suspend/reset.

## Dependencies and Integration Points

The header depends on `err.h`, suspend types, regulator UAPI/internal event definitions, OF device nodes, regmap, and device model types. It is used by most device drivers that need named supplies from DT, ACPI, board data, or regulator aliases.

## Risks

Ignoring `ERR_PTR()` from optional/exclusive gets, assuming disabled-config stubs reflect real hardware, mismatching enable/disable calls, or setting voltage/current outside board constraints can break devices. Bulk operations need proper unwind. Query functions can return negative errno and should not be treated as physical zero. Load/mode requests affect DRMS and shared rail efficiency.

## Test Signals

Tests should cover supply resolution, optional-vs-required behavior, enable count balancing, bulk get/enable unwind, voltage/current constraint enforcement, notifiers, bypass/load/mode behavior, OF bulk get, and disabled-`CONFIG_REGULATOR` build stubs.
