<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_test.go -->
# sources/cloud-native/moby/pkg/homedir/homedir_test.go

Purpose: tests the basic `Get` home-directory helper. It asserts that the returned path is non-empty and is a clean path. State is environment/user lookup only. Dependencies are `filepath` and testing. Risks covered are minimal; it does not simulate missing environment variables or user lookup failures. Test signal is a smoke test for platform home resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/homedir/homedir_test.go -->
