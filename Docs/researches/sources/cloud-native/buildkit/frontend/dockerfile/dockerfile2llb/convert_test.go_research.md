# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_test.go

Purpose: unit-tests core Dockerfile conversion helpers and selected end-to-end conversion paths without running full BuildKit integration.

Important test coverage: simple parsing, stage target case-insensitivity, missing targets, ADD URL vs COPY URL, blank FROM errors, LLB marshaling, preserving base labels across sibling stage copy, env helpers, proxy env deterministic order, circular dependencies, base image config immutability, healthcheck history formatting, numeric and symbolic `SOURCE_DATE_EPOCH`, valid/invalid source epoch stages, extracting source ops from wrapped copy states, and rewriting source states.

Control flow and state: tests call `Dockerfile2LLB` for in-memory Dockerfiles and lower-level helpers directly. Some tests resolve real image metadata for busybox base image config, so they are more integration-like.

Dependencies and integration: validates interactions across parser, dispatch, image metadata, epoch helper, LLB marshal, and linter-adjacent behavior.

Risks and test signals: strong signals for dependency cycles, mutation aliasing, proxy reproducibility, and epoch behavior. Does not cover every instruction, so integration tests complete coverage.
