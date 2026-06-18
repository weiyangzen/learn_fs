# Research: sources/cloud-native/buildkit/examples/nested-llb/main.go

## Purpose
Example demonstrating nested LLB construction, where a generated child definition is embedded into a parent BuildKit graph.

## Important APIs, Types, and Functions
Uses `llb` state construction and definition marshaling; the key API boundary is serialized child LLB consumed by a parent state.

## Control Flow
Builds an inner graph, serializes it, wires it into outer operations, and writes the final parent LLB definition to stdout.

## State and Persistence
No durable local state; definitions are in memory until stdout and solver state is external.

## Dependencies and Integration Points
Depends on BuildKit `client/llb` primitives. Shows frontend/client composition patterns for generated nested builds.

## Risks and Edge Cases
Nested definitions are harder to inspect and depend on solver/frontend compatibility.

## Test Signals
No direct tests; compilation and solver acceptance are the signals.
