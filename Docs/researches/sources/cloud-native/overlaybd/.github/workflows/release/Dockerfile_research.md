<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release/Dockerfile -->
# sources/cloud-native/overlaybd/.github/workflows/release/Dockerfile

Purpose: Buildx packaging wrapper that runs the distro-specific release build in a chosen base image and exports only package artifacts.

APIs and control flow: The first stage accepts `BUILD_IMAGE`, copies the repository into `/src`, receives OS, version, release number, and commit ID build args, chmods `build.sh`, and executes it. The final scratch stage copies `/src/build/overlaybd-*.*` to the image root for `docker buildx -o`.

State and persistence: Build outputs are left in `/src/build` in the builder and exported from scratch.

Dependencies and integration: Called by `release.yml`; depends on the shell script handling all package-manager and CMake work.

Risks and test signals: A missing package glob makes the scratch copy fail. Build arg sanitation and script exit status are the main controls.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/workflows/release/Dockerfile -->
