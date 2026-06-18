# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert.go

Purpose: core Dockerfile-to-LLB converter. It parses Dockerfile syntax, resolves stages, platforms, build args, base images, dependencies, lints, dispatches instructions into LLB/image config mutations, tracks context path usage, and returns build, outline, lint, target-list, or convert-LLB results.

Important APIs and types: `ConvertOpt`, `Result`, `SBOMTargets`, `Dockerfile2LLB`, `Dockerfile2Outline`, `DockerfileConvertLLB`, `DockerfileLint`, `ListTargets`, `dispatchContext`, `dispatchState`, `dispatchStates`, `command`, and many `dispatch*` helpers for Dockerfile instructions. Utility functions handle env mutation, history, platform labels, context path filters, proxy env, source locations, ARG meta processing, and command names.

Control flow: `toDispatchState` validates input, initializes linter and caps, parses stages/ARGs, builds platform defaults, validates base image defaults, resolves `SOURCE_DATE_EPOCH`, builds dispatch states, resolves target and dependency graph, resolves reachable base images concurrently, initializes ONBUILD triggers, dispatches reachable stages, and finalizes image/state metadata. Instruction dispatch expands variables, reports lint warnings, and routes to specialized handlers for RUN, COPY/ADD, metadata instructions, ARG, and platform-related behavior.

State and persistence: converter state is in-memory in `dispatchState`: LLB state, Docker OCI image config/history, base image snapshot, context paths, stage dependencies, outline data, no-cache flags, command counters, epoch, and SBOM scan flags. Result persistence happens when the builder solves returned LLB.

Dependencies and integration: integrates parser/instructions, linter, dockerui config/client, image metadata resolver, containerd platforms/reference, BuildKit LLB, solver caps, source maps, and helper files in this package.

Risks and test signals: high-risk areas include stage dependency cycles, ARG/platform expansion, path filtering, ONBUILD dependency injection, implicit target platform detection, COPY from unregistered states, no-cache propagation, and image config mutation aliasing. `convert_test.go`, platform/image/expose tests, and many frontend integration tests cover this file.
