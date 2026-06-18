# sources/cloud-native/nydus/contrib/nydusify/pkg/copier/copier_test.go

Purpose: unit coverage for copier helper behavior and early Copy error paths.

Important APIs under test: `getPlatform`, `getLocalPath`, `hosts`, `Copy`, and `pushBlobFromBackend` media type validation.

Control flow and state: tests validate default and explicit platform formatting, `file://` detection and absolutization, host credential/insecure mapping, unsupported backend type errors, invalid platform parsing, invalid source references, and unsupported media types for backend blob injection.

Dependencies and integration points: containerd platform formatting, Harbor remote credential function type, OCI descriptors, digest helpers, and local filesystem path handling.

Risks and test signals: tests document that `file://` with an empty suffix maps to the current working directory and that same source/target keys cause target insecurity to overwrite source insecurity in the map. The tests do not exercise successful registry copy, bootstrap inspection, backend blob upload, or multi-platform index push.
