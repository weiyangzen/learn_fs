# sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/version.go

Purpose: holds link-time-overridden metadata for the Dockerfile frontend binary.

Important variables: `Package`, `Version`, and `Revision` default to package path, `0.0.0+unknown`, and empty revision.

Control flow and state: no functions; values are read by `main.go` and `stack.SetVersionInfo`. The packaging Dockerfile overrides them through `-ldflags`.

Dependencies and integration: tied to release Dockerfile version stage and CLI `-version` output.

Risks and test signals: if ldflags are missing, published frontend binaries report unknown metadata. Release build checks and version smoke tests are relevant.
