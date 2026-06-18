<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_list.go -->
# sources/cloud-native/moby/client/container_list.go

Purpose: lists containers with size/all/limit/filter options.

Important APIs/types/functions: `ContainerListOptions`, including deprecated `Latest`, `Since`, and `Before`; `ContainerListResult{Items []container.Summary}`; and `Client.ContainerList`.

Control flow: builds query parameters for supported fields (`size`, `all`, `limit`) and filter JSON, ignores deprecated fields, GETs `/containers/json`, closes response, and decodes a JSON array into `Items`.

State and integration behavior: read-only daemon operation with no local persistence. Depends on `Filters.updateURLValues`, `strconv`, shared `get`, and container summary API types.

Risks and test signals: risks include accidentally reviving deprecated fields, filter encoding drift, and boolean/int query format changes. `container_list_test.go` asserts route, query values, filters, daemon errors, and decode success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_list.go -->
