# File Research: sources/block-storage/linux-dm/drivers/md/dm-path-selector.h

## Purpose

`dm-path-selector.h` defines the path selector interface consumed by `dm-mpath.c` and implemented by selector modules.

## Interface

`struct path_selector` stores a selector type pointer and selector-private context. `struct path_selector_type` supplies the selector name, module, table/info argument counts, constructor/destructor, path registration, path selection, failure/reinstate hooks, status hook, and optional `start_io`/`end_io` accounting callbacks.

The multipath target calls `create()` per priority group, `add_path()` for each path, `select_path()` for mapping, `fail_path()` and `reinstate_path()` on path state changes, `status()` during table/info/IMA reporting, and `start_io()`/`end_io()` around completed mapped I/O when provided.

## Contract

`add_path()` receives selector-specific path arguments and must set `path->pscontext` if it needs per-path state. `select_path()` returns a usable `dm_path` or `NULL` if none are available. `status()` must support being called with `path == NULL` to report selector-level arguments/status.

## Invariants And Risks

- `table_args` and `info_args` must match status output expected by `dm-mpath.c`.
- Selectors must tolerate fail/reinstate and status calls for paths they accepted.
- `start_io()` and `end_io()` must remain balanced across normal and error completions for selectors that maintain load counters.
- Selector callbacks may run in I/O paths, so locking and allocation behavior must be conservative.

## Test Focus

Validate each selector’s table/info argument counts, `path == NULL` status behavior, callback balance under requeue/error completion, and per-path context lifetime.
