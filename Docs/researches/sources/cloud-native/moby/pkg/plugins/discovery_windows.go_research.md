<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_windows.go -->
# sources/cloud-native/moby/pkg/plugins/discovery_windows.go

Purpose: Windows implementation of plugin spec search paths. `specsPaths` returns `%programdata%\docker\plugins`. State is environment-derived path construction. Dependencies are os and filepath. Risks include empty `programdata`, Windows path permissions, and lack of socket scanning semantics compared with Unix. Test signal is compile-time/platform behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_windows.go -->
