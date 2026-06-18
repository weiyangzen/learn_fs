# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/config

Purpose: this kselftest config fragment declares kernel options needed to run IOMMUFD selftests, especially the fault-injection variant.

Important entries: `CONFIG_IOMMUFD=y` enables the tested subsystem. `CONFIG_IOMMUFD_TEST=y` enables test support. `CONFIG_FAULT_INJECTION=y`, `CONFIG_FAULT_INJECTION_DEBUG_FS=y`, and `CONFIG_FAILSLAB=y` enable kernel fault injection used by failure-path tests such as `iommufd_fail_nth`.

Control flow: there is no executable flow. Kselftest/virtme/kconfig tooling consumes this fragment when preparing a kernel config for the IOMMU selftests.

State and persistence: it is a static configuration artifact. Its effects appear in the built kernel, not in this file.

Dependencies and integration points: paired with `tools/testing/selftests/iommu/Makefile` and IOMMUFD test binaries. Requires debugfs/fault-injection support in the runtime environment for failure injection coverage.

Risks: forcing built-in `=y` may not match distro modular setups; omitting related IOMMU hardware/backend options can still leave tests skipped or unavailable depending on platform. Fault injection options are unsuitable for some production-style kernels.

Test signals: a kernel built with these options should expose IOMMUFD test functionality and fault-injection controls needed by the generated selftests.
