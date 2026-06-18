# sources/cloud-native/containerd/plugins/imageverifier/plugin.go

## Purpose
Registers the default `bindir` image verifier plugin.

## Important APIs, Types, And Functions
`init` registers `plugins.ImageVerifierPlugin` with ID `bindir`. `defaultConfig` returns `bindir.Config` with binary directory, maximum concurrent verifiers, and per-verifier timeout.

## Control Flow
Plugin init casts config to `*bindir.Config` and returns `bindir.NewImageVerifier`.

## State And Persistence
No persistent state is owned here. Runtime verifier behavior depends on executable files in the configured directory.

## Dependencies And Integration Points
Integrates with `pkg/imageverifier/bindir`, platform-specific `defaultPath`, and `tomlext.Duration`.

## Risks
Misconfigured or missing verifier binaries affect image verification. Timeout and concurrency defaults gate verifier process behavior.

## Test Signals
No direct tests in this subset.
