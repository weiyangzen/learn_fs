# sources/distributed-fs/ceph-client/tools/perf/util/addr_location.c

## Purpose

`addr_location.c` manages initialization, cleanup, and copying of `struct addr_location`, the perf object that binds a sampled address to thread, maps, map, symbol, CPU, and filtered state.

## Important APIs, Types, and Functions

It implements `addr_location__init`, `addr_location__exit`, and `addr_location__copy`.

## Control Flow and State

Init zeroes/sets default sentinel fields, notably `cpu = -1`. Exit drops references with `maps__zput`, `map__zput`, and `thread__zput`. Copy performs a struct copy, then increments references on maps, map, and thread in the destination.

## Dependencies and Integration Points

It depends on map, maps, and thread reference-counting APIs. Address locations are used widely during sample resolution, hist insertion, branch handling, and annotation.

## Risks and Test Signals

Risks are reference leaks or use-after-free if copy/exit balance is wrong. Tests should initialize, copy, exit, and reuse locations with null and non-null maps/map/thread references.
