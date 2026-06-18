<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_others.go -->
# sources/cloud-native/moby/pkg/homedir/homedir_others.go

Purpose: non-Linux stubs for XDG-specific homedir helpers. Functions return unsupported errors except `StickRuntimeDirContents`, which cannot apply Linux runtime-dir sticky behavior. State changes are absent. Dependencies are only `errors`. Risks are low; callers must handle unsupported errors on non-Linux platforms. Test signal is compile-time portability and caller error handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_others.go -->
