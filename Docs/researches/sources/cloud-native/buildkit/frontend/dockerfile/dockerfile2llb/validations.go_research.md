# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/validations.go

Purpose: houses Dockerfile conversion validation and lint helpers for copy ignored files, dependency cycles, instruction casing, stage names, undefined variables/args, platform rules, duplicate singleton instructions, base image platform mismatch, and secret-looking ARG/ENV keys.

Important APIs: `validateCopySourcePath`, `validateCircularDependency`, `validateCommandCasing`, `validateStageNames`, `reportUnmatchedVariables`, `reportUnusedFromArgs`, `reportRedundantTargetPlatform`, `reportConstPlatformDisallowed`, `validateUsedOnce`, `validateBaseImagePlatform`, `validateNoSecretKey`, and `validateBaseImagesWithDefaultArgs`.

Control flow: validation mostly reports linter warnings rather than hard errors, except circular dependency detection. Dependency cycles use DFS with current path and attach command locations. Copy ignored-file warnings only run when dockerignore has no exclusions. Secret regexes are lazily initialized. Default-ARG base image validation processes ARGs without build overrides to warn about invalid defaults.

State and persistence: no durable state. `instructionTracker` records first CMD/ENTRYPOINT/HEALTHCHECK locations per stage.

Dependencies and integration: called from `convert.go` and `convert_copy.go`; uses linter rule catalog, suggest helper, parser locations, platform/reference parsers, and pattern matcher.

Risks and test signals: risks include false positives for secret names, reserved stage name case sensitivity, cycle path reporting, and dockerignore validation limits. Covered by conversion tests plus broader linter integration tests.
