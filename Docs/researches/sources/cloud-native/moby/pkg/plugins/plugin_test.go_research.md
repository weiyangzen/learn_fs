<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/plugin_test.go -->
# sources/cloud-native/moby/pkg/plugins/plugin_test.go

Purpose: tests legacy plugin activation, storage, handler callbacks, wait behavior, `Get`, `GetAll`, and bad-plugin paths. Tests create fake plugin HTTP servers/transports, register extension handlers, populate temp registry paths, and assert manifest/implementation filtering. State includes global plugin storage/handlers, temp plugin specs, and HTTP servers; tests must reset globals carefully. Dependencies include plugin transport, TLS config, httptest, synchronization, and gotest assertions. Risks covered include activation races, handler re-run behavior, missing manifests, unsupported implementations, and registry scan loading. Test signal is strong for legacy plugin manager behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/plugin_test.go -->
