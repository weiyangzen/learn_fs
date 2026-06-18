<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_unix.go -->
# sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_unix.go

Purpose: implements non-Windows create-request hostconfig validation.

Important APIs and types: `validateNetMode`, `validateIsolation`, `validateQoS`, `validateResources`, `validatePrivileged`, and `validateReadonlyRootfs`.

Control flow: network validation adds UTS/hostname and host-network/links conflict checks after common container-mode validation. Isolation allows only valid default-like isolation. QoS rejects I/O maximum bandwidth/IOPS. Resource validation checks CPU realtime support and period/runtime ordering and rejects negative CPU shares only when CPU shares are supported. Privileged and readonly-rootfs are accepted.

State and persistence: none.

Dependencies and integration: called by `validateCreateRequest` in `config.go`.

Risks: some unsupported resource settings are intentionally not rejected for backward compatibility and may fail later at runtime. Error text includes `runtime.GOOS`.

Test signals: `hostconfig_test.go` covers selected resource cases; `config_test.go` covers isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/runconfig/hostconfig_unix.go -->
