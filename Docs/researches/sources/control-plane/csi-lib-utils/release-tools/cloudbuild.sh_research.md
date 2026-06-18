# sources/control-plane/csi-lib-utils/release-tools/cloudbuild.sh

## Purpose

This shell wrapper is the default Cloud Build entrypoint for repositories importing CSI release tools. It sources the shared Prow/release script and delegates to `gcr_cloud_build`.

## Important Behavior

The script sources `release-tools/prow.sh`, then calls `gcr_cloud_build`. That function configures Docker credentials with `gcloud`, creates work directories, optionally enables QEMU user emulation for Dockerfiles with `RUN` steps, derives `REV` from `GIT_TAG`, and runs `make push-multiarch` with the configured Go version, registry, revision, and build platforms.

## State, Dependencies, and Integration

Persistent state is created by the downstream `make push-multiarch` and Docker registry push, not by this wrapper. It depends on Cloud Build environment variables from `cloudbuild.yaml`, `gcloud`, Docker, Go, and the imported `release-tools/prow.sh`.

## Risks and Test Signals

The file assumes it is invoked from a repo that has `release-tools/prow.sh` and compatible Makefile targets. Any breakage in `prow.sh` or missing Cloud Build substitutions will surface during image publishing. Test signals are Cloud Build logs and image push results.
