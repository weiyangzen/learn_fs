# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/dpll.c

## Purpose
This file adapts ZL3073x hardware state and controls to the Linux DPLL framework. It allocates per-channel DPLL devices, registers eligible input/output pins, implements DPLL device and pin ops, handles automatic/manual mode semantics, exposes phase/frequency monitoring, and sends change notifications from the periodic worker.

## Important APIs, types, and functions
The internal `struct zl3073x_dpll_pin` stores per-registered-pin state, labels, firmware node handles, priority, phase granularity, last pin state, phase offset, FFO, and measured frequency. External APIs are `zl3073x_dpll_alloc()`, `zl3073x_dpll_free()`, `zl3073x_dpll_register()`, `zl3073x_dpll_unregister()`, `zl3073x_dpll_init_fine_phase_adjust()`, and `zl3073x_dpll_changes_check()`. DPLL pin ops cover direction, esync, FFO, frequency, measured frequency, phase offset, phase adjust, priority, ref-sync, and state on DPLL. Device ops cover lock status, mode, supported modes, monitor toggles, averaging factor, and optional die temperature.

## Control flow
Registration creates a `dpll_device`, enumerates input then output pins, filters out disabled pins, N pins for differential signals, inputs on NCO channels, and outputs driven by other channels, then gets DPLL pin objects and registers them with appropriate ops. Firmware-node `ref-sync-sources` are resolved after pins are registered. Device mode maps hardware freerun/holdover/ref-lock/NCO to DPLL manual and hardware auto to DPLL automatic. Pin state changes either force reference lock, return to freerun/holdover, or toggle priority selectability in automatic mode. Output frequency changes recompute output divisors and handle N-div pairs. Esync uses special reference/output registers and currently only exposes a narrow 0/1 Hz range.

## State and persistence
Per-DPLL runtime state is `struct zl3073x_dpll`: registered DPLL pointer, ops, monitor booleans, cached lock status, check counter, pin list, and async change work. Hardware configuration changes persist in device registers/firmware state through `ref_state_set()`, `chan_state_set()`, and `out_state_set()`. Last observed pin measurements are runtime cache used to suppress duplicate notifications.

## Dependencies and integration points
The file depends on cached hardware state from `core/ref/out/synth/chan`, firmware-node properties from `prop.c`, and Linux DPLL core APIs. `core.c` calls registration during start and calls `zl3073x_dpll_changes_check()` from the twice-per-second worker.

## Risks and edge cases
Mode transitions depend on the last cached lock status and selected-reference status. Shared pins can be registered to multiple DPLLs, so generic netlink updates may call these ops for every reference. Ref-sync connect intentionally sets the sync source priority to NONE and does not restore it on disconnect. Phase offset math wraps offsets when comparing references of different frequencies. Output N-div calculations reject zero divisors but can lose precision through integer division.

## Test signals
Exercise DPLL registration for all supported channel counts, firmware-node pin metadata, auto/manual transitions, priority changes, forced reference connect/disconnect, ref-sync connect validation, esync enable/disable, input/output frequency changes, phase adjust, monitor toggles, notification changes, and optional die temperature on flagged chips.
