# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_mount_test.go

## Purpose
This file validates Dockerfile `RUN --mount` behavior across bind/context mounts, tmpfs mounts, cache mounts, writable stage mounts, parser typo suggestions, variable interpolation, mount IDs, user/mode settings, duplicate context mounts, and nested cache mount parallelism. It registers `mountTests` into the global `allTests` matrix.

## Important APIs, Types, and Functions
The major tests are `testMountContext`, `testMountTmpfs`, `testMountInvalid`, `testMountRWCache`, `testCacheMountUser`, `testCacheMountDefaultID`, `testMountEnvVar`, `testMountArg`, `testMountEnvAcrossStages`, `testMountMetaArg`, `testMountFromError`, `testMountTmpfsSize`, `testMountDuplicate`, and `testCacheMountParallel`. They use `getFrontend`, `client.New`, `f.Solve`, local mounts, local exporter outputs, `integration.UnixOrWindows`, `integration.SkipOnPlatform`, and `fstest` fixtures.

## Control Flow and Assertions
Positive tests build small Dockerfiles and assert successful solves or exported file content. `testMountContext` reads a context file through a default mount. `testMountTmpfs` confirms tmpfs contents do not persist between RUN instructions. `testMountRWCache` solves twice with a changed cachebust file and expects identical output from a cached writable mount. Cache ID tests prove default IDs isolate by target and explicit IDs share across targets/stages. Variable tests verify `ENV`, `ARG`, and global meta-ARG expansion in mount attributes. Negative tests check typo diagnostics (`--mont`, `typ`, `tmp`) and reject variable expansion in `from=`.

## State, Persistence, and Dependencies
Cache mounts intentionally persist between RUN instructions and solves according to BuildKit cache semantics; tmpfs and secret-like temporary mounts must not persist. Most other state is temp-directory Dockerfile/context data and optional local exporter output. Dependencies include shell commands inside Linux/Windows base images and BuildKit cache/mount implementations.

## Integration Points
The tests cover parser flag handling, frontend mount option conversion, solver cache keys, local context mounting, stage-to-stage mounts, cache sharing across stages, environment interpolation in mount specs, and exporter output validation. `testCacheMountParallel` loops 20 no-cache solves to catch race conditions in nested cache mount setup.

## Risks and Test Signals
Key risks are stale cache reuse, mount option typo suggestions breaking, unsupported variable expansion becoming ambiguous, tmpfs persistence leaks, duplicate context source mounts failing to refresh after context changes, and parallel nested cache mounts deadlocking or colliding. Test signals include exact error substrings, repeated solve comparisons, stat checks, file existence checks, and stress-looped parallel solves.
