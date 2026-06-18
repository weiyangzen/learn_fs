# sources/distributed-fs/ceph/src/osd/osd_tracer.h

## Purpose

`osd_tracer.h` declares the OSD subsystem's global tracing hook. It lets OSD source files share a common `tracing::Tracer` instance without including or defining storage themselves.

## Important APIs and Types

The public symbol is `extern tracing::Tracer tracer` in namespace `tracing::osd`. The type comes from `common/tracer.h`.

## Control Flow

The header has no executable flow. Including code can reference `tracing::osd::tracer`; the storage is supplied by `osd_tracer.cc`.

## State and Persistence Behavior

The declaration represents process-local tracing state. No persistent state is encoded here. Trace emission, sampling, and export behavior are delegated to the common tracing implementation and runtime configuration.

## Dependencies and Integration Points

The only dependency is `common/tracer.h`. This header should be included by OSD code that needs subsystem-level tracing, and it must remain paired with exactly one definition in `osd_tracer.cc`.

## Risks and Test Signals

Risks include namespace drift, missing definition during build changes, and accidental additional definitions. Test signals are compile/link coverage for OSD targets and runtime tracing smoke tests that verify spans can be emitted through the OSD tracer.
