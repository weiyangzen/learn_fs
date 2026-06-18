<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/distribution_inspect_test.go -->
# sources/cloud-native/moby/client/distribution_inspect_test.go

Purpose: tests validation behavior for `DistributionInspect`.

Important coverage: empty image reference should return a not-found style error rather than issuing a malformed request.

Control flow and dependencies: constructs a client and calls the method with an empty string, using gotest assertions for error class.

State and risks: no persistence. This test protects a narrow validation branch; method/path success coverage is comparatively limited here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/distribution_inspect_test.go -->
