# Research: sources/cloud-native/buildkit/examples/gobuild/main.go

## Purpose
Programmatic Go build example using `llb-gobuild` to create BuildKit LLB for Go artifacts.

## Important APIs, Types, and Functions
`run` builds the graph. `copyAll`, `copyFrom`, and `copy` are `llb.StateOption` helpers for copying build outputs.

## Control Flow
Constructs Go build inputs, invokes the external gobuild helper, copies artifacts to a result state, marshals LLB to stdout.

## State and Persistence
No local persistent state besides stdout; BuildKit materializes artifacts/cache later.

## Dependencies and Integration Points
Depends on `client/llb` and `github.com/tonistiigi/llb-gobuild`. Demonstrates composing third-party LLB helper libraries with BuildKit.

## Risks and Edge Cases
Sensitive to llb-gobuild API/toolchain defaults and expected output paths.

## Test Signals
No direct tests; compilation and LLB solver acceptance are the main signals.
