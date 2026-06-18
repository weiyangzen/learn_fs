<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/trace.rs -->
## sources/cloud-native/nydus/utils/src/trace.rs

### Purpose
This module provides build-time tracing helpers for Nydus image construction. It records timing points and event counters/descriptions under a global root tracer and exports a JSON summary map.

### APIs, Types, and Control Flow
`TraceClass` identifies timing and event classes and renders as JSON keys `consumed_time` and `registered_events`. `TracerClass` abstracts release to `serde_json::Value` and type-erased downcast access. `TimingTracerClass` stores point-name to elapsed seconds in a `Mutex<HashMap<String, f32>>`; `trace_timing()` wraps a closure and stores elapsed time if a timing tracer is registered. `EventTracerClass` stores `TraceEvent::Counter`, `Fixed`, or `Desc` values in an `RwLock<HashMap<_,_>>`. Macros `root_tracer!`, `register_tracer!`, `timing_tracer!`, and `event_tracer!` provide ergonomic global access.

### State, Dependencies, and Integration
`BUILDING_RECORDER` is a lazy global `BuildRootTracer` containing registered tracer classes. Event counters use `AtomicU64`, while insertion uses `RwLock` with double-check logic to avoid most races. The module depends on `serde`, `serde_json`, `thiserror`, and crate-exported macros, and is intended to be used across image build stages without plumbing tracer arguments everywhere.

### Risks and Test Signals
`register()` ignores duplicate registrations, so tests or repeated setup in one process can share prior global state. `trace_timing()` unwraps `duration_since`, which would panic on system clock anomalies. Event macro downcasts unwrap after class lookup; registering the wrong tracer type under a class would panic. Tests exercise concurrent event increments and timing inserts across threads, confirming the mutex/atomic combination produces expected counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/trace.rs -->
