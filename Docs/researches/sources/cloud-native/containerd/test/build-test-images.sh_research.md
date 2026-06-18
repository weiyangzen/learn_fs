<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/build-test-images.sh -->
# sources/cloud-native/containerd/test/build-test-images.sh

- Purpose: Builds and pushes integration test images needed by containerd test jobs.
- Important behavior: Sources build utilities and buildx initialization, then runs image make targets for `volume-copy-up` and `volume-ownership` with `PROJ=gcr.io/${PROJECT}`.
- Control flow and state: Prepare Docker buildx for multiarch, resolve repo root, and push selected images; errors are tolerated for the individual image pushes.
- Dependencies and integration: Requires Docker/buildx, Google credentials/project from `build-utils.sh`, and image makefiles under `integration/images`.
- Risks: `|| true` can mask failed image publication; pushes to shared registry names.
- Test signals: Registry image availability and downstream integration tests pulling the images.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/build-test-images.sh -->
