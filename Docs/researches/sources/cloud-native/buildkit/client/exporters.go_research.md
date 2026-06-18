# sources/cloud-native/buildkit/client/exporters.go

Purpose: defines public exporter type constants and parsing for local exporter modes.

Important APIs/types/functions: exporter constants `image`, `local`, `tar`, `oci`, and `docker`; `LocalExporterMode` with `copy` and `delete`; `ParseLocalExporterMode` normalizes input and validates supported mode.

Control flow: parser trims whitespace, lowercases input, maps empty string to `copy`, accepts `copy` and `delete`, and returns an error for anything else.

State and persistence: none.

Dependencies/integration points: used by client solve/export configuration and local exporter behavior selection; depends on `strings` and `pkg/errors`.

Risks/test signals: empty defaults to copy, which is compatibility-sensitive. No direct tests in this subset, but invalid mode errors protect callers from silent behavior changes.
