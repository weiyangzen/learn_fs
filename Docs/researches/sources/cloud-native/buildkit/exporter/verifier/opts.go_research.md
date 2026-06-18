# sources/cloud-native/buildkit/exporter/verifier/opts.go

Purpose: captures frontend request options into solver result metadata so exporter verification can compare requested platforms/labels/request id against produced results.

Important APIs: `RequestOpts` stores `Platforms`, `Labels`, and `Request`; `CaptureFrontendOpts` serializes request options under `verifier.requestopts`; `getRequestOpts` deserializes them.

Control flow: platform request defaults to the normalized default platform when not provided. Label options are extracted from `label:` prefixed keys. Request id is copied from `requestid`. JSON is stored in `result.Result` metadata.

State and persistence: metadata persists with the in-memory solver result and is later consumed by verifier code; no disk state.

Dependencies and integration: used with `solver/result`, containerd `platforms`, and `platforms.go` verification.

Risks and test signals: malformed metadata JSON can abort verification; default platform assumptions affect warning behavior for single-platform builds. Coverage is mainly through exporter verifier integration paths.
