<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_create_opts.go -->
# sources/cloud-native/moby/client/container_create_opts.go

Purpose: declares option and result types for `ContainerCreate`.

Important APIs/types: `ContainerCreateOptions` with container config, host config, networking config, platform, name, and `Image` shortcut; `ContainerCreateResult` with ID and warnings.

Control flow and dependencies: no runtime control flow. Depends on Moby container/network API types and OCI platform type.

State and integration behavior: no persistence. The type shape is a public API contract consumed by `ContainerCreate`, tests, and downstream callers.

Risks and test signals: field additions are compatibility-sensitive. `container_create_test.go` and compile-time users protect basic shape and encoding expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_create_opts.go -->
