# sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/config

Purpose: declares kernel configuration needed for the PCI endpoint tests.

Important settings: enables `CONFIG_PCI_ENDPOINT=y`, `CONFIG_PCI_ENDPOINT_CONFIGFS=y`, and test endpoint/function drivers `CONFIG_PCI_EPF_TEST=m` and `CONFIG_PCI_ENDPOINT_TEST=m`.

Control flow/integration: consumed by kselftest/kernel config tooling to ensure the endpoint subsystem, configfs support, endpoint function test driver, and endpoint test driver are available before running `pci_endpoint_test`.

State and dependencies: no runtime state. It describes module/built-in requirements.

Risks: having these configs does not guarantee suitable hardware, endpoint configuration, or `/dev/pci-endpoint-test.0` existence; runtime can still fail or skip.

Test signals: config is declarative; pass/fail comes from build config checks and the C selftest.
