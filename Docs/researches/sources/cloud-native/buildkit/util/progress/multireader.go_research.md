## sources/cloud-native/buildkit/util/progress/multireader.go

Purpose: fans out a single progress reader to multiple readers while replaying already-sent progress to late joiners.

Important APIs/types: `MultiReader`, `NewMultiReader(pr)`, `Reader(ctx)`, internal `handle`.

Control flow: `Reader` creates a new progress context/writer pair. If progress has already been sent or the main reader is done, a goroutine replays `mr.sent` to the new writer in batches, respecting context cancellation, then registers it for live updates if not done. The first `Reader` call starts `handle`, which continuously reads main progress, writes raw progress to registered writers, appends sent history, and on EOF closes all writers and marks done.

State/persistence: in-memory sent progress slice grows for lifetime; writer map and done cause protected by mutex. Dependencies: local progress primitives, `context`, `io`.

Integration points: lets multiple consumers observe solver progress streams. Risks: unbounded history growth; `handle` non-EOF errors return without closing `done`, potentially leaving readers waiting; replay loop variable shadowing is subtle but works because outer index is updated after each chunk. Test signals: no direct tests in this subset.
