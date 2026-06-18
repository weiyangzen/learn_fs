# sources/cloud-native/buildkit/frontend/dockerfile/command/command.go

Purpose: enumerates Dockerfile command keywords in one package.

Important APIs: constants for `add`, `arg`, `cmd`, `copy`, `entrypoint`, `env`, `expose`, `from`, `healthcheck`, `label`, `maintainer`, `onbuild`, `run`, `shell`, `stopsignal`, `user`, `volume`, and `workdir`; `Commands` set contains all supported keys.

Control flow and state: static declarations only; no runtime behavior.

Dependencies and integration: consumed by parser/instruction or validation code elsewhere as the canonical command set.

Risks and test signals: risk is drift when adding Dockerfile instructions or labs-only features. Parser tests and command recognition tests provide signal.
