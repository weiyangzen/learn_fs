<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_update.go -->
# sources/cloud-native/moby/client/config_update.go

Purpose: updates an existing Swarm config specification at a particular object version.

Important APIs/types/functions: `ConfigUpdateOptions{Version swarm.Version, Spec swarm.ConfigSpec}`, `ConfigUpdateResult`, and `Client.ConfigUpdate`.

Control flow: validates id, sets `version=<Version.String()>` in the query, posts `options.Spec` to `/configs/{id}/update`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon-side config state changes subject to Swarm version concurrency. Depends on `trimID`, `post`, `ensureReaderClosed`, `url.Values`, and Swarm types.

Risks and test signals: risk is missing or wrong version query causing daemon update conflicts. `config_update_test.go` covers invalid ids, daemon errors, and method/path; query version coverage is comparatively light.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_update.go -->
