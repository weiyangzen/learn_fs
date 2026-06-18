# sources/distributed-fs/ipfs-kubo/Rules.mk

## Purpose
This is Kubo's central Make rule file. It initializes target accumulators, imports shared Make fragments, selects tags, includes subdirectory rules, and defines top-level build/test/clean/help targets.

## Important APIs, Types, And Functions
Key variables include `TGT_BIN`, `CLEAN`, `COVERAGE`, `DISTCLEAN`, `TEST`, `TEST_SHORT`, `GOCC`, `PROTOC`, `GOTAGS`, and `LIBP2P_TCP_REUSEPORT`. Targets include `build`, `clean`, `mod_tidy`, `coverage`, `distclean`, `test`, `test_short`, `nofuse`, `install`, `uninstall`, `supported`, and `help`.

## Control Flow
It includes `mk/git.mk`, `mk/tarball.mk`, `mk/util.mk`, and `mk/golang.mk`, then sub-rules for `bin`, `plugin`, `test`, and `cmd/ipfs`. Coverage rules are included only when coverage-related goals are requested.

## State And Persistence Behavior
Rules create binaries, generated protobuf files, coverage output, test output, and cleanup sets. `distclean` is destructive for untracked build products through `git clean -ffxd`.

## Dependencies And Integration Points
It integrates Go, protoc, plugin/test/cmd rule fragments, `.github/build-platforms.yml`, and repo-wide environment flags.

## Risks And Test Signals
Risks include target accumulator ordering, conditional coverage inclusion, and destructive `distclean`. Signals are successful top-level build/test targets and accurate `help`/`supported` output.
