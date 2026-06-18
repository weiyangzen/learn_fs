# sources/cloud-native/soci-snapshotter/scripts/check-config.sh

Purpose: verifies the checked-in default config matches output from the built `soci-snapshotter-grpc config default` command.

Important APIs/types/functions: computes root, expected `config/config.toml`, output binary under `out/soci-snapshotter-grpc`, generates a temp config, and diffs it against the checked-in file.

Control flow: create temp directory, run binary to generate default config, `diff -q`, print regeneration guidance and cleanup on mismatch, then remove tempdir on success.

State and persistence: creates and removes a temp directory; reads built binary and config file.

Dependencies/integration points: requires `out/soci-snapshotter-grpc` to be built and config generation command to be available.

Risks: failure cleanup is embedded in a shell OR expression; unexpected failures before that point may leave tempdir. The binary path must match build output.

Test signals: CI-style guard that config defaults and committed config stay in sync.
