# sources/distributed-fs/ceph-client/tools/perf/ui/keysyms.h

## Purpose

`keysyms.h` centralizes perf UI key constants.

## Important APIs, Types, and Functions

It includes `libslang.h`, defines control-key macro usage and perf-specific pseudo keys such as timer, error, resize, tab/untab, switch-input-data, and reload, and declares `key_name`.

## Control Flow and State

There is no runtime flow. It defines the shared numeric vocabulary used by SLang input and browser hotkey handling.

## Dependencies and Integration Points

TUI setup, browser utilities, map/hist browsers, and warning code include it.

## Risks and Test Signals

Risks are collisions between pseudo keys and SLang key values. Build and runtime hotkey tests across all browser paths validate it.
