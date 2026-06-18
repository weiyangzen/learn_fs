# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/overlayutils/utils_test.go

Purpose: Tests `AppendVNIList` parsing, error handling, append semantics, and allocation behavior.

Important APIs and functions: `TestAppendVNIList` checks nil/empty/existing slices, trailing comma, invalid tokens, and a zero-allocation reuse scenario.

Control flow: table-driven tests compare returned slices and expected error substrings. The allocation subtest reuses a preallocated slice in `testing.AllocsPerRun`.

State and persistence: stateless except local slices.

Dependencies and integration points: protects utility behavior used by overlay driver and ovmanager option parsing.

Risks: does not validate VNI range, because the function itself does not. Does not cover VXLAN UDP port configuration.

Test signals: good coverage for CSV parser behavior and performance expectation.
