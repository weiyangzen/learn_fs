# sources/control-plane/mayastor/test/python/pool/docker-compose.yml

## Purpose
Docker Compose environment for pool tests that require direct device access.

## Important APIs, Types, And Functions
Defines a single privileged `ms0` service at `10.1.0.2` with `RUST_LOG=mayastor=trace`, reservation support, `/dev` mounted, hugepages, source tree, `/nix`, `/tmp`, and `/var/tmp`.

## Control Flow
pytest starts `ms0`; pool tests can create pools over host-visible devices or temporary files.

## State And Persistence
State includes remote Mayastor pool metadata and host device/file effects through `/dev` and `/tmp` mounts.

## Dependencies And Integration Points
Used by `pool/test_unmap.py`. Requires privileged Docker and host device access.

## Risks
Privileged `/dev` mounting gives tests broad host access. Static network naming can conflict with other suites.

## Test Signals
Container readiness with `/dev` access enables block discard/unmap behavior to be validated.
