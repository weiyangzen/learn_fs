# sources/control-plane/rook/images/ceph/Makefile

Purpose: builds the architecture-specific Rook Ceph container image and generates offline image lists.

Important APIs/types/functions: variables `CEPH_VERSION`, `BASEIMAGE`, `CEPH_IMAGE`, `S5CMD_ARCH`, `BUILD_CONTAINER_IMAGE`, `S5CMD_VERSION`, target `do.build`, `prerequisites`, yq v3 install target, and `list-image`.

Control flow: `do.build` prepares a temporary context, copies Dockerfile/scripts/Rook binary/monitoring/external scripts, replaces `BASEIMAGE`, runs Docker build unless disabled, and removes the context unless saved.

State and persistence: outputs local image `$(BUILD_REGISTRY)/ceph-$(GOARCH)` and optional `deploy/examples/images.txt`.

Dependencies/integration: depends on built Rook binary, monitoring manifests, Docker/Podman, curl, yq v3, and image cache logic from `image.mk`.

Risks: mutable Ceph version variable, temporary context cleanup issues, and offline image list extraction by regex can miss images.

Test signals: `BUILD_CONTAINER_IMAGE=false make -C images/ceph do.build`, real image build, and `make list-image` producing a non-empty sorted `images.txt`.
