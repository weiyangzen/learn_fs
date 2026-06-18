# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/hists.h

## Purpose

`hists.h` declares the TUI histogram browser object and its small public lifecycle API. It lets other perf UI code allocate, initialize, run, and destroy a browser over a `struct hists` tree.

## Important APIs, Types, and Functions

`struct hist_browser` embeds `struct ui_browser` and stores the active `struct hists`, selected `hist_entry`, selected `map_symbol`, timer, filter stack, perf environment, optional block event, print sequence, display flags, percent limit, row counters, c2c filtering flag, and title callback. Public functions are `hist_browser__new`, `hist_browser__delete`, `hist_browser__run`, and `hist_browser__init`.

## Control Flow and State

The header does not execute code, but it defines the mutable state contract used by `browsers/hists.c`. Ownership is mixed: the browser owns its allocated wrapper but references hists, evsel/env/timer data owned by report/top paths. Row counters are derived state and must be recomputed after filters or folding change.

## Dependencies and Integration Points

It includes `ui/browser.h` and forward-declares `struct evsel`; other referenced types come from included browser/hist headers. Consumers are primarily `browsers/hists.c` and code that launches block histogram browsers.

## Risks and Test Signals

Risks are ABI drift between this struct and its implementation, especially selection and row-count fields. Compile coverage catches declaration mismatches; runtime coverage should exercise selection, filtering, and block browser paths.
