# sources/cloud-native/containerd/pkg/oci/spec_opts.go

Purpose: main library of `SpecOpts`, the composable functions that mutate generated OCI specs for process args/env, image config, users/groups, namespaces, mounts, security, devices, and resources.

Important APIs/types/functions: `SpecOpts` and `Compose`; initialization helpers `setProcess`, `setRoot`, `setLinux`, `setResources`, `setCPU`, and `setCapabilities`; defaults (`WithDefaultSpec`, `WithDefaultSpecForPlatform`); config loaders (`WithSpecFromBytes`, `WithSpecFromFile`, `WithImageConfigArgs`); process/env opts; namespace/cgroup opts; user/group lookup helpers (`WithUser`, `WithUserID`, `WithUsername`, `WithAdditionalGIDs`, `WithAppendAdditionalGroups`, `UserFromFS`, `GIDFromFS`); capability opts; security opts; resource opts; device opts; Windows opts; `openUserFile`.

Control flow: options are closures applied in caller order. Many options lazily initialize missing spec sections, then mutate only relevant Linux or Windows branches. Image config reads the image config descriptor/blob, unmarshals OCI image JSON, applies env/args/cwd/user, and handles Windows `ArgsEscaped`.

State/persistence: no direct persistence. Some options read image content, snapshot mounts, rootfs files, env files, or spec JSON; output is an in-memory OCI spec.

Dependencies/integration: integrates with snapshot services, mount/fsview helpers, user parsing, namespaces, runtime-spec, image-spec, errdefs, and platform-specific files.

Risks: option order can silently override prior fields. Rootfs user/group lookup relies on safe fs access and read-only mounts. Resource options are no-ops on wrong platform, which can hide caller mistakes. Windows command-line escaping is subtle.

Test signals: broad tests in `spec_opts*_test.go` cover env merging, image config args, users/groups, capabilities, mounts, `/dev/shm`, resources, devices, Windows command lines, and path env defaults.
