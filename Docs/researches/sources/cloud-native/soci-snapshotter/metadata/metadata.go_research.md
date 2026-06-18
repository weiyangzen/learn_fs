# sources/cloud-native/soci-snapshotter/metadata/metadata.go

Purpose: public metadata package contracts for storing and reading filesystem metadata for a compressed layer blob.

Important APIs/types/functions: `Attr` represents file attributes: size, modtime, symlink target, mode, UID/GID, device major/minor, xattrs, and link count. `Store` is a constructor function type. `Reader` exposes `RootID`, `GetAttr`, `GetChild`, `ForeachChild`, `OpenFile`, `Clone`, and `Close`. `File` exposes uncompressed file size/offset plus tar name/header offset/header size. `Options`, `Option`, `WithTelemetry`, `MeasureLatencyHook`, and `Telemetry` define initialization telemetry hooks.

Control flow: this file only defines interfaces and option application contracts. `NewReader` in `reader.go` applies `Option` functions and records telemetry.

State and persistence: no direct state; interfaces represent metadata persisted by the bbolt-backed implementation.

Dependencies/integration points: references `io.SectionReader`, `ztoc.TOC`, and `ztoc/compression.Offset`. The Reader interface is consumed by filesystem/lazy-read paths that need metadata lookup and file-open information.

Risks: interface methods use numeric node IDs, so callers need correct traversal through `GetChild`/`ForeachChild`. Telemetry currently only exposes initialization latency.

Test signals: `reader_test.go` and `util_test.go` validate an implementation of these contracts through `testableReader`.
