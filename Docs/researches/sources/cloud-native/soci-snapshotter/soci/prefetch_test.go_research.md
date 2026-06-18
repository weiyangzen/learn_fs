# sources/cloud-native/soci-snapshotter/soci/prefetch_test.go

Purpose: this file validates the prefetch JSON artifact format and simple in-memory helpers.

Important tests: `TestNewPrefetchArtifact` verifies version initialization and empty state. `TestPrefetchArtifactAddPrefetchSpanAndIsEmpty` verifies span append behavior. `TestMarshalPrefetchArtifact_EmptyError` checks nil and empty artifacts are rejected. `TestMarshalPrefetchArtifact_Success` confirms descriptor media type, positive size, readable JSON, and round-trip field preservation. `TestUnmarshalPrefetchArtifact_Success` includes priority. Error tests cover invalid JSON and unsupported version.

Control flow and state: tests use in-memory JSON readers/writers only. They inspect decoded struct values rather than relying on digest constants.

Dependencies and integration points: imports `ztoc/compression` for `SpanID`, matching the production artifact type.

Risks and gaps: tests do not verify the descriptor digest equals the marshaled bytes, empty unmarshal rejection, malformed span ranges, priority omission, or unknown extra JSON fields. There is no interoperability fixture for a frozen JSON artifact schema.

Test signal quality: good for basic schema acceptance/rejection; limited for descriptor integrity and semantic validation.
