<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/filesystem_test.go -->
# sources/cloud-native/cri-o/utils/filesystem_test.go

Purpose: unit specs for filesystem helpers.

Important coverage: `GetDiskUsageStats(".")` must return positive byte and inode counts, while a missing path returns an error and zero values. `IsDirectory` succeeds on `.`, fails on the test binary path, and fails on a missing path.

State and integration: reads the test process filesystem and package working directory. Risks include assumptions about current directory contents and using `os.Args[0]` as a regular file. It does not cover symlink behavior, permission errors, or very large trees. Test signal is direct focused coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/filesystem_test.go -->
