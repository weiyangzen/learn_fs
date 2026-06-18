# sources/cloud-native/moby/hack/dockerfile/etc/docker/daemon.json

## Purpose
Daemon configuration fragment for Dockerfile build/test images.

## Important APIs and Types
JSON config defines a `crun` runtime with path `/usr/local/bin/crun`.

## Control Flow, State, and Persistence
No executable flow. When installed as Docker daemon config, it persists runtime registration so containers can request `--runtime=crun`.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on the `crun` binary being present at the configured path. Integrates with daemon startup and runtime selection in CI images. Risks include daemon startup failure if JSON is malformed or runtime path assumptions drift. Test signal is daemon boot and runtime-specific integration tests inside the image.
