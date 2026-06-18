# sources/distributed-fs/ceph-client/scripts/livepatch/Makefile

## Purpose
This standalone Makefile supports livepatch developer tooling checks and is not part of kbuild proper.

## Important APIs, Types, and Functions
It defines `SHELLCHECK`, `SRCS := klp-build`, default target `help`, and target `check`.

## Control Flow
`make` defaults to `help`, printing available targets. `make check` verifies `shellcheck` was found and runs it over `klp-build` with optional `SHELLCHECK_OPTIONS`.

## State and Persistence
No persistent state; it only runs shellcheck.

## Dependencies and Integration Points
Depends on `shellcheck` for the check target and a sibling `klp-build` script. It is developer-facing under `scripts/livepatch`.

## Risks and Edge Cases
`which shellcheck` is used at parse time; PATH changes after make starts will not be reflected. The target only checks `klp-build`, not `fix-patch-lines` or `init.c`.

## Test Signals
Run `make -C scripts/livepatch help` and `make -C scripts/livepatch check` with and without shellcheck installed.
