# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/load.go

Purpose: provides daemon config loading from TOML streams and files.

Important APIs and flow: `Load` decodes a `Config` from an `io.Reader` using `pelletier/go-toml/v2` and wraps parse errors. `LoadFile` opens a path, returns an empty config when the file does not exist, wraps other open errors with the path, defers close, and delegates to `Load`.

State and dependencies: reads config file state but does not write. Depends on TOML decoding, standard I/O, and pkg/errors wrapping.

Risks and test signals: returning empty config for missing files is intentional and supports default startup, but can hide typoed default paths while explicit load errors still surface for non-ENOENT. `load_test.go` covers complex TOML decoding but not missing-file behavior.
