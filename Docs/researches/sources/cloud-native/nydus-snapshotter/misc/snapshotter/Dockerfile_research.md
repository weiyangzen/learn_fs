# sources/cloud-native/nydus-snapshotter/misc/snapshotter/Dockerfile

Purpose: build deployment image that carries Nydus tools, kubectl, snapshotter binaries, configs, systemd unit, and deploy script artifacts.

Flow: downloads Nydus static release in a sourcer stage, downloads kubectl in another stage, then copies artifacts plus built `containerd-nydus-grpc` and `nydus-overlayfs` into `/opt/nydus-artifacts` layout. It prepares cache/tmp dirs and declares snapshotter lib/run volumes.

State/dependencies: external Nydus and Kubernetes release downloads; expects binaries in Docker build context from release workflow.

Integration points: used by release workflow to publish ghcr.io container images and by Kubernetes DaemonSet deployment.

Risks/tests: downloads amd64 Nydus tarball regardless of `TARGETARCH` in the URL, which is risky for non-amd64 image builds. Runtime behavior depends on `snapshotter.sh`.
