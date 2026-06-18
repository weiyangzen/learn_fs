# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kherr.h

## Purpose

`kherr.h` defines NetIDMgr's structured error-reporting subsystem. It lets code build thread-local hierarchical error contexts, report localized and formatted events, attach facilities, suggestions, progress, and resources, notify context handlers, and later expose those events through alerts or error viewers.

## Important APIs, Types, and Functions

- Parameter types `KEPT_*` and `kherr_param` describe values used to expand formatted event strings.
- Severity levels run from `KHERR_FATAL`, `ERROR`, `WARNING`, `INFO` through debug levels to `KHERR_NONE`; smaller values are more severe.
- Suggestion IDs include none, abort, retry, ignore, interact, and other.
- `kherr_event` stores magic, reporting thread, short/facility/location/long/suggestion strings, severity, facility ID, suggestion ID, resource/free flags, four parameters, tick and FILETIME timestamps, optional module handle, and list links.
- Event flags distinguish constant/resource/message/free strings for short, long, and suggestion fields, plus resolved, folded, inert, and committed states.
- `kherr_context` stores magic, unique serial, aggregate severity, flags, refcount, descriptor event, significant error event, progress meter, tree links, and event queue.
- Context flags include dirty, own-progress, unbound, transitive, and an initial mask.
- Handler APIs are `kherr_add_ctx_handler()` and `kherr_remove_ctx_handler()`.
- Reporting APIs include `kherr_report()`, `kherr_reportf_ex()`, `kherr_reportf()`, `kherr_dup_string()`, inline `kherr_val()`, and helper macros such as `_int32`, `_cstr`, `_dupstr`, `_report_cs*`, `_report_sr*`, `_report_mr*`, and `_report_ts*`.
- Last-event mutation APIs include `kherr_suggest()`, `kherr_location()`, `kherr_facility()`, `kherr_set_desc_event()`, and `kherr_del_last_event()`.
- Context lifecycle/traversal APIs include create/hold/release, push/pop/peek, error clear/check, progress set/get, event iteration, child-context iteration, descriptor/error event access, and event evaluation.

## Control Flow

Typical code calls `kherr_push_new_context()` or pushes an unbound context, reports one or more events with `kherr_report()` or macros, optionally mutates the last event with suggestion/location/facility/descriptor calls, and pops the context. Contexts form a hierarchy independent of each thread's stack; an unbound context becomes attached when pushed. Events can remain unresolved until a UI or caller asks for strings, at which point `kherr_evaluate_event()` loads resources, expands inserts, frees transient string ownership, and marks resolved state. Context handlers run synchronously in the thread that caused a begin, describe, error, end, or event-commit transition.

## State and Persistence Behavior

Error state is thread-local plus globally discoverable through context trees. Contexts are refcounted and assigned serial numbers because context objects can be reused. Event lists are valid only while the owning context is held, and the last event may still be active until committed by a later event or context closure. The subsystem itself is transient; persistence is normally achieved by UI reporting, debug output, or external logs. Transitive contexts propagate across message handling for threads processing messages caused by the originating context.

## Dependencies and Integration Points

`kherr.h` depends on `khdefs.h` and `khlist.h`, plus Win32 types such as `DWORD`, `FILETIME`, `HMODULE`, `MAKEINTRESOURCE`, and `DWORD_PTR` when used on Windows. `khalerts.h` embeds `kherr_context` and `kherr_event` pointers. `kmq.h` stores a `kherr_context` on each `kmq_message` so async work can carry error state. Facility IDs include KMM, KCDB, UI, KRB5, KRB4, AFS, and user banks.

## Risks and Edge Cases

- Most functions are deliberately lightweight and often return no error; failure to record an error can be silent after the original failure.
- Constant string pointers are not copied. Callers must use `_dupstr`/`KEPT_STRINGT` or free flags for transient buffers.
- Handler callbacks must be reentrant and fast because they run inside the reporting thread.
- Context/event pointers from traversal become invalid after releasing the context.
- `_report_sr*` and `_report_mr*` macros require `KHERR_HMODULE` for resource resolution; missing module setup causes compile failures or null module behavior.
- There is a declaration typo in `kherr_report()` parameter name `long_desC`; harmless for ABI but a signal that callers should rely on types, not parameter spelling.

## Test Signals

- Report events with constant, duplicated, free, string-resource, and message-resource strings, then force evaluation and verify cleanup.
- Push/pop nested and unbound contexts across multiple threads and verify serial uniqueness and hierarchy.
- Register handlers for each event kind and ensure no deadlocks when handlers inspect but do not hold closed contexts.
- Validate severity aggregation, dirty recalculation, descriptor removal from event queues, and error clearing.
- Carry a context through KMQ message dispatch and show it through `khalerts.h`.
