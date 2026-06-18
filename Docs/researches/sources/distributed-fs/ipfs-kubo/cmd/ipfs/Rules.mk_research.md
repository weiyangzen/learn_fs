# sources/distributed-fs/ipfs-kubo/cmd/ipfs/Rules.mk

## Purpose
This Make fragment builds, installs, and coverage-instruments the `cmd/ipfs` binary.

## Important APIs, Types, And Functions
It defines `IPFS_BIN_$(d)`, appends it to `TGT_BIN`, adds command directory to `PATH`, sets ldflags for `CurrentCommit`, `taggedRelease`, and `buildOrigin`, defines install target, and creates `ipfs-test-cover` with `testrunmain` tag.

## Control Flow
Included by root `Rules.mk`, it builds the package target with Go deps and always rebuild semantics. Coverage target computes Kubo package dependencies, joins them for `-coverpkg`, and compiles a test binary.

## State And Persistence Behavior
It creates `cmd/ipfs/ipfs`, optional installed binary under `$GOBIN`, and `cmd/ipfs/ipfs-test-cover`.

## Dependencies And Integration Points
It integrates Make Go macros, Git metadata macros, package dependency discovery, and `runmain_test.go` coverage entrypoint.

## Risks And Test Signals
Risks include shell quoting in ldflags, package list size for coverage, and PATH shadowing. Signals are version metadata embedded in binaries and coverage binary creation.
