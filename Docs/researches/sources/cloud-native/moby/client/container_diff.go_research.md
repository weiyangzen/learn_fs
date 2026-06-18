<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff.go -->
# sources/cloud-native/moby/client/container_diff.go

Purpose: fetches filesystem changes for a container.

Important APIs/functions: `Client.ContainerDiff`.

Control flow: validates container id, GETs `/containers/{id}/changes`, closes the response, decodes a JSON array of `container.FilesystemChange`, and returns it in `ContainerDiffResult`.

State and integration behavior: read-only daemon operation with no local persistence. Depends on `ContainerDiffOptions/Result`, shared `get`, JSON decoding, and container API types.

Risks and test signals: risks are invalid-id handling and route drift. `container_diff_test.go` covers daemon errors and successful decode.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff.go -->
