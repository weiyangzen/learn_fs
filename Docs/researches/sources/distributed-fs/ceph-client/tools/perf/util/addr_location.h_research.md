# sources/distributed-fs/ceph-client/tools/perf/util/addr_location.h

## Purpose

`addr_location.h` defines `struct addr_location`, perf's resolved-address carrier.

## Important APIs, Types, and Functions

The struct stores thread, maps, map, symbol, address, object address, filtered flag, CPU, socket, and related fields. It declares init/exit/copy helpers.

## Control Flow and State

There is no runtime flow. The header defines ownership-sensitive pointer fields that implementation code reference-counts.

## Dependencies and Integration Points

It forward-declares thread/maps/map/symbol types and is included by sample processing and hist code.

## Risks and Test Signals

Risks are adding pointer fields without updating copy/exit semantics. Build plus reference-count tests around sample resolution validate it.
