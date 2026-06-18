<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_linux.go -->
# sources/cloud-native/moby/pkg/homedir/homedir_linux.go

Purpose: Linux XDG directory helpers used by rootless and plugin path logic. Important APIs are `GetRuntimeDir`, `StickRuntimeDirContents`, `GetDataHome`, `GetConfigHome`, `GetLibHome`, and `GetLibexecHome`. Control flow reads XDG env vars or falls back to `$HOME`-derived paths, silently skips sticky-bit work when `XDG_RUNTIME_DIR` is unset, resolves absolute paths, and applies sticky mode only to files under the runtime directory. State changes include `chmod` sticky bit on selected runtime files. Dependencies are filesystem/env APIs and `homedir.Get`. Risks include prefix checks needing a trailing separator, permission failures on chmod, and rootless behavior depending on env availability. Test signal is indirect through plugin discovery/rootless tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_linux.go -->
