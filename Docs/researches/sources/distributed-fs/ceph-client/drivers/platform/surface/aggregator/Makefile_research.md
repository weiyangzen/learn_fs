# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/Makefile

## Purpose

This Makefile builds the Surface Aggregator core module from controller, serial-hub, packet/request layer, parser, optional bus, and trace-support sources.

## Important APIs, Types, And Functions

`CFLAGS_core.o = -I$(src)` lets trace headers resolve through the local source directory. `obj-$(CONFIG_SURFACE_AGGREGATOR) += surface_aggregator.o` creates the aggregate object. `surface_aggregator-y` includes `core.o`, `ssh_parser.o`, `ssh_packet_layer.o`, `ssh_request_layer.o`, and `controller.o`; `surface_aggregator-$(CONFIG_SURFACE_AGGREGATOR_BUS)` conditionally adds `bus.o`.

## Control Flow

There is no runtime control flow. Kbuild links the listed objects into the `surface_aggregator` built-in object or module according to `CONFIG_SURFACE_AGGREGATOR`.

## State And Persistence

The file has no runtime state. It controls build artifacts and whether bus support is present in the resulting object.

## Dependencies And Integration Points

It integrates the aggregator Kconfig symbols with Kbuild and supports tracepoint generation in `core.o`. It assumes packet/request/parser sources exist in the same directory and are compiled into one module with shared internal headers.

## Risks

Object ordering matters for init/exit dependencies only indirectly, but omitting `bus.o` when `CONFIG_SURFACE_AGGREGATOR_BUS=y` would remove exported bus symbols. Trace include path changes can break `CREATE_TRACE_POINTS` compilation in `core.c`.

## Test Signals

Build tests with `CONFIG_SURFACE_AGGREGATOR=m/y` and `CONFIG_SURFACE_AGGREGATOR_BUS=y/n`, plus module symbol checks for bus exports, validate this file.
