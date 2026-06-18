# sources/distributed-fs/ceph-client/kernel/trace/trace_synth.h

## Purpose

`trace_synth.h` declares in-kernel structures for synthetic trace events, including fields, dynamic string metadata, event registration state, and lookup by name. The complete 41-line header was read.

## Important APIs, Types, and Functions

Constants are `SYNTH_SYSTEM`, `SYNTH_FIELDS_MAX`, and `STR_VAR_LEN_MAX`. `struct synth_field` stores type/name strings, size, offset, field position, and signed/string/dynamic/stack flags. `struct synth_event` embeds `struct dyn_event`, reference count, name, field arrays, event class/call, tracepoint pointer, and module pointer. Lookup is `find_synth_event()`.

## Control Flow

The header has no executable flow. Implementation code creates `synth_event` objects, populates fields, registers trace event metadata, exposes dynamic events, and resolves references by name.

## State and Persistence Behavior

Synthetic event state persists while the dynamic event is registered or referenced. Reference count and module pointer indicate lifetime integration with modules and users.

## Dependencies and Integration Points

It includes `trace_dynevent.h` and integrates with dynamic events, trace event classes/calls, tracepoints, modules, filters, and histogram/synthetic event users.

## Risks and Edge Cases

Field and string limits must match trace encoding and filters. Dynamic offsets and `n_u64` sizing must be correct. Module-backed synthetic events must not outlive their module. Lookup must handle deletion races in implementation code.

## Test Signals

Create synthetic events with scalar and dynamic string fields, hit field limits, validate format files, emit events, delete referenced events, and use lookup through histogram/dynamic event paths.
