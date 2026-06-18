<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unsupported.go

Purpose: no-op external key listener for platforms other than Linux and FreeBSD.

Important APIs/functions: `Controller.startExternalKeyListener` returns nil; `Controller.stopExternalKeyListener` does nothing.

Control flow: no listener is created and no external namespace key is accepted.

State and persistence: none.

Dependencies and integration points: selected by `//go:build !linux && !freebsd` to satisfy controller calls on unsupported platforms.

Risks and test signals: higher-level code must account for platform support. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unsupported.go -->
