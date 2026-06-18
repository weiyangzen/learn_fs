# sources/distributed-fs/ipfs-kubo/bin/push-docker-tags.sh

## Purpose
This legacy CI script tags and pushes Docker images based on branch or release tag policy.

## Important APIs, Types, And Functions
It accepts build number, commit SHA, branch, optional tag, and optional dry-run marker. `pushTag` either prints or runs `docker tag` and `docker push` from `$IMAGE_NAME:$WIP_IMAGE_TAG`.

## Control Flow
Tag selection mirrors `get-docker-tags.sh`: RC tags get version only, stable releases get version/latest/release, `bifrost-*` gets sanitized branch/build/SHA, and master/staging get build/SHA plus `*-latest`.

## State And Persistence Behavior
In non-dry-run mode it mutates local Docker image tags and pushes remote Docker registry tags.

## Dependencies And Integration Points
It integrates CI-provided Git metadata, Docker CLI, and Docker Hub naming policy.

## Risks And Test Signals
Risks include legacy status, accidental pushes, branch regex policy drift, and missing local `wip` image. Signals are expected dry-run output or successful pushed Docker tags.
