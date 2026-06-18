<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_inspect.go -->
# sources/cloud-native/moby/client/container_inspect.go

Purpose: inspects a container and returns both typed response and raw daemon JSON.

Important APIs/types/functions: `ContainerInspectOptions{Size bool}`, `ContainerInspectResult{Container container.InspectResponse, Raw json.RawMessage}`, and `Client.ContainerInspect`.

Control flow: validates id, optionally sets `size=1`, GETs `/containers/{id}/json`, and delegates decoding/raw preservation to `decodeWithRaw`.

State and integration behavior: read-only daemon operation. No local persistence. The `Size` option can cause a costly daemon-side filesystem-size calculation.

Dependencies: shared id validation, `get`, `decodeWithRaw`, and container API types.

Risks and test signals: risks include expensive size usage, not-found mapping, and raw JSON preservation. `container_inspect_test.go` covers errors, not found, invalid ids, route/query, and decode success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_inspect.go -->
