# sources/distributed-fs/ceph-client/tools/perf/util/dlfilter.h

## Purpose
This header defines the internal perf object used to manage a dlfilter plugin and declares the wrapper APIs used by perf script. It separates fast inline no-op checks from the heavier callback invocation implemented in `dlfilter.c`.

## Important APIs And Types
`struct dlfilter` stores the plugin file path, `dlopen` handle, plugin-private `data`, session pointer, context-validity flags, dlfilter arguments, transient event/sample/evsel/machine/address-location pointers, public converted sample/address objects, and function pointers for `start`, `stop`, `filter_event`, and `filter_event_early`. API declarations cover construction, start, event dispatch, cleanup, filter listing, and description lookup.

## Control Flow And Integration
Callers construct a filter with `dlfilter__new()`, optionally start it with a session, and then call `dlfilter__filter_event()` or `dlfilter__filter_event_early()`. The inline wrappers return pass-through success when no filter or no matching callback exists; otherwise they delegate to `dlfilter__do_filter_event()`.

## State And Persistence
Persistent state is the plugin handle, file path, callback table, plugin data returned from `start`, and command-line arguments. Event context fields are transient and valid only during `dlfilter__do_filter_event()`. This is important because helper callbacks in the public dlfilter API guard on `ctx_valid`.

## Risks And Test Signals
The main risks are callers bypassing the inline guards with a partially initialized object, plugins assuming context persists after callbacks, and lifetime mistakes around `dlargv` ownership, which is borrowed. Tests should cover null filters, missing early/normal callbacks, start/stop data lifetime, cleanup after failed start, and event filtering with both resolved and unresolved address locations.
