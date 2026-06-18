<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/oss_fuzz_build.sh -->
# sources/cloud-native/containerd/contrib/fuzz/oss_fuzz_build.sh

## Purpose
OSS-Fuzz build script for compiling containerd native and libFuzzer Go fuzz targets.

## Important APIs, Types, And Functions
Defines `compile_fuzzers` shell function and build steps.

## Control Flow
Installs Go/protoc/runc dependencies, patches paths for `/tmp/containerd`, removes vendor, compiles fuzz functions discovered by git grep with native or go-fuzz builders, and sets CGO/architecture.

## State And Persistence
Mutates OSS-Fuzz build workspace, downloads toolchains, edits source files with sed, compiles binaries.

## Dependencies And Integration Points
OSS-Fuzz env vars/tools, wget, git, Go, protoc, runc build, compile_go_fuzzer helpers.

## Risks And Test Signals
Downloads pinned tool versions; source patching is build-context-specific. Validated by OSS-Fuzz build. Source size reviewed: 101 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/oss_fuzz_build.sh -->
