<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history.go

Purpose: records build history around a solve, including frontend/exporter metadata, logs, result descriptors, provenance attestations, resource usage, errors, traces, and metrics.

Important APIs and types: `Solver.recordBuildHistory` returns a finalizer function. It builds `controlapi.BuildHistoryRecord`, calls history queue `Update` with STARTED/COMPLETE events, imports status/error blobs, opens blob writers, creates SLSA provenance with `NewProvenanceCreator`, manages trace recording through `detect.Recorder`, and records build metrics.

Control flow: initial call starts trace recording and emits a STARTED event. The returned finalizer closes job progress, copies exporter response metadata, bounds finalization to 300 seconds, concurrently creates provenance for default and named refs, imports job status from a channel, records descriptors, imports errors when present, acquires history finalizer for trace saving, records metrics, emits COMPLETE, and asynchronously saves OTLP trace blobs if available.

State and persistence: persists records and blobs through `s.history` queue; temporary releasers hold leases until record update completes. The history record is mutated through finalization with timestamps, counts, descriptors, errors, and trace metadata.

Dependencies and integration: integrates solver jobs, resources sampler, exporter descriptors, provenance, in-toto media type, tracing recorder, BuildKit history queue, and OTEL metrics.

Risks and test signals: finalization has many concurrent writers guarded by a mutex; errors in history export are converted to internal only if the build error was nil. Trace saving is asynchronous and coordinated with `AcquireFinalizer`. No direct tests in this subset, but metrics tests cover the `recordBuildCompletion` call target.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history.go -->
