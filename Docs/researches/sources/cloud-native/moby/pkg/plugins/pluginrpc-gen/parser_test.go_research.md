<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser_test.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser_test.go

Purpose: unit tests for `pluginrpc-gen` parser behavior using fixture interfaces. Tests cover empty interfaces, non-interface errors, one/multiple functions, unnamed return rejection, embedded interfaces, parsed imports including aliases, skipped functions, and timeout annotations including multiline comments. State is parser output structs and global skip function map. Dependencies are filepath/runtime fixture path resolution and test helpers. Risks covered include AST shape handling and import resolution; generated source execution is not tested here. Test signal is strong for parser contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/parser_test.go -->
