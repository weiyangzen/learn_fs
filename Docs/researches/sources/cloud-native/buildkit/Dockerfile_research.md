# sources/cloud-native/buildkit/Dockerfile

## Purpose
Multi-stage BuildKit build definition. It builds BuildKit binaries/images, release archives, rootless/debug variants, integration-test images, and supporting test tools such as runc, containerd variants, registry, CNI plugins, stargz snapshotter, nydus, minio, gotestsum, and delve.

## APIs, Flow, And State
Public inputs are build args for tool versions, base image selection, Go version, debug mode, build tags, target platform, and output base. Stages derive from `golang`, `alpine`, `ubuntu`, Docker binaries, and external source repositories. Control flow is stage composition: compile toolchain helpers, compute version ldflags from Git, build `buildctl`/`buildkitd`, package OS-specific binaries, assemble runtime images, assemble integration-test images, and expose final target `buildkit`.

## Dependencies And Integration
Heavily integrated with `docker-bake.hcl`, Makefile targets, CI workflows, `hack/test`, release workflows, and DockerHub publishing. It depends on vendored Go modules, `tonistiigi/xx`, BuildKit Dockerfile frontend features, remote Git `ADD --keep-git-dir`, pinned image/tool versions, QEMU/binfmt helpers, rootlesskit, CNI, Docker Engine/CLI, Buildx, and fixture scripts.

## State And Persistence
Build cache mounts persist compiler/module/cache data in BuildKit cache. Resulting artifacts persist as local outputs, release tarballs, OCI images, DockerHub images, test images, and mounted volumes (`/var/lib/buildkit`, rootless state dirs).

## Risks And Test Signals
Risks include supply-chain drift in remote Git/image downloads, platform-specific static linking failures, emulation flakes, version metadata failures when `.git` is absent, and large test image complexity. Test signals include `xx-verify`, `--version` checks, bake target success, integration tests, release artifact contents, SBOM/provenance generation, and image runtime smoke tests.
