# sources/cloud-native/soci-snapshotter/scripts/install-check-tools.sh

Purpose: installs Go-based repository check tools.

Important APIs/types/functions: runs `go install github.com/kunalkushwaha/ltag@v0.2.4` and `go install github.com/vbatts/git-validation@v1.2.0`.

Control flow: print message, enable fail-fast shell, install both tools.

State and persistence: writes binaries to Go install bin path.

Dependencies/integration points: supports `check-ltag.sh`, `add-ltag.sh`, and `check-dco.sh`.

Risks: requires network and compatible Go toolchain. Pin versions may become incompatible with future Go versions.

Test signals: no direct test; failure blocks check setup.
