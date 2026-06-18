<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_create.go -->
# sources/cloud-native/moby/client/container_create.go

Purpose: creates containers and normalizes selected inputs before sending a daemon create request.

Important APIs/functions: `Client.ContainerCreate`, helper `formatPlatform`, `normalizeCapabilities`, `normalizeCap`, and `allCapabilities`.

Control flow: defaults nil `Config` to an empty config, supports `options.Image` as a shortcut for `Config.Image`, rejects both image fields being set, requires an image, normalizes `HostConfig.CapAdd/CapDrop`, adds `platform` and `name` query values, posts a `container.CreateRequest` to `/containers/create`, closes response, and decodes ID/warnings.

State and integration behavior: no local persistence; daemon creates container state. Mutates the provided `HostConfig` capability slices in-place when non-nil, while copying `Config` when applying the `Image` shortcut to avoid mutating caller config.

Dependencies: container/network API types, Open Containers platform spec, containerd errdefs, shared request helpers, sorting/string normalization.

Risks and test signals: risks include caller-visible HostConfig mutation, capability normalization drift, image shortcut ambiguity, and multi-platform formatting. `container_create_test.go` covers error mapping, image-not-found classification, name query, AutoRemove body behavior, connection errors, and capabilities normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_create.go -->
