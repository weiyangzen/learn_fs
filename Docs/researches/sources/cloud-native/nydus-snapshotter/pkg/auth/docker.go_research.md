# sources/cloud-native/nydus-snapshotter/pkg/auth/docker.go

Purpose: implements a Docker config credential provider that reads credentials from Docker CLI `config.json`, including credential-helper-backed configs through Docker's configfile API.

Important APIs and functions: constants `dockerHost` and `convertedDockerHost` map containerd's Docker Hub host `registry-1.docker.io` back to Docker config's `https://index.docker.io/v1/` key. `DockerProvider` stores a `*configfile.ConfigFile`; `NewDockerProvider` loads the default config from `DOCKER_CONFIG`/home; `CanRenew` marks this provider renewable; `GetCredentials` parses image refs and returns username/password from the loaded config.

Control flow: `GetCredentials` validates request/ref, parses host with `parseReference`, rewrites Docker Hub host when needed, calls `ConfigFile.GetAuthConfig`, rejects incomplete username/password pairs, and returns `PassKeyChain`.

State and persistence: provider state is a loaded Docker config object. The provider does not reload the file for each `GetCredentials`, but renewal creates providers through `renewableProviders`, so new provider instances can reread Docker config on renewal.

Dependencies and integration points: uses Docker CLI config packages and `parseReference`. It participates in the provider order after labels and CRI, and before kubelet/kubesecret through `buildProviders`.

Risks: token-only or helper returns that do not populate both username and password are treated as incomplete. Errors are returned for absence instead of silent nil, which is expected by the provider-chain aggregator but can produce noisy logs. The provider's loaded config can become stale if reused for long periods outside renewal reconstruction.

Test signals: `docker_test.go` verifies empty refs, invalid refs, Docker Hub host conversion, and an arbitrary registry from a synthetic Docker config.
