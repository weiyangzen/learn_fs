## sources/distributed-fs/ipfs-kubo/test/cli/webui_test.go

Purpose: CLI harness coverage for gateway `/webui/` error handling when the WebUI cannot or must not be served.

Important APIs and control flow: `TestWebUI` has three parallel subtests that create a single harness node, update `config.Config`, start a daemon, and call `node.APIClient().Get("/webui/")`. The cases set `Gateway.NoFetch=true`, `Gateway.DeserializedResponses=false`, and both together. State is limited to temporary repo config and daemon runtime.

Dependencies and integration points: the test drives the HTTP API/gateway path through the Kubo daemon, using `net/http` status constants and testify assertions. It depends on the WebUI gateway handler returning `503 Service Unavailable` and on stable explanatory body text.

Risks: assertions match human-facing error strings such as WebUI availability, NoFetch, deserialized response settings, pin/import advice, and release URL. This is useful regression coverage for operator guidance but can be brittle if wording changes. Test signal is priority ordering: `DeserializedResponses=false` must produce the incompatible message and suppress NoFetch messaging when both settings are present.
