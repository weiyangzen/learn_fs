# Research: sources/cloud-native/containerd/internal/cri/server/test_config.go

This test-support file defines shared CRI server test constants and a baseline `testConfig`. `testRootDir` and `testStateDir` provide fake root/state directories. `testConfig` is a `criconfig.Config` with those directories, `TolerateMissingHugetlbController` enabled, default runtime name `runc`, and a single runtime configured with type `runc`, snapshotter `overlayfs`, and sandboxer `shim`.

The file has no executable control flow, no persistence, and no direct external dependencies beyond the CRI config package. It is used by `fakeRuntimeService.Config` and `newTestCRIService` to provide a consistent configuration surface for unit tests that exercise runtime config updates, sandbox status, resource updates, and other CRI server helpers.

The main integration point is test determinism: tests do not need to construct full production config and can rely on one default runtime handler. Risks are that the simplified config omits many production fields, including CNI directories, image config, stats collection periods, CDI, SELinux, NRI, and runtime feature details. Tests that depend on those fields must mutate `c.config` explicitly. There are no direct tests for this file; its signal comes through compilation and downstream unit tests that use `newTestCRIService`.
