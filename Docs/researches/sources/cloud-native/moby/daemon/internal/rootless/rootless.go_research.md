<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/rootless.go -->
# sources/cloud-native/moby/daemon/internal/rootless/rootless.go

Purpose: detects whether Docker is running under RootlessKit.

Important APIs and types: `RunningWithRootlessKit() bool`.

Control flow: returns true when `ROOTLESSKIT_STATE_DIR` is non-empty.

State and persistence: reads process environment.

Dependencies and integration: used by NRI path defaults and rootless behavior toggles.

Risks: environment-variable detection can be spoofed or missing in unusual launch setups.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/rootless/rootless.go -->
