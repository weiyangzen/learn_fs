# sources/cloud-native/buildkit/.github/workflows/buildx-image.yml

## Purpose
Manual workflow to create Buildx compatibility tags from BuildKit images, e.g. mapping `moby/buildkit:latest` to `moby/buildkit:buildx-stable-1` variants.

## APIs, Flow, And State
Inputs are `source-tag` and boolean `dry-run`. A matrix covers destination tag `buildx-stable-1` with base, rootless, and ubuntu/gpu flavors. GitHub Script computes source/destination tag names and executes `docker buildx imagetools create`, optionally with `--dry-run`.

## Dependencies And Integration
Depends on Docker Buildx imagetools, DockerHub credentials when not dry-run, and the tag layout produced by `buildkit.yml`. This workflow does not build images; it creates/updates manifests/tags.

## Risks And Test Signals
Because it can retag public images, incorrect `source-tag`, flavor mapping, or dry-run handling can move compatibility tags unexpectedly. Test signal is dry-run output and DockerHub manifest inspection after non-dry-run execution.
