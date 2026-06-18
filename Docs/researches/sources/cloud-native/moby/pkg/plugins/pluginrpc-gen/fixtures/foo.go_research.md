<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/foo.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/foo.go

Purpose: parser fixture file containing many interface shapes for `pluginrpc-gen` tests. It defines empty interfaces, interfaces with named/unnamed returns, embedded interfaces, aliased imports, selector types, maps/slices/pointers, skipped methods, and timeout annotations. State and runtime behavior are irrelevant; it is source input for AST parsing tests. Dependencies include an aliased `io` import and another fixture package. Risks are fixture drift if parser capabilities change, especially unsupported aliases or unnamed returns. Test signal is high for generator parser edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/fixtures/foo.go -->
