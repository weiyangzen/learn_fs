# sources/control-plane/juicefs-csi-driver/.github/workflows/juicefs-image.yaml

## Purpose
This workflow builds and publishes JuiceFS mount images for CE and EE. It can be manually dispatched with explicit CE or EE package inputs and also runs daily.

## Important Jobs and Steps
`publish-ce-mount-image` discovers or accepts a CE JuiceFS version, checks whether `juicedata/mount:ce-<version>` already exists, builds latest and versioned CE images when missing, and syncs them to Alibaba Cloud registries. `publish-ee-4_0-mount-image` downloads the EE 4.9 binary endpoint, derives a version, builds `ee-<version>` images if missing, and syncs them. `publish-ee-5_0-mount-image` downloads a full/std/min EE package, derives `mount_version` plus binary hash, chooses a package type, builds the appropriate image target, sends Slack notifications for manual-dispatch success/failure, and syncs the image.

## Control Flow
Each job checks image existence with `docker pull` and gates build/sync steps on `MOUNT_IMAGE_EXIST == 'false'`. Buildx and QEMU are set up before multi-platform builds. The CE job has a special branch for v1.1 image targets. EE 5.0 chooses full Buildx builds for full packages and non-Buildx `ee-image` for std/min packages.

## State and Persistence Behavior
The workflow publishes external Docker Hub images and syncs them to multiple Alibaba Cloud registries using secrets. It also emits Slack notifications for manually dispatched EE 5.0 builds.

## Dependencies and Integration Points
It depends on Docker Hub credentials, ACR credentials, Slack secrets/vars, Docker Buildx, `docker` Makefile targets, `.github/scripts/sync.sh`, GitHub releases API for CE versions, and JuiceFS static package endpoints for EE versions.

## Risks
Version detection is shell/grep based and can break on upstream output changes. Some `if [ ${{ env.VAR }} ]` patterns may behave badly with empty or special values. Secrets are broadly used in shell scripts. The workflow uses live external endpoints and registry availability as control-flow inputs, so transient network failures can skip or fail builds.

## Test Signals
Success indicates mount images were either already present or built and synced. It does not run CSI E2E tests against the produced images; release check workflows provide that validation.
