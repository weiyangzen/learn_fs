<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_top.go -->
# sources/cloud-native/moby/client/container_top.go

Purpose: returns process information from inside a container.

Important APIs/types/functions: `ContainerTopOptions{Arguments []string}`, `ContainerTopResult` containing process titles/processes, and `Client.ContainerTop`.

Control flow: validates container id, joins/encodes process listing arguments as query data, GETs `/containers/{id}/top`, closes response, and decodes the daemon JSON process list.

State and integration behavior: read-only daemon operation with no local persistence. Depends on shared request helpers and container top response types.

Risks and test signals: risks are argument query formatting and decode shape. `container_top_test.go` covers internal errors, invalid ids, route/query, and successful decoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_top.go -->
