<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/http.go -->
# sources/cloud-native/moby/pkg/plugins/transport/http.go

Purpose: HTTP request factory/round-tripper wrapper for plugin clients. Important APIs are `HTTPTransport`, `NewHTTPTransport`, and `HTTPTransport.NewRequest`. Control flow ensures service paths start with `/`, creates POST requests with the plugin body, sets the plugin version `Accept` header, and overrides URL scheme/host using transport fields while delegating actual round trips to the embedded transport. State is scheme/address configuration. Dependencies are HTTP and IO. Risks include request URL construction for unusual service names, POST-only semantics, and Accept header compatibility. Test signal is `http_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/http.go -->
