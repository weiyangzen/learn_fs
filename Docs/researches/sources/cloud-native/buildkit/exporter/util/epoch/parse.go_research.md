# sources/cloud-native/buildkit/exporter/util/epoch/parse.go

Purpose: centralizes parsing of `SOURCE_DATE_EPOCH` values for exporters and frontend forwarding.

Important APIs: `Epoch` wraps `*time.Time`; `ParseBuildArgs` detects numeric frontend build args that should be forwarded; `ParseExporterAttrs` consumes exporter `source-date-epoch`; `ParseSource` reads source metadata globally or per-platform; `parseTime` parses Unix seconds.

Control flow: empty values intentionally parse to nil without error, enabling explicit clearing/override semantics. Build args are forwarded only when syntactically numeric. Exporter attrs are split into epoch and rest map. Source metadata checks per-platform keys before global keys and wraps frontend-origin errors with context.

State and persistence: no persistence; returned time values are UTC and later used to normalize filesystem mtimes or image created annotations.

Dependencies and integration: used by local, tar, and container image exporter option flows, and by frontend metadata handoff through exporter metadata keys.

Risks and test signals: risks include accepting empty values as nil, parse errors for non-numeric frontend metadata, and precedence between per-platform and global epochs. `parse_test.go` covers build-arg forwarding semantics.
