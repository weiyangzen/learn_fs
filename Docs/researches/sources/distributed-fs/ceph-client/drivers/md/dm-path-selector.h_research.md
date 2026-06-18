
# sources/distributed-fs/ceph-client/drivers/md/dm-path-selector.h

## Purpose
Defines the path selector interface used by the dm multipath target and selector modules. It abstracts how a priority group chooses a path and how selector-specific state is created, updated, reported, and notified of I/O lifecycle.

## Important APIs, Types, And Functions
`struct path_selector` stores a selector type and opaque context. `struct path_selector_type` contains the selector name, owning module, feature flags, status argument counts, and callbacks: `create`, `destroy`, `add_path`, `select_path`, `fail_path`, `reinstate_path`, `status`, optional `start_io`, and optional `end_io`. `DM_PS_USE_HR_TIMER` requests high-resolution bio timing for selectors that use elapsed I/O time. Registry functions are declared: `dm_register_path_selector()`, `dm_unregister_path_selector()`, `dm_get_path_selector()`, and `dm_put_path_selector()`.

## Control Flow
Multipath obtains a selector type, calls `create`, adds each path with selector arguments, calls `select_path` during mapping, notifies `start_io`/`end_io` around I/O where implemented, calls failure/reinstate callbacks on path state changes, and asks `status` to format table/info/IMA details.

## State And Persistence
The header defines contracts for in-memory selector contexts only. Persistence is outside this interface and normally represented by dm table arguments emitted through `status`.

## Dependencies And Integration Points
Includes `linux/device-mapper.h` and `dm-mpath.h` for `struct dm_path`. It is consumed by `dm-mpath.c`, the selector registry, and individual selector modules.

## Risks
Selector callbacks run in performance-sensitive and sometimes constrained contexts. `select_path` returning NULL drives failover/no-path behavior. `start_io` and `end_io` must be balanced and tolerate requeue/error paths. Status argument counts must match emitted table/info fields or userspace parsers break.

## Test Signals
Compile selector modules, validate callback contracts with path failures and requeues, verify high-resolution timing flag behavior in bio mode, check table/status argument counts, and run multipath I/O tests for every registered selector.
