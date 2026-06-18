# sources/distributed-fs/ceph-client/tools/perf/util/dlfilter.c

## Purpose
This file implements `perf script --dlfilter` loading and callback mediation. It loads user-provided shared objects, exposes a stable `perf_dlfilter_fns` helper table, converts perf internal sample/address structures into public dlfilter structs, and invokes early or normal filter callbacks with a temporarily valid context.

## Important APIs, Types, And Functions
Public functions are `dlfilter__new()`, `dlfilter__start()`, `dlfilter__do_filter_event()`, `dlfilter__cleanup()`, `get_filter_desc()`, and `list_available_dlfilters()`. Internal helpers include `find_dlfilter()`, `dlfilter__open()`, `dlfilter__close()`, `al_to_d_al()`, `dlfilter__resolve_ip()`, `dlfilter__resolve_addr()`, `dlfilter__resolve_address()`, `dlfilter__al_cleanup()`, `dlfilter__insn()`, `dlfilter__srcline()`, `dlfilter__attr()`, and `dlfilter__object_code()`.

## Control Flow
Creation resolves the filter path from an explicit path, current directory, or perf's `dlfilters` directory, then uses `dlopen()` and `dlsym()` to discover `start`, `stop`, `filter_event`, `filter_event_early`, and `perf_dlfilter_fns`. On start/stop, flags allow the filter to query arguments outside sample processing. For each event, `dlfilter__do_filter_event()` fills a public sample object, installs transient pointers to event/sample/evsel/machine/address locations, marks `ctx_valid`, calls the selected filter, and clears context validity before returning.

## State, Dependencies, And Integration
`struct dlfilter` owns the shared-object handle, resolved file path, plugin data pointer, argument vector, session pointer, callback pointers, and transient event context. Address helpers integrate with `machine__resolve()`, `thread__resolve()`, `thread__find_symbol_fb()`, `get_srcline_split()`, `perf_sample__fetch_insn()`, and `dso__data_read_offset()`. `CHECK_FLAG()` build assertions keep public dlfilter branch flags synchronized with `PERF_IP_FLAG_*`.

## Risks And Test Signals
Risks include untrusted shared-object execution, leaks if v2 `priv` address-location results are not cleaned with `al_cleanup`, use of helper callbacks outside valid context, stale instruction/source allocations owned by lower layers, and `get_filter_desc()` returning without `dlclose()` when validation fails. Tests should load filters with only early or normal callbacks, validate callback table population, exercise args in start/stop and event contexts, resolve IP/address/srcline/object code, confirm v0/v2 address cleanup compatibility, and list filters from both current and install directories.
