# Research: sources/cloud-native/buildkit/examples/dockerfile2llb/main.go

## Purpose
CLI example that converts a Dockerfile into BuildKit LLB JSON and optional metadata.

## Important APIs, Types, and Functions
`buildOpt`, `xmain`, and `writeJSON` use `dockerfile2llb.ConvertOpt`, `imagemetaresolver`, `dockerui`, `pb.Definition`, and appcontext/logrus.

## Control Flow
Reads CLI flags and Dockerfile input, configures frontend conversion, marshals the resulting definition, and writes JSON metadata when requested.

## State and Persistence
Only writes selected JSON outputs; no BuildKit daemon or cache state is mutated.

## Dependencies and Integration Points
Depends on Dockerfile frontend internals, solver protobufs, and image metadata resolver. Useful for inspecting Dockerfile frontend output and debugging LLB translation.

## Risks and Edge Cases
Frontend internal APIs and option names can drift; missing context/image metadata surfaces as conversion errors.

## Test Signals
Indirectly covered by Dockerfile frontend conversion tests, not by this example itself.
