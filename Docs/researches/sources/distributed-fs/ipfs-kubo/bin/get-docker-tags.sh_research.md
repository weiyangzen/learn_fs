# sources/distributed-fs/ipfs-kubo/bin/get-docker-tags.sh

## Purpose
This script computes Docker image tags that should be published for a build, without performing any Docker operations.

## Important APIs, Types, And Functions
It consumes build number, commit SHA, branch, optional Git tag, and `$IMAGE_NAME`. `echoImageName` emits `IMAGE_NAME:tag`.

## Control Flow
Release candidates emit their version tag. Stable semver tags emit version, `latest`, and `release`. `bifrost-*` branches emit sanitized branch/build/SHA tags. `master` and `staging` emit build/SHA and `*-latest` tags. Other branches print "Nothing to do."

## State And Persistence Behavior
The script is read-only and writes computed tags to stdout.

## Dependencies And Integration Points
It integrates Git metadata, CI build numbers, and Docker tag naming policy.

## Risks And Test Signals
Risks include regex policy drift and branch sanitization collisions. Signals are expected tag lists for release, RC, master, staging, and no-op branches.
