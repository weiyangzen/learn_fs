<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cfg.cc -->
# sources/distributed-fs/lizardfs/src/common/cfg.cc

## Purpose

This file implements a legacy process-global configuration file parser and typed getters.

## Important APIs, Types, and Functions

Public functions are `cfg_load()`, `cfg_reload()`, `cfg_term()`, `cfg_filename()`, `cfg_isdefined()`, and generated getters for strings, integers, unsigned integers, int sizes, uint sizes, and double. Internal state is a linked list of `paramstr` nodes plus `cfgfname` and `logundefined`.

## Control Flow

`cfg_load()` resets global state, duplicates the filename, and calls `cfg_do_load()`. The parser reads lines up to 1000 bytes, accepts uppercase/underscore names, `=`, printable values, trailing whitespace or comments, and replaces duplicate definitions. Getters linearly scan the list and convert with `strtol`/`strtoul`/`strtod` or duplicate strings, logging defaults when configured.

## State and Persistence Behavior

Configuration is stored in process-global heap memory until `cfg_term()`. `cfg_reload()` tears down and reloads the current filename.

## Dependencies and Integration Points

It depends on C stdio/string allocation, logging, and assertion helpers. Many LizardFS daemons use these getters for startup/reload configuration.

## Risks and Edge Cases

The subsystem is not thread-safe. `cfg_load()` does not call `cfg_term()` before replacing existing state. Numeric conversions do not validate full-string consumption, overflow, or signed-to-unsigned range. `cfg_term()` frees globals but does not reset pointers, so repeated termination without reload can double-free.

## Test Signals

Useful tests parse comments, whitespace, duplicate keys, malformed lines, all numeric types, reload behavior, and repeated term/load lifecycles. No direct unit test is present here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/cfg.cc -->
