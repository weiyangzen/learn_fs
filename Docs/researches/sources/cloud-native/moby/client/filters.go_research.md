<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/filters.go -->
# sources/cloud-native/moby/client/filters.go

Purpose: provides a small filter builder and URL encoder for Docker API filter maps.

Important APIs/types/functions: `Filters map[string]map[string]bool`, `Add`, `Clone`, and private `updateURLValues`.

Control flow: `Add` lazily creates nested maps and marks each supplied value true. `Clone` deep-copies the nested maps. `updateURLValues` JSON-encodes the filter map and sets it as the `filters` query parameter, including an empty string for nil/empty filters.

State and integration behavior: filters are caller-owned in-memory maps. No persistence. The helper integrates with list/prune APIs for configs, containers, images, networks, tasks, and similar endpoints.

Dependencies and risks: depends on JSON encoding and `url.Values`. Risks include map aliasing without `Clone`, unstable expectations around empty filters, and silently ignored JSON marshal errors if impossible map shape assumptions change. `filters_test.go` covers add, clone isolation, and query encoding.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/filters.go -->
