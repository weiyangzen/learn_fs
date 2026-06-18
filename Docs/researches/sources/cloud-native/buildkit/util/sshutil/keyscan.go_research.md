<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/keyscan.go -->
# sources/cloud-native/buildkit/util/sshutil/keyscan.go

Purpose: retrieves an SSH server host key in authorized-keys style for a hostname or host:port string.

Important APIs and types: `SSHKeyScan`, `addDefaultPort`, constants `defaultPort`, and sentinel `errCallbackDone`.

Control flow: `SSHKeyScan` creates an SSH client config with a custom host key callback. The callback records `hostname public-key` and returns the sentinel error to stop the handshake after key capture. The function adds port 22 when missing, dials TCP SSH, suppresses the expected sentinel error when a key was captured, closes any connection, and returns key/error.

State and persistence: local variable only; no known-hosts persistence.

Dependencies and integration: uses `golang.org/x/crypto/ssh`, `net`, and string formatting. Useful for Git/SSH source handling or diagnostics.

Risks: the config intentionally has no normal host-key verification because the goal is scanning. Network calls can block according to SSH dial behavior. The returned hostname strips the port.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/keyscan.go -->
