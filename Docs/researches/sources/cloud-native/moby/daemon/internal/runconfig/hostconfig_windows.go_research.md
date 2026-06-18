<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_windows.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_windows.go

Purpose: implements Windows create-request hostconfig validation.

Important APIs and types: `validateNetMode`, `validateIsolation`, `validateQoS`, `validateResources`, `validatePrivileged`, and `validateReadonlyRootfs`.

Control flow: network validation applies common container-mode checks and additionally rejects container network mode with Hyper-V isolation. Isolation allows default/process/hyperv. QoS is accepted. Resource validation rejects CPU realtime period/runtime. Privileged and readonly rootfs are rejected.

State and persistence: none.

Dependencies and integration: called by `config.go` on Windows.

Risks: Windows-specific constraints are API-visible and must match daemon/runtime capabilities. QoS validation is permissive while non-Windows rejects I/O maximums.

Test signals: `config_test.go` conditionally covers isolation and privileged behavior depending on GOOS.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_windows.go -->
