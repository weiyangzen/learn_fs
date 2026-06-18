<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_resize.go -->
# sources/cloud-native/moby/client/container_resize.go

Purpose: resizes container or exec TTY dimensions.

Important APIs/types/functions: `ContainerResizeOptions{Height, Width uint}`, `ContainerResizeResult`, `ExecResizeOptions`, `ExecResizeResult`, `Client.ContainerResize`, and `Client.ExecResize`.

Control flow: each method builds `h` and `w` query values, posts to `/containers/{id}/resize` or `/exec/{id}/resize`, closes the response, and returns an empty result. Container resize validates the container id; exec resize uses the exec id path directly.

State and integration behavior: no local persistence; daemon adjusts terminal state. Depends on shared `post`, query encoding, and id validation.

Risks and test signals: risks are swapped width/height query keys and missing id validation. `container_resize_test.go` covers both endpoints, error mapping, and query values.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_resize.go -->
