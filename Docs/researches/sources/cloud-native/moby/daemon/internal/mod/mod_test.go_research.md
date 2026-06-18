<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mod/mod_test.go -->
# sources/cloud-native/moby/daemon/internal/mod/mod_test.go

Purpose: validates module version extraction and normalization from synthetic Go build-info text.

Important APIs and types: `TestModuleVersion` table-drives calls to `moduleVersion`.

Control flow: each case parses build info text with `debug.ParseBuildInfo`, runs `moduleVersion`, and compares the returned display version.

State and persistence: no persistent state; test avoids the process-global `Version` cache by calling `moduleVersion` directly.

Dependencies and integration: covers `mod.go` behavior for Docker and BuildKit module paths.

Risks: tests focus on selected pseudo-version forms; malformed semver and additional metadata combinations are less covered.

Test signals: strong signal for intended display normalization and the deliberate empty return for replaced modules.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mod/mod_test.go -->
