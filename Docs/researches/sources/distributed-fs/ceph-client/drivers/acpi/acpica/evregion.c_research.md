# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evregion.c

## Purpose
Implements operation-region handler dispatch, region attach/detach, `_REG` execution, and bulk `_REG` walks. It lazily activates regions on first access, routes field accesses to installed address-space handlers, manages handler-region bidirectional links, and notifies firmware when region availability changes.

## Important APIs, Types, And Functions
- `acpi_ev_initialize_op_regions` runs `_REG(CONNECT)` for default-handler spaces that need it.
- `acpi_ev_address_space_dispatch` initializes a region if needed, prepares special context for PCC/FFH/GSBus/GPIO, exits the interpreter for non-default handlers, and invokes the address-space handler.
- `acpi_ev_attach_region` and `acpi_ev_detach_region` maintain the handler's region list and the region's handler pointer/reference.
- `acpi_ev_execute_reg_method` finds/caches a region's `_REG` method, builds `(space_id, connect_state)` arguments, evaluates it, and tracks `AOPOBJ_REG_CONNECTED`.
- `acpi_ev_execute_reg_methods`, `acpi_ev_reg_run`, and `acpi_ev_execute_orphan_reg_method` walk regions for a space and handle EC/GPIO orphan `_REG` compatibility.

## Control Flow
Dispatch first requires a secondary object and installed handler. If setup is incomplete, it prepares space-specific handler context, exits the interpreter, calls the setup routine with `ACPI_REGION_ACTIVATE`, records the returned region context, then continues. Non-default handlers run outside the interpreter lock. GSBus/GPIO use the handler context mutex to pass connection buffer, resource length, and access length; GPIO also remaps address/bit width to pin index and field bit length. Detach unlinks the region, optionally drops the namespace mutex to run `_REG(DISCONNECT)`, deactivates the region through setup, clears context, removes the handler reference, and protects against circular handler lists.

## State And Persistence
State is stored in region objects and secondary objects: handler pointer, next-region link, setup flags, `_REG` cached method node, region context, address/length/space ID, `AOPOBJ_SETUP_COMPLETE`, and `AOPOBJ_REG_CONNECTED`. Handler objects store region lists, setup callbacks, contexts, and context mutexes.

## Dependencies And Integration Points
Depends on namespace object lookup/walking/search, address-space handler registration, interpreter lock enter/exit, OS mutexes, region setup callbacks, utility integer object creation, method evaluation, and public `acpi_get_handle`/`acpi_evaluate_object` for orphan `_REG`.

## Risks And Edge Cases
Missing handlers return `AE_NOT_EXIST` but many regions are created before handlers exist. Setup callbacks may run control methods, so interpreter locking must be correct. Non-default handlers may block, requiring interpreter release. GSBus/GPIO shared context must be mutex-protected. `_REG` connect/disconnect calls are paired and skipped if already in the requested state. Orphan `_REG` execution intentionally ignores errors for EC/GPIO firmware compatibility.

## Test Signals
Test lazy setup on first field access, no-handler region access failure, default versus non-default interpreter lock behavior, GSBus/GPIO context population, handler errors including EC timeout diagnostics, attach/detach reference counts, `_REG` connect/disconnect pairing, skipped `_REG` for system memory/IO/data table, and orphan EC/GPIO `_REG` execution only when no matching region exists.
