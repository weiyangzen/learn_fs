# sources/cloud-native/containerd/internal/cri/server/container_create_other_test.go

## Purpose
This non-Linux/non-Windows test fixture provides `getCreateContainerTestData` for generic create tests on other platforms. It validates only the cross-platform portions of generated specs.

## Important APIs, Types, and Functions
The file defines `getCreateContainerTestData` and references `checkMount` to satisfy shared test compilation. The returned `specCheck` validates process args, working directory, environment merging, bind mount options, and default CRI annotations.

## Control Flow, State, and Persistence
No runtime state is persisted. Tests using this helper build synthetic CRI configs and compare an in-memory OCI spec. The helper deliberately avoids Linux or Windows-only fields.

## Dependencies and Integration Points
It integrates with generic tests in `container_create_test.go` by providing platform-specific fixture data under the `!windows && !linux` build tag. It uses runtime API metadata, image-spec config, and runtime-spec mounts.

## Risks and Test Signals
The main signal is that generic create behavior continues to compile and assert core annotations on alternative platforms. Risk is limited coverage: security contexts, platform resources, and snapshot options are outside this file’s scope.
