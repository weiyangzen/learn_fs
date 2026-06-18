# sources/cloud-native/buildkit/frontend/dockerfile/cmd/dockerfile-frontend/main.go

Purpose: executable entry point for the external Dockerfile frontend.

Important APIs: `init` sets stack version info from linked variables; `main` handles `-version` and otherwise runs `dockerfile.Build` via `grpcclient.RunFromEnvironment`.

Control flow: command-line parsing is minimal. Version mode prints binary name, package, version, and revision then exits. Normal mode creates an app context, runs gateway gRPC environment plumbing, logs fatal error, and panics on failure.

State and persistence: no durable state. Version variables come from `version.go` defaults or Dockerfile ldflags.

Dependencies and integration: connects the packaged frontend binary to the builder package and BuildKit gateway gRPC protocol. Imports proto encoding for registration.

Risks and test signals: risks include panic-style fatal path and stale version ldflags. Smoke tests of external frontend image and `-version` output cover this file.
