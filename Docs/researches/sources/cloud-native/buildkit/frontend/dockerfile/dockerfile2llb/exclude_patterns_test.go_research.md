# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/exclude_patterns_test.go

Purpose: verifies parser/converter acceptance of `--exclude` patterns for COPY and ADD.

Important tests: `TestDockerfileCopyExcludePatterns` and `TestDockerfileAddExcludePatterns` call `Dockerfile2LLB` on scratch Dockerfiles with two exclude patterns.

Control flow and state: tests only assert no conversion error; they do not solve the LLB or inspect filtered copy options.

Dependencies and integration: covers `convert_copy.go` option plumbing from parsed instruction fields to conversion.

Risks and test signals: minimal smoke coverage; deeper behavior requires integration tests that verify copied files.
