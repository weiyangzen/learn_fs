## sources/cloud-native/buildkit/util/progress/controller/controller.go

Purpose: reference-counted progress controller for a named vertex and status updates.

Important type/API: `Controller` implements `progress.Controller` with `Start(ctx) (context.Context, done)` and `Status(id,action) func()`. Fields include digest/name/writer factory/progress group.

Control flow: `Start` increments count under mutex. On first active start it initializes start time, writer, and vertex ID, then writes a started vertex if digest is set. It returns a context carrying the writer and a done func. The done func decrements count; when zero it writes completed vertex with optional error string, closes writer, and clears state. `Status` writes start/completion status around an action using the current writer when present.

State/persistence: in-memory count, timestamps, writer, ID protected by mutex; progress is emitted to configured writer. Dependencies: BuildKit client vertex types, identity, solver progress group, OCI digest.

Integration points: used by code that wants nested operations to share one visible progress vertex. Risks: `Status` reads `c.writer` without locking, so races are possible if used concurrently with `Start`/done; missing `WriterFactory` would panic when called. Test signals: no direct controller tests in this subset.
