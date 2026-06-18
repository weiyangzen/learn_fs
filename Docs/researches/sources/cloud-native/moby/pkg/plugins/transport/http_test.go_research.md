<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/http_test.go -->
# sources/cloud-native/moby/pkg/plugins/transport/http_test.go

Purpose: unit test for plugin `HTTPTransport.NewRequest`. It asserts path normalization, POST method, URL scheme/host assignment, body propagation, and version MIME accept header. State is in-memory request data. Dependencies are gotest assertions and net/http. Risks covered are request construction regressions; actual network transport behavior is not tested. Test signal is focused and fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/transport/http_test.go -->
