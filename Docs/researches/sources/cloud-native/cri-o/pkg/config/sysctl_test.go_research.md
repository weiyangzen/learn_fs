# sources/cloud-native/cri-o/pkg/config/sysctl_test.go

This test file verifies sysctl parsing and namespace-aware validation. It uses the shared config fixture and mutates `sut.DefaultSysctls` for each scenario.

The tests cover default empty parsing, multiple valid `key=value` entries with empty entries skipped, wrong-format failure, extra-space failure, rejection of unwhitelisted sysctls, rejection of network sysctls with host network enabled, rejection of IPC sysctls with host IPC enabled, and success for allowed net or kernel sysctls when the corresponding host namespace is not shared. State is purely in-memory on `sut`; no external files are used.

Dependencies are Ginkgo/Gomega and the config suite. Integration signal is strong for the strict parser and allowlist rules that protect host namespace safety. Risks not covered include future kernel sysctl namespace additions and full pod admission paths, but the unit tests are precise for the current table-driven behavior in `sysctl.go`.
