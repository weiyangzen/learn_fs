<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux_test.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux_test.go

Purpose: unit tests for Linux OS-release parsing, version extraction, fallback file selection, and containerization detection. Tests use temp files and package variables to simulate `/etc/os-release`, `/usr/lib/os-release`, and `/proc/1/cgroup`. State is temporary filesystem fixtures. Dependencies are gotest assertions and filepath/os helpers. Risks covered include quoted values, missing `PRETTY_NAME`, dual `VERSION_ID`, fallback behavior, and cgroup paths for host versus container. Test signal is strong for parser behavior but not for real distro edge cases beyond fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_linux_test.go -->
