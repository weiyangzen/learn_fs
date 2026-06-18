<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/opts_test.go -->
# sources/cloud-native/moby/daemon/internal/opts/opts_test.go

Purpose: validates boolean set option parsing and named option metadata.

Important APIs and types: `TestSetOpts` and `TestNamedSetOpts`.

Control flow: both tests parse `=1`, `=true`, `=0`, `=false`, and bare key forms, compare the resulting map and string, then assert parse errors for invalid bools, empty bools, and empty keys.

State and persistence: uses in-memory maps only.

Dependencies and integration: uses `gotest.tools/assert`.

Risks: expected string depends on map formatting and insertion behavior, which can be brittle if Go map display changes.

Test signals: good coverage of accepted and rejected option syntaxes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/opts/opts_test.go -->
