<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/Dockerfile -->
# sources/cloud-native/moby/Dockerfile

## Purpose
Defines Moby's main multi-stage BuildKit Dockerfile for developer environments, CI build images, static/dynamic daemon binaries, auxiliary runtime tools, frozen test images, smoke tests, devcontainers, and dind images.

## Important APIs, Types, And Functions
- Global args define versions for Go, Debian, `xx`, Docker CLI, Buildx, Compose, registry, containerd, runc, tini, rootlesskit, crun, Delve, golangci-lint, gotestsum, shfmt, go-swagger-adjacent tooling, and Windows container utility.
- Stages include `xx`, `base`, `criu`, `registry`, `frozen-images`, `delve`, `gowinres`, `containerd`, `golangci_lint`, `gotestsum`, `shfmt`, `gopls`, Docker CLI stages, `runc`, `tini`, `rootlesskit`, `crun`, `containerutil`, `dev-*`, `build`, `binary`, `all`, `smoketest`, `devcontainer`, `dind`, and `dev`.
- Uses BuildKit features such as cache mounts, bind mounts, `COPY --link`, remote Git `ADD`, and target-platform-aware `xx-go`/`xx-apt-get`.

## Control Flow
The Dockerfile builds tool stages first, conditionally selecting dummy or real outputs for unsupported OS/arch combinations. The `dev` lineage assembles test tools, CLIs, runtimes, frozen images, daemon config, rootless tooling, optional systemd/firewalld packages, and source code. The `build` stage cross-compiles Moby binaries through `hack/make.sh`, verifies them with `xx-verify`, and publishes scratch `binary`/`all` outputs. Smoke and dind stages consume built binaries for validation and nested Docker use.

## State And Persistence
Build cache mounts persist apt and Go build/module caches across BuildKit runs. Final output stages are immutable images or scratch artifacts. Dev images declare Docker data volumes for `/var/lib/docker` and rootless storage.

## Dependencies And Integration Points
Integrated by the root Makefile, GitHub Bake workflows, devcontainer config, dind image builds, test workflows, and packaging flows. It pulls from Docker Hub, GitHub repositories, Debian/openSUSE apt repos, and upstream container runtime projects.

## Risks And Edge Cases
The file is a central supply-chain surface: many version args and remote `ADD` sources must be audited. External apt/GitHub/image availability can break builds. Platform conditionals must keep dummy stages aligned with unsupported outputs. `DOCKER_STATIC`, `SYSTEMD`, and `FIREWALLD` args materially change build/test behavior.

## Test Signals
Signals include successful Bake targets (`binary`, `dynbinary`, `binary-cross`, `dev`, `dind`, `binary-smoketest`), `xx-verify` checks, tool version commands, smoke `dockerd --version` and `docker-proxy --version`, and downstream unit/integration CI using the dev image.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/Dockerfile -->
