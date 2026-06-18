# sources/control-plane/mayastor/.github/workflows/lint.yml

## Purpose
Reusable workflow for Rust, JS, Python, and Nix linting.

## Important Jobs and Steps
`code-linter` checks out submodules, installs Nix, sets `NIX_PATH` from `spdk-rs/nix/sources.json`, warms nix-shell, uses Rust cache, runs `rust-style.sh` with `FMT_OPTS=--check`, `rust-linter.sh`, `js-check.sh`, Black check for `test/python`, and `nixpkgs-fmt --check .`.

## Control Flow
Triggered by `workflow_call`; usually called by aggregate PR CI.

## State and Persistence
Creates build/cache artifacts on runner. Does not mutate repo because all formatters are in check/diff mode.

## Dependencies and Integration Points
Depends on Nix shell providing Rust, JS, Python, and Nix tooling. Integrates with pre-commit hooks and bors CI.

## Risks
Tool versions are controlled indirectly by Nix/submodules; submodule drift can change lint behavior. Black only checks `test/python`, not arbitrary Python files outside that tree.

## Test Signals
Success of each lint command. Re-running locally inside nix-shell should reproduce CI.
