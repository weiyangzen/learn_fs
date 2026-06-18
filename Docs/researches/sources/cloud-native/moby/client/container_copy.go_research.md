<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_copy.go -->
# sources/cloud-native/moby/client/container_copy.go

Purpose: implements stat, upload, and download operations for container filesystem archives.

Important APIs/types/functions: `ContainerStatPathOptions/Result`, `CopyToContainerOptions/Result`, `CopyFromContainerOptions/Result`, `Client.ContainerStatPath`, `Client.CopyToContainer`, `Client.CopyFromContainer`, and `getContainerPathStatFromHeader`.

Control flow: stat validates container id, normalizes the path with `filepath.ToSlash`, sends `HEAD /containers/{id}/archive`, and decodes `X-Docker-Container-Path-Stat` from base64 JSON. Copy-to sends a raw tar reader with `PUT /containers/{id}/archive`, path query, default `noOverwriteDirNonDir=true`, and optional `copyUIDGID=true`. Copy-from sends `GET /containers/{id}/archive`, decodes stat headers, and returns the response body to the caller without closing it.

State and integration behavior: no local persistence, but daemon filesystem content is read or modified. Streaming responses transfer body ownership to callers; simple HEAD/PUT paths close responses internally.

Dependencies: `encoding/base64`, `encoding/json`, `filepath`, shared raw request helpers, `container.PathStat`, and error mapping in the request layer.

Risks and test signals: risks include missing stat headers, body ownership leaks, platform path separator differences, and unsafe overwrite defaults. `container_copy_test.go` covers not-found/internal errors, invalid ids, missing/invalid stat header behavior, query flags, request body forwarding, and returned stream content.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_copy.go -->
