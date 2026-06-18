# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_parents_test.go

## Purpose
This file validates `COPY --parents` behavior in Dockerfile builds. It covers preserving parent paths from local context and from previous stages, pivot markers with `./`, wildcard expansion, multiple inputs, and missing-source behavior. It is registered as `parentsTests` in `allTests`.

## Important APIs, Types, and Functions
The core tests are `testCopyParents`, `testCopyRelativeParents`, and `testCopyParentsMissingDirectory`. They use local export validation, `FrontendAttrs{"target": ...}` to solve multiple stages from a single Dockerfile, `integration.UnixOrWindows` for Linux/Windows fixtures, `fstest` context construction, `client.New`, and `f.Solve`.

## Control Flow and Assertions
`testCopyParents` exports a scratch result and reads files from the output directory, proving direct and globbed local `COPY --parents` preserve expected `foo1/foo2` paths under root and `WORKDIR /test`. `testCopyRelativeParents` builds a source tree in a base stage, then solves targets named `middle`, `end`, `start`, `double`, `wildcard`, `doublewildcard`, and `doubleinputs`; each target asserts whether path prefixes before/after pivot markers are preserved. `testCopyParentsMissingDirectory` solves positive targets plus negative and wildcard-nonexistent cases, checking an exact missing file regex only for a literal nonexistent file while wildcard misses produce empty output directories.

## State, Persistence, and Dependencies
All filesystem state is produced in temporary build stages or local contexts. The tests depend on Dockerfile frontend path normalization, wildcard matching, stage filesystem snapshots, and platform-specific shell commands for assertions.

## Integration Points
The file exercises the parser and copier logic for `--parents`, local context transfer, stage-to-stage copy, target-specific solves, wildcard resolution, platform path separators, and local exporter validation.

## Risks and Test Signals
Risks include incorrect pivot trimming, accidental inclusion of too much path prefix, wildcard misses becoming hard errors, literal missing files not erroring, Windows path behavior diverging from Linux, or multi-input globs collapsing incorrectly. Test signals are per-target solve results, exported byte checks, in-build file/directory assertions, and a regex for the expected checksum/missing-path error.
