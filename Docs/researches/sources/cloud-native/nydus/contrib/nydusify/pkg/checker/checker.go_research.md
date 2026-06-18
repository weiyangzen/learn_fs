# sources/cloud-native/nydus/contrib/nydusify/pkg/checker/checker.go

## Purpose
This file implements the high-level Nydus image checker orchestration. It parses source/target images, writes diagnostic artifacts, and runs manifest, bootstrap, and filesystem validation rules.

## Important APIs, Types, and Functions
`Opt` captures workdir, image refs, insecurity flags, backend config, multi-platform flag, binary paths, and expected architecture. `Checker` stores options plus source and target parsers. Important methods are `New`, `Check`, and internal `check`.

## Control Flow
`New` creates a target remote/parser and optionally source remote/parser. `Check` calls `check`, and if the error is retryable with HTTP, it toggles source/target remotes to HTTP and retries once. `check` parses target and optional source, removes the work directory, outputs source/target image info, creates three rule objects, and validates each in order.

## State, Persistence, and Dependencies
Persistent output is written under `WorkDir`, including manifests, configs, bootstrap contents, and rule outputs. Dependencies include provider/default remotes, parser, checker rules, utils retry logic, filesystem cleanup, and logrus.

## Integration Points
This is invoked by `nydusify check`. It integrates parser output with rules from `pkg/checker/rule`, and passes backend information to bootstrap/filesystem validators.

## Risks and Test Signals
`os.RemoveAll(WorkDir)` is destructive for the configured path. Retrying with HTTP mutates remote state after certain errors. The `MultiPlatform` option is present but not used in this file directly. Tests cover constructor failures/success, HTTP retry, cleanup/output/rule failure paths via monkeypatches.
