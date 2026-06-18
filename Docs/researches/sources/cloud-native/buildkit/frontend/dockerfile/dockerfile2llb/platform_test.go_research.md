# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/platform_test.go

Purpose: unit-tests platform option resolution.

Important tests: `TestResolveBuildPlatforms`, `TestResolveTargetPlatform`, and `TestImplicitTargetPlatform`.

Control flow and state: constructs `ConvertOpt` combinations with/without `TargetPlatform` and `BuildPlatforms`, then asserts derived build platforms, target platform, and implicit target flag.

Dependencies and integration: protects platform defaults used by Dockerfile stage resolution and automatic build args.

Risks and test signals: covers selection logic but not `defaultArgs` values or platform auto-detection from base image config.
