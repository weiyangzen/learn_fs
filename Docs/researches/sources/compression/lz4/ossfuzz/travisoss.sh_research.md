# sources/compression/lz4/ossfuzz/travisoss.sh

## Purpose
`travisoss.sh` regression-tests the OSS-Fuzz integration by cloning the OSS-Fuzz repository and building LZ4 fuzzers through its Docker-based helper workflow.

## Important APIs, Types, And Functions
The script uses `git clone`, `sed -i`, and `python infra/helper.py build_image --pull lz4` followed by `python infra/helper.py build_fuzzers lz4`. It reads Travis CI variables `TRAVIS_PULL_REQUEST`, `TRAVIS_BRANCH`, `TRAVIS_PULL_REQUEST_BRANCH`, and `TRAVIS_PULL_REQUEST_SLUG`.

## Control Flow
With `set -ex`, the script clones OSS-Fuzz into `/tmp/ossfuzz`, checks that the LZ4 project exists, rewrites the project Dockerfile to build the current branch or pull-request branch, then invokes OSS-Fuzz image and fuzzer builds.

## State, Persistence, And Dependencies
It writes a full clone under `/tmp/ossfuzz` and mutates `/tmp/ossfuzz/projects/lz4/Dockerfile`. It depends on git, Docker-capable OSS-Fuzz helper scripts, Python, GNU sed behavior, and Travis environment variables.

## Integration Points
This script validates `ossfuzz.sh` and the upstream OSS-Fuzz project configuration against the current LZ4 branch or PR.

## Risks
It is Travis-specific and may not work unchanged in other CI systems. `sed -i` syntax is GNU-style. The script always clones into a fixed `/tmp/ossfuzz` path and does not clean it first.

## Test Signals
Successful image and fuzzer builds are the primary signal. Failure to find the LZ4 project, Dockerfile rewrite errors, or helper build failures indicate integration drift.
