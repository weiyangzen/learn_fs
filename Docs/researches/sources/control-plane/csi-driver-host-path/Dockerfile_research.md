<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/Dockerfile -->
## sources/control-plane/csi-driver-host-path/Dockerfile

Purpose: container image for the CSI hostpath plugin binary.

Behavior: starts from Alpine, labels maintainers/description, accepts `binary` build arg defaulting to `./bin/hostpathplugin`, installs util-linux, coreutils, socat, and tar, updates/upgrades Alpine packages, copies binary to `/hostpathplugin`, and sets it as entrypoint.

State and dependencies: runtime image contains the plugin and utilities needed for loop devices/socat/tar operations.

Integration points: built by release-tools Makefile and Cloud Build with architecture-specific binaries.

Risks: `apk update && apk upgrade` makes builds depend on current Alpine repository state and can reduce reproducibility. Base image tag is unpinned `alpine`.

Test signals: image build and hostpath e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/Dockerfile -->
