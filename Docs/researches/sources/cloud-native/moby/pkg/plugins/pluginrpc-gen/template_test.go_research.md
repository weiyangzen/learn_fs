<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template_test.go -->
# sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template_test.go

Purpose: tests `goduration` formatting used in generated source. Cases cover zero, second, minute, hour, and sub-second durations. State is pure values. Dependencies are time and testing. Risks covered are invalid Go duration expressions; broader template rendering is not directly snapshot-tested. Test signal is narrow but important for generated code validity.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/plugins/pluginrpc-gen/template_test.go -->
