
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_fuzz_test.go -->
# sources/cloud-native/containerd/internal/cri/server/images/image_fuzz_test.go

## Purpose

This fuzz test exercises `ParseAuth` against arbitrary CRI `AuthConfig` structures and host strings to find panics or unexpected crashes in auth parsing.

## Important APIs, Types, and Functions

The file defines `FuzzParseAuth`. It uses `github.com/AdaLogics/go-fuzz-headers` to populate a `runtime.AuthConfig` and host string, then calls `ParseAuth`.

## Control Flow

For each fuzz input, the consumer attempts to generate an auth struct and a host. If either generation step fails, the input is skipped. Otherwise, `ParseAuth` is called and its returned username, secret, and error are intentionally ignored.

## State and Persistence Behavior

The fuzz target has no persistent state. It only constructs data in memory and calls the parser.

## Dependencies and Integration Points

Dependencies include the CRI runtime API and the local `ParseAuth` implementation in `image_pull.go`. This fuzz target complements table tests for known auth formats.

## Risks and Edge Cases

Because return values are ignored, the fuzz test catches panics and severe parser issues but not semantic regressions. It depends on struct generation quality to reach combinations such as malformed base64, invalid server URLs, identity tokens, and username/password mixtures.

## Test Signals

Useful fuzz findings would include panics on malformed URLs or base64, unexpected memory growth from decoded auth length handling, and unsafe handling of unusual host strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/image_fuzz_test.go -->
