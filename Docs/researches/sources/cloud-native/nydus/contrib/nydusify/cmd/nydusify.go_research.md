# sources/cloud-native/nydus/contrib/nydusify/cmd/nydusify.go

## Purpose
This is the main `nydusify` CLI. It converts OCI images to Nydus images, checks Nydus images, generates chunk dictionaries, mounts/views images, builds RAFS from directories, copies images, optimizes Nydus images, and commits container changes.

## Important APIs, Types, and Functions
Important helpers include `isPossibleValue`, `parseBackendConfig`, `getBackendConfig`, `addReferenceSuffix`, `getTargetReference`, `getCacheReference`, `getPrefetchPatterns`, `validateSourceAndTargetArchives`, `setupLogLevel`, `getGlobalFlags`, and `tryReverseConvert`. `main` defines the urfave CLI app and commands. It dispatches into packages `converter`, `checker`, `generator`, `viewer`, `packer`, `copier`, `optimizer`, and `committer`.

## Control Flow
Startup configures log formatting, creates a CLI app, registers global flags, then builds command definitions. The `convert` action validates archives, target reference, backend config, cache options, fs version, prefetch patterns, optional chunk dict, OCI media type flags, optional reverse conversion, then constructs `converter.Opt` and calls `converter.Convert`. `check` builds source/target parsers and `checker.Opt`. Other commands similarly parse flags and hand off to package-level workflows. At the end, unsupported architectures abort before `app.Run`.

## State, Persistence, and Dependencies
Persistent state is created by delegated workflows in work directories, registries, archives, or storage backends. This file itself manages CLI flag state and logging output. Dependencies include OCI reference parsing, human size parsing, logrus, urfave CLI, and many local packages.

## Integration Points
This is the top-level integration surface for Nydus image lifecycle tooling. It maps environment variables and flags into lower-level package option structs, handles registry backend defaults for mount/optimize, and controls version strings injected by the Makefile.

## Risks and Test Signals
Risk concentrates in flag conflict handling, inconsistent backend env var names, backend config validation, archive path validation, and large command surface complexity. `--reverse` always attempts reverse conversion rather than detecting format. `getPrefetchPatterns` reads stdin when enabled, which can block interactive use. Tests cover helper validation, backend config parsing, target/cache references, prefetch conflicts, log files, and archive validation, but not full command execution against registries.
