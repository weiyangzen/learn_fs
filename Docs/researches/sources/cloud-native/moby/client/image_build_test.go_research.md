<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_build_test.go -->
# sources/cloud-native/moby/client/image_build_test.go

Purpose: validates build request construction, option query encoding, headers, errors, and returned stream behavior.

Important coverage: daemon internal errors, expected `POST /build`, tar content type, registry auth config header, tags and selected query values, JSON-encoded option fields, single-platform behavior, invalid multi-platform rejection, and response body reading.

Control flow and dependencies: tests provide a build context reader, inspect the request in a mock transport, and read the returned body.

State and risks: no persistence. The suite is high-signal because build options have many compatibility-sensitive query encodings and can include credentials.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_build_test.go -->
