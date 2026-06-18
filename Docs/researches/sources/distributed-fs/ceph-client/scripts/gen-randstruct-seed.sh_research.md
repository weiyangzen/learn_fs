# sources/distributed-fs/ceph-client/scripts/gen-randstruct-seed.sh

## Purpose
`gen-randstruct-seed.sh` creates a random seed file and a hashed-seed C header definition for randstruct builds.

## Important APIs, Types, and Functions
It reads 32 bytes from `/dev/urandom` via `od`, strips whitespace, writes the raw hex seed to `$1`, hashes that seed with `sha256sum`, and writes `#define RANDSTRUCT_HASHED_SEED "..."` to `$2`.

## Control Flow
There is no argument validation; positional arguments are expected to be output paths.

## State and Persistence Behavior
The script writes two host files and consumes system randomness. Re-running changes both outputs and therefore affects randomized layout reproducibility.

## Dependencies and Integration Points
It depends on POSIX shell plus `od`, `tr`, `sha256sum`, and `cut`. It integrates with randstruct plugin/build logic that needs a private seed and a non-secret hash.

## Risks and Test Signals
Missing arguments can redirect into empty path errors. Tool availability differs on non-GNU systems. Test output length, hash consistency with the seed file, and build reproducibility when the seed is preserved.
