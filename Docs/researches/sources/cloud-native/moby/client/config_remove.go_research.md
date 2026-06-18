<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_remove.go -->
# sources/cloud-native/moby/client/config_remove.go

Purpose: removes a Swarm config by id.

Important APIs/types/functions: `ConfigRemoveOptions`, `ConfigRemoveResult`, and `Client.ConfigRemove`.

Control flow: validates the id with `trimID`, issues `DELETE /configs/{id}`, closes the response, and returns an empty future-proof result.

State and integration behavior: no local persistence; daemon-side config state is deleted. Depends on shared `delete`, `ensureReaderClosed`, and id validation.

Risks and test signals: risks are accidental id/path changes and body leaks. `config_remove_test.go` covers invalid ids, daemon error mapping, and successful route/method.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_remove.go -->
