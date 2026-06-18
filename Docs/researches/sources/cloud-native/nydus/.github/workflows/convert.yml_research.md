# sources/cloud-native/nydus/.github/workflows/convert.yml

## Purpose
This scheduled/manual workflow converts a curated list of top container images into several Nydus formats, validates them, uploads conversion metrics, and renders image-size/conversion-time summaries.

## Important APIs, Types, and Functions
Global env includes `REGISTRY=ghcr.io`, `ORGANIZATION=${{ github.repository }}`, `IMAGE_LIST_PATH`, and `FSCK_PATCH_PATH`. Jobs build `nydusify`, Nydus, and `fsck.erofs`; conversion jobs cover `convert-zran`, `convert-native-v5`, `convert-native-v6`, and `convert-native-v6-batch`; `convert-metric` aggregates outputs. The workflow invokes `nydusify convert`, `nydusify check`, a local Docker registry on port 5000, and `fsck.erofs`.

## Control Flow
Build jobs produce artifacts. The zran and v6 jobs additionally download `fsck.erofs`. Each convert job logs in to GHCR with `GITHUB_TOKEN`, downloads binaries into `/usr/local/bin`, starts a local registry, loops over `misc/top_images/image_list.txt`, converts/pushes/checks images, writes per-image JSON metrics, and uploads a metric directory. The final job downloads metric artifacts, uses `jq` and `bc` to calculate MB and ms values, writes summary tables, and deletes intermediate artifacts.

## State and Persistence
External state includes pushed GHCR tags such as `nydus-nightly-v5`, `nydus-nightly-v6`, `nydus-nightly-v6-batch`, and `nydus-nightly-oci-ref`. Local state includes Docker images/registry data and conversion output directories. Artifact state transports binaries and metrics.

## Dependencies and Integration Points
The workflow depends on GHCR permissions, Docker, Go, Rust builds, EROFS utilities at tag `v1.6` plus repository patch, `misc/top_images`, `nydusify` semantics, and Makefile release targets.

## Risks and Edge Cases
The workflow mutates registry tags nightly. It assumes `latest` exists for all listed images and that linux/amd64 and linux/arm64 conversion works. zran skips influxdb explicitly. External downloads, GHCR throttling, Docker disk pressure, local registry startup, and `fsck.erofs` patch application are failure points. The final summary assumes all metric JSON files exist for all images; skipped zran images can break aggregation unless the list excludes them or the file is otherwise present.

## Test Signals
Successful conversion/check loops, `fsck.erofs` validation for zran/v6 modes, uploaded metric artifacts, and final summary tables are the workflow's signals.
