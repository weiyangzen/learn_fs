# sources/cloud-native/moby/daemon/internal/builder-next/executor_opts.go

## Purpose
Defines `executorOpts`, the shared option bag used by platform-specific `newExecutor` implementations in Moby's embedded BuildKit builder. It is intentionally unexported and spans common, Linux-only, and Windows-only fields.

## APIs, Control Flow, and Integration
The struct carries the builder root, libnetwork controller, OCI DNS config, CDI manager, proxy provider, Linux cgroup/AppArmor/rootless/userns settings, and Windows containerd namespace/address/Hyper-V settings. There is no executable flow here; the file is an integration contract consumed by `executor_*.go` and builder setup code.

## State, Dependencies, and Risks
State is in-memory configuration only. Dependencies are BuildKit OCI/network/CDI APIs, Moby libnetwork, and `moby/sys/user`. Risk is field drift: platform files must ignore unsupported fields while builder setup must populate the platform-specific subset correctly. Tests are indirect through executor construction and build execution.
