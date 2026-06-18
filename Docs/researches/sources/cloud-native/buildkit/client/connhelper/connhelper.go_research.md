# sources/cloud-native/buildkit/client/connhelper/connhelper.go

Purpose: shared registry for client connection helpers keyed by URL scheme. It lets BuildKit clients map custom daemon URLs to a `grpc.WithContextDialer`-compatible connection function.

Important APIs/types/functions: `ConnectionHelper` exposes `ContextDialer func(context.Context, string) (net.Conn, error)`. `GetConnectionHelper` parses a daemon URL, looks up a registered scheme in package-global `helpers`, and returns nil when unsupported. `Register` installs a scheme handler.

Control flow: helper packages register themselves in `init`; caller passes a daemon URL; URL parse errors are returned; unknown schemes fall through without error; known schemes call the registered factory with the parsed URL.

State and persistence: the only state is the in-memory package-level `helpers` map. There is no locking, so registration is expected during package initialization before concurrent lookups.

Dependencies/integration points: standard `net`, `net/url`, and `context`; consumed by Docker, Podman, nerdctl, Kubernetes pod, SSH, and npipe helper packages. The returned dialer is intended for gRPC client configuration.

Risks/test signals: risks are duplicate/late registrations and concurrent map access if external packages register dynamically. The file has no direct test in this subset; scheme-specific tests validate parsing behavior in registered helpers.
