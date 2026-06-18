# sources/cloud-native/moby/integration-cli/docker_cli_registry_user_agent_test.go

Purpose: validates that registry requests carry a combined Engine and upstream Docker client User-Agent.

Important APIs and functions: `unescapeBackslashSemicolonParens`, `regexpCheckUA`, `registerUserAgentHandler`, `registry.NewMock`, `reg.RegisterHandler`, and registry suite pull command.

Control flow: the mock registry registers a `/v2/` handler that returns 404 after recording the `User-Agent` header. The test points the daemon/CLI flow at this registry, triggers an image pull, then `regexpCheckUA` splits the header into Docker engine and `UpstreamClient` portions, unescapes punctuation, and validates both with regexes.

State and persistence: starts a mock registry and captures a header string; no images are expected to persist because the handler returns unsupported/not found.

Dependencies and integration points: internal mock registry helper, HTTP header propagation through registry client stack, environment variables for test setup, and User-Agent escaping rules.

Risks: regex checks intentionally validate shape rather than exact version, but can still break on intentional UA format changes; handler returns 404, so only the first registry negotiation path is covered.

Test signals: outgoing registry requests must include an Engine UA prefix plus an escaped upstream Docker client UA after `UpstreamClient`.
