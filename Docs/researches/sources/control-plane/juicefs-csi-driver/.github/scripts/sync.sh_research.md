<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/sync.sh -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/sync.sh

## Purpose
`sync.sh` mirrors container images to multiple Aliyun Container Registry regions under `juicedata`, with special handling for JuiceFS mount, CSI driver/dashboard, and operator images and optional multi-platform manifest creation.

## Important APIs, Types, and Functions
Functions are `sync_image`, `sync_multi_platform_image`, `parse_image_name`, and `main`. Inputs are `ACR_USERNAME`, `ACR_TOKEN`, positional `image_input`, and optional `platform`. `REGIONS` lists active Aliyun registry endpoints. It uses Docker pull/tag/push/login/manifest commands and parses image strings into registry, image, and tag.

## Control Flow, State, and Persistence
`main` parses the image, then routes known images. `mount` tags containing `latest`, `nightly`, `min`, or `std` are single-platform synced; other mount tags are synced as `amd64` and `arm64` then combined into a manifest. `juicefs-csi-driver` syncs both driver and `csi-dashboard`, using single-platform for `nightly` and multi-platform otherwise. `juicefs-operator` follows similar nightly/multi-platform logic. Other images use `platform=all` for multi-platform or single `sync_image` for a specific platform. Persistent state is pushed tags/manifests in each target registry and local Docker image cache.

## Dependencies and Integration Points
It depends on Bash arrays, Docker CLI with manifest support, ACR credentials, network access to source and target registries, and source images under Docker Hub or a parsed registry. It integrates image release pipelines with China-region registry mirrors.

## Risks and Test Signals
Risks include unquoted Docker arguments, credentials passed via `--password`, `parse_image_name` mishandling image paths with namespaces because it treats everything before the last slash as registry, ignored `platform` parameter in some special cases, no cleanup of local arch tags, and manifest creation assuming both arch pushes succeeded. Signals are per-region login/pull/tag/push logs and successful `docker manifest push`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/sync.sh -->
