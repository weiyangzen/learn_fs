## sources/cloud-native/buildkit/util/progress/logs/logs.go

Purpose: converts stdout/stderr byte streams into BuildKit progress log vertices with size/speed clipping and optional local printing.

Important APIs/types: `NewLogStreams(ctx, printOutput)` returns stdout/stderr write closers plus flush function. `streamWriter` handles limits, clipping, circbuf tail, and writes `client.VertexLog`. `LoggerFromContext` returns a stderr logger function.

Control flow: env config is read once from `BUILDKIT_STEP_LOG_MAX_SIZE` and `BUILDKIT_STEP_LOG_MAX_SPEED`. `Write` computes allowed bytes based on max total size or speed-derived budget, initializes a 256 KiB circular buffer once clipping starts, emits an output-clipped message at transition, writes limited data to progress and optionally OS stdout/stderr, and reports the original byte count. `flushBuffer` emits buffered tail. `Close` closes progress writer.

State/persistence: per-stream counters, clipping flags, optional circbuf tail; package-level defaults mutate after env read. Dependencies: BuildKit progress/client, circbuf, units, identity.

Integration points: Git CLI streams and executor logs. Risks: config read once means later env changes are ignored; when clipping, returned write count hides dropped bytes intentionally; `Close` does not flush tail automatically. Test signals: no local tests in this subset.
