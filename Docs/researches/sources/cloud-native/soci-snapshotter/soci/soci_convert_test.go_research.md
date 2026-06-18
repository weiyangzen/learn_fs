# sources/cloud-native/soci-snapshotter/soci/soci_convert_test.go

Purpose: this file tests the descriptor-list mutation logic for adding SOCI v2 indexes into an OCI index.

Important fixtures: package-level descriptors define a Linux amd64 image manifest, two SOCI index descriptors, and copies with platform pointers assigned in `init`. `TestAddSociIndexes` runs table cases against `IndexBuilder.addSociIndexes`.

Control flow: cases cover appending a new SOCI index, preserving an identical existing SOCI index for the platform, and replacing an existing SOCI index for the same platform with a new digest. Assertions compare manifest count, digest, media type, artifact type, architecture, and OS in order.

State and persistence: purely in-memory descriptor mutation; no content store or artifact DB is involved.

Dependencies and integration points: validates part of `soci_convert.go` that is used after SOCI indexes are built and before the converted OCI index is pushed.

Risks and gaps: no test covers missing platform error, multi-platform replacement isolation, duplicate SOCI descriptors, non-SOCI artifact descriptors, nil platform on existing descriptors, full `Convert`, image annotation, new OCI index creation, GC labels, or artifact DB reference updates. The fixture uses digest strings like `sha256:1234` that are not valid full OCI digests, but the tested function only compares strings.

Test signal quality: focused and useful for the simple append/replace contract, but it does not validate the end-to-end conversion path.
