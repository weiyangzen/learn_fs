# sources/cloud-native/soci-snapshotter/service/keychain/dockerconfig/dockerconfig.go

Purpose: credential provider backed by the local Docker CLI config.

Important APIs/types/functions: `DockerCreds` loads Docker config, maps Docker Hub hosts to `https://index.docker.io/v1/`, reads auth config, and returns either identity token or username/password. `NewDockerConfigKeychain` returns a resolver credential function ignoring image reference and using only host.

Control flow: load config from default Docker config path, normalize host, call `GetAuthConfig`, prefer identity token, otherwise return basic credentials.

State and persistence: reads Docker config each call; no in-memory cache in this file.

Dependencies/integration points: default credential source registered by `service/plugin`; integrates Docker CLI config and resolver credential chain.

Risks: config load errors are swallowed as anonymous credentials, while `GetAuthConfig` errors are returned. Per-host only lookup cannot distinguish namespace-scoped credentials.

Test signals: no direct tests; behavior is indirectly exercised by registry auth flows.
