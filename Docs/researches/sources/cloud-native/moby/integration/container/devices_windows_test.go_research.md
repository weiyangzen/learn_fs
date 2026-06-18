# sources/cloud-native/moby/integration/container/devices_windows_test.go

Purpose: Windows-only validation that `HostConfig.Devices` entries are propagated to HCS/hcsshim for process and Hyper-V isolation.

Important APIs and flow: `TestWindowsDevices` enumerates device string forms such as `class/<GUID>`, `class://<GUID>`, and `vpci-class-guid://<GUID>`, combines them with `container.WithWindowsDevice` and `container.WithIsolation`, creates containers, starts them, then execs a shell command that searches for `HostDriverStore/FileRepository`. It handles expected Hyper-V start failures for non-containerd runtime.

State and dependencies: Creates Windows containers with device assignments and isolation-specific host config. The observable external state is the mounted Windows driver store path. It depends on Windows daemon OS type, runtime type, and a well-known class GUID from Windows device definitions.

Risks and signals: Passing tests show device strings survive API-to-runtime translation and produce the expected mount. Failures can indicate device assignment regressions, Hyper-V support differences, or environment setup limitations.
