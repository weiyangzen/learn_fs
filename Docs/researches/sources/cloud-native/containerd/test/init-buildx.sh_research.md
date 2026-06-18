<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/init-buildx.sh -->
# sources/cloud-native/containerd/test/init-buildx.sh

- Purpose: Ensures Docker Buildx is configured for multi-architecture image builds.
- Important behavior: Checks current builder output for non-docker driver and required platforms; on Linux installs QEMU binfmt with a pinned `multiarch/qemu-user-static` digest.
- Control flow: Exit early when a suitable builder exists, otherwise reset binfmt, remove existing `containerd-buildkit-multiarch`, create it, and bootstrap.
- State and persistence: Mutates Docker buildx builder selection and binfmt_misc registrations.
- Dependencies and integration: Requires Docker, Buildx, privileged Docker run on Linux, and network access to the pinned image.
- Risks: Removing/recreating a named builder can affect concurrent builds; pinned image digest is old and must be reviewed when platforms change.
- Test signals: `docker buildx inspect --bootstrap` reporting required platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/init-buildx.sh -->
