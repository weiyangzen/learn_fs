# sources/cloud-native/moby/daemon/volume/local/local_test.go

## Purpose
Cross-platform local-driver unit tests with Windows skips for mount-dependent behavior.

## Important APIs, Types, And Functions
Covers `getAddress`, `getPassword`, `Root.Remove`, `New` reload behavior, `Root.Create`, `validateName`, option-backed tmpfs create/mount, and no-option reload compatibility.

## Control Flow
Tests parse option strings, create temporary roots, create/remove volumes including missing `_data` fallback, restart `Root` over existing directories, validate accepted/rejected names, and on privileged non-Windows systems mount tmpfs with options, verify mountinfo, increment/decrement active count, and reload persisted options.

## State And Persistence
Uses temporary volume directories and persisted `opts.json`. Mount tests create real tmpfs mounts and must unmount through production code.

## Dependencies And Integration Points
Depends on local driver, idtools, mountinfo, runtime OS checks, and test skip helpers.

## Risks
Some reload edge cases in `TestReloadNoOpts` write files at paths that appear intended to simulate malformed opts; changes to directory layout could reduce test effectiveness. Privileged mount tests skip in many CI contexts.

## Test Signals
Protects name/path containment, local driver restart discovery, mount refcount semantics, option persistence, and compatibility with empty/null option data.
