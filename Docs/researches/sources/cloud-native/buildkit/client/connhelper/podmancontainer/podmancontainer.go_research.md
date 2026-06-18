# sources/cloud-native/buildkit/client/connhelper/podmancontainer/podmancontainer.go

Purpose: connection helper for `podman-container://<container>` URLs, tunneling BuildKit client traffic through `podman exec`.

Important APIs/types/functions: `init` registers `podman-container`; `Helper` returns a `ConnectionHelper` that runs `podman exec -i <container> buildctl dial-stdio`; `SpecFromURL` extracts and requires the hostname as container name.

Control flow: parser rejects empty host; dialer launches the external command through `commandconn` using background context.

State and persistence: no persistent state except registration. Runtime depends on local Podman and the target container.

Dependencies/integration points: shared `connhelper`, Docker CLI `commandconn`, Podman CLI, and in-container BuildKit `dial-stdio`.

Risks/test signals: no query options or validation beyond non-empty container. Background context affects cancellation semantics. Unit tests cover valid and missing container parsing only.
