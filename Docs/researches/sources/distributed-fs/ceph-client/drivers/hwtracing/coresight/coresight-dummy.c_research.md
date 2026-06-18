# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-dummy.c

## Purpose
`coresight-dummy.c` provides lightweight CoreSight dummy source and sink devices for topologies where a real endpoint is absent or where a placeholder is needed for testing and graph completion.

## Important APIs, Types, And Functions
`struct dummy_drvdata` stores the parent device, registered CoreSight device, and optional trace ID for dummy sources. Source callbacks are `dummy_source_enable()`, `dummy_source_disable()`, and `dummy_source_trace_id()`. Sink callbacks are `dummy_sink_enable()` and `dummy_sink_disable()`. A read-only `traceid` sysfs attribute is exposed for dummy sources.

## Control Flow
Probe distinguishes `arm,coresight-dummy-source` from `arm,coresight-dummy-sink`. For a source, it allocates a CoreSight source name, sets source subtype `OTHERS`, installs source ops, and obtains either a static trace ID from device tree or a dynamic system trace ID. For a sink, it allocates a sink name and registers subtype `DUMMY`. Both paths load CoreSight platform data, register the device, and enable runtime PM. Remove releases any valid trace ID, disables runtime PM, and unregisters the CoreSight device.

Enable for a dummy source uses `coresight_take_mode()` to prevent conflicting modes and otherwise only logs; disable sets mode back to disabled. Dummy sink operations log and return success without hardware programming.

## State And Persistence
The only meaningful persistent state is the source trace ID and CoreSight mode. There is no hardware buffer or register state. The trace ID is held for the lifetime of a dummy source and returned to the trace ID allocator on remove.

## Dependencies And Integration Points
The driver depends on OF compatible strings, CoreSight platform data, CoreSight registration, trace ID allocation, and runtime PM. It integrates with normal CoreSight path construction as either a source or sink.

## Risks
Dummy devices can make a topology appear valid while no real trace capture or generation occurs. Static trace ID conflicts are delegated to the trace ID allocator; failures abort probe. Source ops do not include perf-specific behavior beyond mode ownership, so tests should not treat dummy trace as real data.

## Test Signals
Tests should cover source and sink probe, static and dynamic trace ID allocation, trace ID sysfs read, mode conflict on enable, remove-time ID release, and path construction through dummy endpoints.
