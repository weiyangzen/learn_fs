# sources/distributed-fs/ceph-client/kernel/trace/trace_export.c

## Purpose
Builds exported trace event descriptors for core ftrace events from `trace_entries.h`. It uses repeated macro redefinition to generate compile-time structure checks, field metadata arrays, `trace_event_class` objects, `trace_event_call` objects, and `_ftrace_events` section entries.

## Important APIs, Types, And Functions
The only ordinary function is `ftrace_event_is_function()`, which identifies the `event_function` trace event. `ftrace_event_register()` is a stub registration callback used for entries with triggers. Most behavior is macro-driven through `FTRACE_ENTRY`, `FTRACE_ENTRY_REG`, `FTRACE_ENTRY_DUP`, field macros such as `__field`, `__array`, and `__dynamic_array`, and the included `trace_entries.h`.

## Control Flow
The file includes `trace_entries.h` three times with different macro meanings. The first pass emits temporary `____ftrace_*` structs and `____ftrace_check_*()` functions that force the printk format strings to compile against the entry structure. The second pass emits `ftrace_event_fields_*` arrays used by trace event formatting and filtering. The third pass emits `trace_event_class` and `trace_event_call` definitions and places pointers in the `_ftrace_events` linker section for discovery by the trace core.

## State And Persistence
All generated event metadata is static kernel data. There is no runtime mutable state in this file except trace-core state attached to the generated `trace_event_call` instances elsewhere. Generated calls are marked `TRACE_EVENT_FL_IGNORE_ENABLE`, so their enable semantics are special to ftrace internals.

## Dependencies And Integration Points
This file depends on `trace_entries.h`, `trace_output.h`, kallsyms/stringification helpers, filter type constants, and the trace event linker-section discovery mechanism. It is a bridge between low-level ftrace ring-buffer entry definitions and user-visible trace event metadata consumable by tracefs and perf.

## Risks
The macro layering is brittle: changing a field macro in one pass without matching the others can create mismatched C structs, field metadata, or print formats. Packed fields, dynamic arrays, and special filter types such as `FILTER_TRACE_FN` must preserve the ABI expected by filtering and output code. Since most definitions are generated at compile time, failures can appear as build errors or subtle runtime formatting/filtering mismatches.

## Test Signals
Primary signals are successful kernel build, no printk format warnings from generated check functions, and trace event registration of ftrace events at boot. Runtime smoke tests include reading ftrace event format files, filtering on function fields, enabling perf access to generated events that use registration functions, and verifying `ftrace_event_is_function()` consumers detect the function event correctly.
