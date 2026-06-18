# sources/cloud-native/soci-snapshotter/soci/prefetch.go

Purpose: this file defines the JSON artifact format used to describe compressed spans that should be prefetched for a layer.

Important APIs and types: constants define media type `application/vnd.amazon.soci.prefetch.v1+json` and version `1.0`. `ErrEmptyPrefetchArtifact` rejects nil or empty artifacts. `PrefetchArtifact` contains version and a slice of `PrefetchSpan`. `PrefetchSpan` stores start/end `compression.SpanID` and optional future priority. `NewPrefetchArtifact`, `AddPrefetchSpan`, and `IsEmpty` manage the in-memory value. `MarshalPrefetchArtifact` returns an `io.Reader` plus OCI descriptor with digest and size. `UnmarshalPrefetchArtifact` validates JSON, version, and non-empty content.

Control flow: marshal rejects nil/empty artifacts, JSON encodes, computes digest from bytes, and returns a descriptor with the prefetch media type. Unmarshal reads all data, JSON decodes, verifies exact version, rejects empty span lists, and returns the artifact.

State and persistence: persisted form is a small JSON blob stored in a content store. Descriptor digest is content-addressed from the JSON representation. No internal mutable global state exists.

Dependencies and integration points: used by `soci_index.go` to create prefetch descriptors and artifact DB entries. It depends on zTOC compression span IDs and OCI descriptors.

Risks: no semantic validation ensures start span is less than or equal to end span or that priorities are non-negative. JSON ordering is stable for structs but any future map fields could affect digest expectations. Unmarshal reads the full reader into memory, acceptable for small artifacts.

Test signals: `prefetch_test.go` covers constructor, add/is-empty, marshal nil/empty rejection, successful marshal, successful unmarshal, invalid JSON, and unsupported version.
