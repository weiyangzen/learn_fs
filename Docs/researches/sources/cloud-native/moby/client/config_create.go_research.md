<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/config_create.go -->
# sources/cloud-native/moby/client/config_create.go

Purpose: implements Swarm config creation through the Engine API.

Important APIs/types/functions: `ConfigCreateOptions{Spec swarm.ConfigSpec}`, `ConfigCreateResult{ID string}`, and `Client.ConfigCreate`.

Control flow: posts `options.Spec` as JSON to `/configs/create`, closes the response body, decodes `swarm.ConfigCreateResponse`, and returns only the created config ID.

State and integration behavior: no local persistence; daemon-side Swarm config state is created. Depends on shared `post`, JSON decoding, body closing, and `swarm` API types.

Risks and test signals: risks are route/body drift and decode failures. `config_create_test.go` asserts daemon errors are mapped and the successful route is `POST /configs/create`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/config_create.go -->
