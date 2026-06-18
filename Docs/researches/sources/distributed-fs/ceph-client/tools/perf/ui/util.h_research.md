# sources/distributed-fs/ceph-client/tools/perf/ui/util.h

## Purpose

`ui/util.h` declares generic UI dialogs and error-operation registration.

## Important APIs, Types, and Functions

It declares input/menu/help/dialog/info functions, `struct perf_error_ops`, and `perf_error__register/perf_error__unregister`.

## Control Flow and State

No runtime behavior exists here. The header defines the UI utility contract used by TUI implementations and generic callers.

## Dependencies and Integration Points

It is included by generic util, TUI util, GTK util/setup, browser code, and script dialogs.

## Risks and Test Signals

Risks are backend implementations missing a declared function or incompatible callback signatures. Build coverage of all UI configurations validates it.
