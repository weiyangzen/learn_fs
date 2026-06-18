# sources/cloud-native/buildkit/client/connhelper/dockercontainer/dockercontainer.go

Purpose: connection helper for `docker-container://<container>` URLs, allowing a client to talk to `buildctl dial-stdio` inside a Docker container.

Important APIs/types/functions: `init` registers scheme `docker-container`. `Helper` parses a `Spec` and returns a `ConnectionHelper` whose dialer runs `docker [--context=...] exec -i <container> buildctl dial-stdio` through Docker CLI `commandconn`. `Spec` stores `Context` and `Container`. `SpecFromURL` extracts query parameter `context` and the hostname as container name.

Control flow: URL parsing validates the container host is present; dialing builds optional context flags, then spawns the Docker CLI with a background context so the process can remain alive for the connection lifetime after gRPC dial setup.

State and persistence: no persistent state beyond global registration. Connections are external subprocess-backed streams into a running container.

Dependencies/integration points: uses Docker CLI `commandconn`, the shared `connhelper` registry, and `github.com/pkg/errors`. Integrates with BuildKit containers that provide `buildctl dial-stdio`.

Risks/test signals: container names are not further validated here, relying on argument-vector invocation to avoid shell interpolation. The background context means cancellation of the dial context will not necessarily terminate the helper process after connection establishment. Unit coverage in `dockercontainer_test.go` checks valid context parsing and missing container errors.
