# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/filer_persister.go

Purpose: small storage abstraction over filer read/write operations, used by daily-run cursor persistence while keeping cursor code testable.

Important APIs/types: `FilerStore` interface exposes `Read(ctx, dir, name)` and `Save(ctx, dir, name, content)`. `NewFilerStoreClient` wraps a `filer_pb.SeaweedFilerClient`. `filerStoreClient` implements the interface through SeaweedFS filer helpers.

Control flow: `Read` calls `filer.ReadInsideFiler`; `Save` calls `filer.SaveInsideFiler`. No retries or validation are performed here.

State and persistence behavior: this is the persistence adapter for content stored inside the filer. For this subset, the main consumer is `dailyrun.FilerCursorPersister`, which stores cursor JSON under `/etc/s3/lifecycle/daily-cursors`.

Dependencies and integration points: depends on `weed/filer` helper functions and `filer_pb.SeaweedFilerClient`. Tests inject fake `FilerStore` implementations instead of using this concrete adapter.

Risks: nil client is not checked here; errors surface from filer helper calls. Atomicity, overwrite semantics, and directory creation behavior are delegated to `SaveInsideFiler`. Any change affects both dispatcher and daily-run cursor storage consumers.

Test signals: no direct tests for this adapter in the subset. `cursor_test.go` validates the consumer via a fake store, not actual filer I/O.
