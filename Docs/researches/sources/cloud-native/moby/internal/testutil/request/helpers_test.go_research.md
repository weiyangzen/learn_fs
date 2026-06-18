<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/helpers_test.go -->
# sources/cloud-native/moby/internal/testutil/request/helpers_test.go

Purpose: unit tests for `ReadJSONResponse`. The single table-driven test covers valid JSON with plain and charset content types, malformed JSON, non-JSON content, and nil response handling. Control flow constructs synthetic `http.Response` values with controlled bodies and asserts decoded fields or error substrings. State is in-memory buffers only. Dependencies are `gotest.tools/assert` and the request package. Risks covered include content-type parsing and body decoding failures; it does not explicitly assert body closure side effects. Test signal is focused and fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/helpers_test.go -->
