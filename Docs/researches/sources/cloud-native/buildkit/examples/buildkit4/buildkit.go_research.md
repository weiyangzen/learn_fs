# Research: sources/cloud-native/buildkit/examples/buildkit4/buildkit.go

## Purpose
Example BuildKit LLB program that assembles a source-level BuildKit build graph for BuildKit, runc, and containerd artifacts.

## Important APIs, Types, and Functions
`buildOpt` carries version/output settings. `goBuildBase`, `goRepo`, `runc`, `containerd`, `buildkit`, and `prefixed` compose `llb.State` values using git sources, Go build steps, and copied outputs.

## Control Flow
`main` parses flags, builds an LLB state, marshals it to a definition, and writes stdout. Helpers fetch repositories, run Go builds, and copy selected artifacts into a prefixed result state.

## State and Persistence
No local daemon state is persisted; stdout contains the serialized LLB definition and BuildKit later owns cache/execution state.

## Dependencies and Integration Points
Depends on `client/llb` and `util/system`. Integrates with buildctl/gateway workflows that consume generated LLB.

## Risks and Edge Cases
Pinned versions and repository layouts can drift; generated graph debugging is harder than Dockerfile examples.

## Test Signals
No direct tests; signal is example compilation plus solver acceptance of emitted LLB.
