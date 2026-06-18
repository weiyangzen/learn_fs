# sources/cloud-native/buildkit/client/connhelper/ssh/ssh.go

Purpose: connection helper for `ssh://` URLs, connecting to a remote BuildKit endpoint by running `buildctl dial-stdio` over SSH.

Important APIs/types/functions: `init` registers `ssh`. `Helper` turns a parsed `Spec` into a dialer running `ssh [-l user] [-p port] -- <host> buildctl [--addr unix://<socket>] dial-stdio`. `Spec` contains user, host, port, and optional socket path. `SpecFromURL` extracts URL components, rejects plaintext passwords, missing hosts, query strings, and fragments.

Control flow: URL user info may only contain username; path becomes a Unix socket override; raw query and fragment are disallowed to avoid ambiguous or unsupported settings. Dialer uses background context and argument-vector construction.

State and persistence: no persistent state except registry entry. Runtime state is the SSH session and optional remote Unix socket.

Dependencies/integration points: shared `connhelper`, Docker CLI `commandconn`, local `ssh` binary, remote `buildctl`, and BuildKit daemon address selection.

Risks/test signals: plaintext password rejection avoids credential leakage. Path-as-socket is Unix-specific and prepends `unix://`. Host/user/port are delegated to SSH; no validation beyond URL parsing. Unit tests cover user/port/socket, password rejection, queries/fragments, and missing host.
