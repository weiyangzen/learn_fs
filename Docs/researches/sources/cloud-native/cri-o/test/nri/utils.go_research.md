<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/utils.go -->
# sources/cloud-native/cri-o/test/nri/utils.go

Purpose: support utilities for NRI tests. It discovers available CPU and NUMA memory node sets from sysfs, derives a test namespace from the Go call stack, and waits for files produced asynchronously by tests.

Important APIs and flow: `getAvailableCpuset` and `getAvailableMemset` lazily cache parsed values from `/sys/devices/system/cpu/online` and `/sys/devices/system/node/has_normal_memory`. `getXxxset` expands comma-separated ranges such as `0-3,8` into string slices. `getTestNamespace` scans callers for a function name prefixed with `Test`. `waitForFileAndRead` polls up to five seconds, sleeps a short slack period after existence, then reads the file.

State and persistence: package globals cache parsed sysfs data for the process lifetime. The helpers read host sysfs and arbitrary paths but write nothing. Risks include nil sets on hosts without the expected sysfs files, no synchronization around lazy globals, and a fixed wait timeout that can be flaky on slow environments. Test signal is its direct use by NRI integration tests that need host topology and file-event synchronization.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/utils.go -->
