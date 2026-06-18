# sources/distributed-fs/ceph-client/tools/perf/ui/ui.h

## Purpose

`ui.h` declares the high-level perf UI selection and lifecycle API shared by stdio, TUI, and GTK modes.

## Important APIs, Types, and Functions

It declares global `ui__lock`, `perf_gtk_handle`, and `use_browser`; lifecycle functions `setup_browser`, `exit_browser`, optional `ui__init/ui__exit`, `ui__refresh_dimensions`, `stdio__config_color`, and SIGWINCH mask helpers.

## Control Flow and State

When SLang support is absent, inline stubs make `ui__init` fail and `ui__exit` a no-op. Otherwise implementation lives in TUI setup and generic setup.

## Dependencies and Integration Points

It includes the perf mutex abstraction and is used throughout UI code and command frontends that select browser mode.

## Risks and Test Signals

Risks are compile-configuration mismatches and incorrect global `use_browser` assumptions. Build with and without SLang/GTK plus runtime setup/fallback tests validate it.
