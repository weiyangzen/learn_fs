## sources/cloud-native/moby/integration/container/cdi_test.go

Purpose: integration coverage for Container Device Interface support. Tests verify CDI device requests are persisted and applied, CDI spec dirs appear in system info, discovered devices are exposed, and `/etc/cdi` is honored even in rootless-related paths.

Control flow starts isolated daemons with `--cdi-spec-dir`, config files, or `--feature cdi`; writes sample CDI JSON specs; runs containers with `container.WithCDIDevices`; inspects `HostConfig.DeviceRequests`; reads container logs for injected env; and checks `Info.CDISpecDirs` and `Info.DiscoveredDevices`.

State includes daemon CDI feature config, spec directories/files, discovered device list, container device requests, and temporary or `/etc/cdi` host files. Dependencies include local daemon control, Linux, non-remote daemon, testdata CDI specs, system info API, and cleanup of `/etc/cdi` artifacts. Risks are host-global `/etc/cdi` mutation, rootless permission differences, Windows skips, and exact default spec-dir expectations. Test signals are expected `DeviceRequest`, `FOO=injected`, exact `CDISpecDirs`, and expected `system.DeviceInfo`.
