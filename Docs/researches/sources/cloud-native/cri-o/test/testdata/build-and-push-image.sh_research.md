<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/build-and-push-image.sh -->
# sources/cloud-native/cri-o/test/testdata/build-and-push-image.sh

Purpose: maintenance script for building and publishing the multi-architecture CRI-O CI image.

Important flow: configures QEMU binfmt through `multiarch/qemu-user-static`, creates a Docker buildx builder, builds and loads architecture-specific images for `amd64` and `arm64`, pushes each arch tag, then creates, annotates, and pushes the multi-arch manifest for `quay.io/crio/fedora-crio-ci:latest`. Cleanup removes the buildx builder.

State and integration: writes Docker builder state and remote registry tags/manifests. Risks include privileged Docker requirement, QEMU image/version drift, registry credential requirements, and the script mutating `latest`. Test signal is external: CRI-O test fixtures depend on the resulting image.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/build-and-push-image.sh -->
