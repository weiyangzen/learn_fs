## sources/cloud-native/buildkit/util/progress/progress.go

Purpose: core context-based progress pipe abstraction for BuildKit operations.

Important APIs/types: `WriterFactory`, `FromContext`, `NewFromContext`, `NewContext`, `WithProgress`, `WithMetadata`, `Controller`, `Writer`, `Reader`, `Progress`, `Status`, `OneOff`. Internal `progressReader`/`progressWriter` implement a collapsing progress pipe.

Control flow: `NewContext` creates a reader/writer pipe and stores writer in context. `FromContext` returns a factory that creates child writers from an existing writer, or returns a `MultiWriter` as-is, or a no-op writer if no progress is present. `Read` waits on condition variable until dirty progress is available, context is canceled, or all writers close after pipe cancellation; it collapses by progress ID and returns items sorted by timestamp. Writers store last progress per ID and broadcast. Metadata options are copied/decorated into child writers. `OneOff` writes start and completion status around a call.

State/persistence: in-memory writer set and dirty map protected by mutex; closed writer has a `done` flag. No persistence. Dependencies: context, sync, time, `maps`, `slices`, `pkg/errors`.

Integration points: central for progress emitted by solvers, flightcontrol, logs, controllers, and UI. Risks: `progressWriter.done` is checked/set outside a mutex, so misuse may race; collapse-by-ID drops intermediate statuses between reads; writers must be closed to let readers finish. Test signals: `progress_test.go` covers nested progress, metadata propagation, ID collapse/final status expectations.
