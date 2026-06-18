<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_options.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_options.go

Purpose: exposes option functions for configuring the supervised containerd daemon.

Important APIs and types: `WithLogLevel`, `WithLogFormat`, `WithCRIDisabled`, and `WithDetectLocalBinary`.

Control flow: options mutate the `remote` config before startup. Info log level is normalized to an empty containerd debug level. CRI is disabled by appending its plugin ID. Local binary detection looks beside the running dockerd executable and overrides `daemonPath` when a non-directory containerd binary is found.

State and persistence: affects generated containerd config and executable path; no standalone persistence.

Dependencies and integration: consumed by `Start`; depends on containerd log format and `os.Executable`.

Risks: local binary detection is path-sensitive and returns an error if a directory exists with the expected binary name. Option ordering can matter if multiple options change the same fields.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/supervisor/remote_daemon_options.go -->
