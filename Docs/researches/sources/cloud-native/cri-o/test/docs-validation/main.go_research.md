# sources/cloud-native/cri-o/test/docs-validation/main.go

## Purpose
Documentation validation tool ensuring CRI-O config TOML tags, generated config template defaults, CLI flags, and manpage docs stay synchronized.

## Important APIs, Types, And Functions
Defines `entry`, `validateTags`, `validateCli`, `openFile`, `stringInSlice`, `allEntries`, `recursiveEntries`, and exclusion/mapping tables for tags and CLI options.

## Control Flow
`main` loads default config, validates TOML tags against `cfg.WriteTemplate(true)` and `docs/crio.conf.5.md`, then validates CLI flags in `internal/criocli/criocli.go` against `docs/crio.8.md`. Reflection recursively walks config structs, follows pointers/interfaces, avoids recursive private data with a seen map, extracts TOML tags, and computes default-value strings for supported types unless value validation is excluded.

## State And Persistence
Read-only against source/docs files. Exits 1 if validation fails.

## Dependencies And Integration Points
Integrates with `pkg/config.DefaultConfig`, config template generation, CLI implementation, and docs. Uses reflection heavily.

## Risks And Test Signals
Regex matching can be brittle around formatting changes and special regex characters in values. Pointer/interface recursion must avoid nil and inaccessible values. This is itself a test/CI signal for documentation drift rather than application runtime behavior.
