## sources/cloud-native/moby/daemon/internal/fstype/fstype_unsupported.go

Purpose: Non-Linux implementation of filesystem magic detection.

Important API: `getFSMagic(rootpath string) (FsMagic, error)` returns `FsMagicUnsupported, nil`.

Control flow and state: Build-tagged with `//go:build !linux`; no runtime branching.

Dependencies and integration: Keeps the public `GetFSMagic` API usable on unsupported platforms.

Risks: Returning nil error for unsupported detection makes platform support distinguishable only through the magic value. Callers must not treat `FsMagicUnsupported` as a real filesystem.

Persistence: None. No tests in this subset.
