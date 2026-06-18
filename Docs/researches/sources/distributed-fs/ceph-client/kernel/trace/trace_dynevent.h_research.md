# sources/distributed-fs/ceph-client/kernel/trace/trace_dynevent.h

## Purpose
`trace_dynevent.h` defines the shared interface for dynamic event providers and command builders used by the generic dynamic events implementation.

## Important APIs, types, and functions
Core types are `struct dyn_event_operations`, `struct dyn_event`, `struct dynevent_arg`, and `struct dynevent_arg_pair`. The operations table requires `create`, `show`, `is_busy`, `free`, and `match` callbacks. Inline helpers include `dyn_event_init()`, `dyn_event_add()`, and `dyn_event_remove()`. Iteration macros `for_each_dyn_event` and `for_each_dyn_event_safe` wrap the global list.

## Control flow
Providers register a `dyn_event_operations` object, embed `struct dyn_event` in their event-specific object, initialize it with `dyn_event_init()`, and add it to the global list with `dyn_event_add()` while holding `event_mutex`. The generic tracefs layer later invokes provider callbacks through this contract for create, display, match, busy checks, and deletion. Command helper declarations support building type-specific tracefs command strings safely into a `dynevent_cmd`.

## State and persistence behavior
The header declares `dyn_event_list` but stores no state itself. `dyn_event_add()` marks the associated `trace_event_call` dynamic and links the event into persistent in-memory dynamic event state; `dyn_event_remove()` unlinks it.

## Dependencies and integration points
It depends on list, mutex, seq file, kernel utility headers, and `trace.h` for `event_mutex`, `trace_event_call`, and `dynevent_cmd` definitions. Providers such as eprobes, kprobes, uprobes, fprobes, and synthetic events include this header.

## Risks
The inline add/remove helpers assert `event_mutex` but do not acquire it, so callers must satisfy locking. Providers must implement every required callback; missing callbacks are rejected by registration, but incorrect match/free semantics can still cause leaks or wrong deletion.

## Test signals
Build all dynamic event providers, create and delete events from each provider, verify `dynamic_events` listing uses each `show()` implementation, and run lockdep while mutating dynamic events concurrently with trace event enable/disable.
