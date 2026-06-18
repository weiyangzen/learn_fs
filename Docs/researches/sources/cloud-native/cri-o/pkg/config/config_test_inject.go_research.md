# sources/cloud-native/cri-o/pkg/config/config_test_inject.go

This file is guarded by `//go:build test` and exposes internal config mutation hooks for tests. Its purpose is to let tests inject mocked networking, namespace, checkpoint/restore, and cgroup-manager state without exporting those knobs in production builds.

The public test APIs are `(*Config).SetCNIPlugin`, `(*Config).SetNamespaceManager`, `(*RuntimeConfig).SetCheckpointRestore`, and `(*RuntimeConfig).SetCgroupManager`. `SetCNIPlugin` lazily initializes `c.cniManager` with `cnimgr.CNIManager` before delegating to `SetCNIPlugin`, which means it preserves the manager's shutdown semantics. `SetNamespaceManager` directly replaces the unexported `namespaceManager`. `SetCheckpointRestore` toggles `EnableCriuSupport`, and `SetCgroupManager` injects a `cgmgr.CgroupManager`.

There is no persistence beyond in-memory config fields. Dependencies are CRI-O internal managers plus `ocicni.CNIPlugin`. Integration points are test suites that need to emulate server config state and runtime dependency injection, especially checkpoint tests. The main risk is that test-only access can drift from production initialization behavior, but the build tag prevents accidental production exposure. Test signal is indirect: files such as server checkpoint tests rely on `SetCheckpointRestore` to exercise enabled and disabled paths.
