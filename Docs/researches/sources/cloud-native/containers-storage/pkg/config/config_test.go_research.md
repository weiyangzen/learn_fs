## sources/cloud-native/containers-storage/pkg/config/config_test.go

Purpose: tests graph-driver option emission and precedence.

Important APIs/types/functions: `searchOptions`, `TestAufsOptions`, `TestBtrfsOptions`, `TestOverlayOptions`, `TestVfsOptions`, and `TestZfsOptions`.

Control flow: creates `OptionsConfig` values with top-level and driver-specific fields, calls `GetGraphDriverOptions`, and searches output strings for expected fragments.

State and persistence: pure in-memory tests.

Dependencies and integration points: validates config-to-driver option handoff for storage drivers.

Risks: assertions use substring matching and sometimes only check non-empty output, so exact key/value formatting and ordering are only partially constrained. Some failure messages have stale wording.

Test signals: broad option precedence coverage; no validation of TOML decoding. Local tests could not run because `go` is not installed.
