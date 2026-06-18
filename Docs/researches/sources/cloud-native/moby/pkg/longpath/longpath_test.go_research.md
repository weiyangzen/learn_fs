<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/longpath/longpath_test.go -->
# sources/cloud-native/moby/pkg/longpath/longpath_test.go

Purpose: tests Windows long path prefix transformation. It covers standard drive paths and UNC paths, asserting expected prefixing and avoiding duplicate prefixes. State is string-only. Dependencies are testing and strings. Risks covered are path formatting regressions; actual filesystem behavior with long paths is not exercised. Test signal is focused on path-normalization logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/longpath/longpath_test.go -->
