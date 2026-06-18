<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_stats.go -->
# sources/cloud-native/moby/client/container_stats.go

Purpose: retrieves container resource statistics as a stream or one-shot response.

Important APIs/types/functions: `ContainerStatsOptions{Stream bool, OneShot bool}`, `ContainerStatsResult` with body and metadata, and `Client.ContainerStats`.

Control flow: validates container id, sets `stream` and `one-shot` query values according to options, GETs `/containers/{id}/stats`, and returns the body stream to the caller with response metadata. The method does not close the body on success.

State and integration behavior: read-only daemon stream; no local persistence. Depends on shared `get`, query encoding, and caller-owned `io.ReadCloser` lifecycle.

Risks and test signals: risks include leaked stats streams and incorrect one-shot semantics. `container_stats_test.go` covers daemon errors, invalid ids, route/query behavior, stream reading, and close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_stats.go -->
