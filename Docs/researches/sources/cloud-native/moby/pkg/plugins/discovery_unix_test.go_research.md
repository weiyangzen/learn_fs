<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_unix_test.go -->
# sources/cloud-native/moby/pkg/plugins/discovery_unix_test.go

Purpose: Unix tests for local socket discovery and registry scanning. Tests create Unix sockets and non-plugin files under temp plugin directories, scan names, and verify socket-based `Plugin` resolution. State includes temporary directories and socket listeners. Dependencies include net.Unix sockets, os paths, reflect/gotest assertions. Risks covered include directory layouts, socket mode detection, and filtering non-plugin files. Test signal is strong for Unix plugin discovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/discovery_unix_test.go -->
