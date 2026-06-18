<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_inspect.go -->
# sources/cloud-native/moby/client/config_inspect.go

Purpose: implements Swarm config inspection and returns both typed and raw JSON response data.

Important APIs/types/functions: `ConfigInspectOptions`, `ConfigInspectResult{Config swarm.Config, Raw json.RawMessage}`, and `Client.ConfigInspect`.

Control flow: validates/trims the config id with `trimID`, GETs `/configs/{id}`, and uses `decodeWithRaw` to fill the typed config and preserve raw daemon JSON.

State and integration behavior: no local persistence. Depends on `trimID`, shared `get`, `decodeWithRaw`, and Swarm config API types.

Risks and test signals: risks include missing body closure through `decodeWithRaw` semantics, invalid id handling, and not-found mapping. `config_inspect_test.go` covers empty ids, daemon errors, 404 classification, and success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_inspect.go -->
