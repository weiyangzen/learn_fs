# Research: sources/cloud-native/buildkit/cmd/buildkitd/util_linux.go

Purpose: implements Linux user namespace remap parsing for the OCI worker's experimental `UserRemapUnsupported` config.

Important API and flow: `parseIdentityMapping` returns nil for an empty string, otherwise splits at most three colon components, rejects too many components, treats the first component as a username, logs the selected subuid owner, loads identity mappings through `moby/sys/user`, and returns them.

State and dependencies: reads system subuid/subgid mapping state through user helpers. It depends on BuildKit logging and error wrapping.

Risks and test signals: comments in the caller warn that changing this should not mutate existing state directories because mappings affect ownership compatibility. The parser ignores fields after the first colon except for rejecting excess parts. No direct tests are present.
