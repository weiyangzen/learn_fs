<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_list.go -->
# sources/cloud-native/moby/client/config_list.go

Purpose: lists Swarm configs with optional filter encoding.

Important APIs/types/functions: `ConfigListOptions{Filters Filters}`, `ConfigListResult{Items []swarm.Config}`, and `Client.ConfigList`.

Control flow: creates query values, delegates filter JSON encoding to `Filters.updateURLValues`, GETs `/configs`, closes the response, and decodes a JSON array into `Items`.

State and integration behavior: read-only daemon operation with no local persistence. Depends on shared `Filters`, `get`, JSON decoding, and Swarm types.

Risks and test signals: risks are filter serialization drift and response body leaks. `config_list_test.go` asserts route, filter query behavior for empty/non-empty filters, daemon error mapping, and decode success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_list.go -->
