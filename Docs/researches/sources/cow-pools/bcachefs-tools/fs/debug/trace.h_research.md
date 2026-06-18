# File Research: sources/cow-pools/bcachefs-tools/fs/debug/trace.h

## Purpose

Defines bcachefs tracepoint declarations for string-valued filesystem events.

## Main Interfaces

- Trace system name: `bcachefs`.
- Event class `fs_str(struct bch_fs *c, const char *str)` records filesystem name and string payload.
- Tracepoint sets:
  - Persistent counters via `BCH_PERSISTENT_COUNTERS()`.
  - Non-counter tracepoints such as `accounting_mem_insert`, `journal_entry_close`, `extent_trim_atomic`, and btree iterator events.
  - Optional path tracepoints under `CONFIG_BCACHEFS_PATH_TRACEPOINTS`.

## Behavior

When path tracepoints are disabled, inline no-op `trace_*()` and `trace_*_enabled()` stubs are provided for path tracepoints so callers compile away cleanly.

## Dependencies

Uses Linux tracepoint infrastructure and must be included through `trace/define_trace.h` with `TRACE_INCLUDE_PATH` pointing to `../../fs/bcachefs/debug`.

## Notes

Tracepoints accept free-form strings rather than structured bcachefs objects. This keeps instrumentation lightweight but places formatting responsibility on callers.
