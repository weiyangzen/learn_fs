# sources/distributed-fs/ceph-client/tools/perf/ui/browsers/map.h

## Purpose

`map.h` exposes the TUI map browser entry point.

## Important APIs, Types, and Functions

It forward-declares `struct map` and declares `int map__browse(struct map *map)`.

## Control Flow and State

There is no runtime behavior here. The header defines the integration contract for callers that want to inspect a map's symbols interactively.

## Dependencies and Integration Points

It is included by the histogram browser and implemented by `map.c`.

## Risks and Test Signals

The risk surface is limited to declaration drift. Build coverage of `browsers/hists.c` and `map.c` validates it.
