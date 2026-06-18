# sources/cloud-native/stargz-snapshotter/recorder/recorder.go

Purpose: Provides a small thread-safe JSON log recorder for recording file/layer access entries.
Important APIs/types/functions: `Entry` with `Path`, optional `ManifestDigest`, and optional `LayerIndex`; `New(io.Writer)`; and `(*Recorder).Record`.
Control flow: `New` wraps an output writer in `json.Encoder`; `Record` serializes access through a mutex and emits one JSON object per call.
State and persistence: state is the encoder and mutex. Persistence is delegated to the caller-provided writer, so durability, buffering, and close semantics are external.
Dependencies and integration points: useful for optimizer/access tracing flows that need newline-delimited JSON access records. It only depends on Go standard library `encoding/json`, `io`, and `sync`.
Risks: no nil checks for recorder, writer, or entry; writer errors are returned from `Encode`. Because entries are written immediately and locked, high-frequency recording can become serialized on one mutex.
Test signals: no direct tests in this subset; behavior is simple enough for targeted unit tests around concurrent `Record` calls and JSON shape.
