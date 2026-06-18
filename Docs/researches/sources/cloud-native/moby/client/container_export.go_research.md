<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_export.go -->
# sources/cloud-native/moby/client/container_export.go

Purpose: exports a container filesystem as a tar stream.

Important APIs/types/functions: `ContainerExportOptions`, `ContainerExportResult` interface, `Client.ContainerExport`, private `containerExportResult`, and interface assertions.

Control flow: validates container id, GETs `/containers/{id}/export`, and returns `resp.Body` wrapped in a result type. The response body is not closed inside the method because ownership is transferred to the caller.

State and integration behavior: read-only daemon stream with no local persistence. Depends on shared `get`, `newCancelReadCloser` if used similarly in implementation, and `io.ReadCloser` semantics.

Risks and test signals: risks are stream leaks and incorrect not-found/error mapping. `container_export_test.go` covers daemon errors, invalid ids, route/method, body content, and caller close behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_export.go -->
