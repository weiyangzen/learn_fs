# sources/cloud-native/moby/integration/container/isolation_windows_test.go

Purpose: Windows isolation coverage for process and Hyper-V containers, including lifecycle, exec, filesystem, network, environment, resource settings, volume mounts, and coexistence.

Important APIs and flow: Tests run containers with `container.WithIsolation(IsolationProcess)` or `IsolationHyperV` and long-running `ping`. Validation functions inspect `HostConfig.Isolation` and `State.Running`, exec `cmd` or `ping`, create/read files, inspect environment variables and CPU count, and check resource fields such as `CPUShares`, `NanoCPUs`, `Memory`, and `CPUCount`. Volume coverage creates a named volume and mounts it at `C:\data`; Hyper-V resource coverage checks memory configuration.

State and dependencies: Creates Windows containers, named volumes, files inside containers, and isolated runtime state. It assumes Windows images and commands are available; timeouts are longer for Hyper-V.

Risks and signals: It provides broad Windows runtime smoke and configuration persistence coverage. Failures can reveal isolation-mode regressions, HCS execution problems, resource config loss, or volume mount failures.
