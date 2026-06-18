<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cfg.h -->
# sources/distributed-fs/lizardfs/src/common/cfg.h

## Purpose

The header declares the global configuration loader/getter API and typed convenience wrappers.

## Important APIs, Types, and Functions

Public declarations include `cfg_load`, `cfg_reload`, `cfg_term`, `cfg_filename`, `cfg_isdefined`, typed `cfg_get*` functions, overloads `cfg_get()`, `cfg_ranged_get()`, templates `cfg_get_minvalue()`, `cfg_get_maxvalue()`, `cfg_get_minmaxvalue()`, and `cfg_warning_on_value_change()`.

## Control Flow

Callers load a config file, request typed values with defaults, optionally clamp ranges, and terminate on shutdown. Range helpers log when values are outside accepted bounds.

## State and Persistence Behavior

The header exposes a process-global runtime config model implemented in `cfg.cc`. Returned `char*` values from `cfg_getstr`/string-copy paths are heap allocations requiring caller discipline.

## Dependencies and Integration Points

It depends on `slogger` and standard integer/string types. It is a cross-daemon common API.

## Risks and Edge Cases

Template helpers use `std::to_string`, so they require numeric-like types. `cfg_get(const char*, const std::string defaultValue)` passes default by value rather than const reference. The API does not express ownership for `char*` getters in the type system.

## Test Signals

Coverage should include clamping logs, changed-value warnings, default logging, string ownership, and each typed getter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cfg.h -->
