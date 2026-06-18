<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/Makefile -->
## sources/control-plane/csi-driver-host-path/Makefile

Purpose: top-level build entrypoint for the hostpath CSI driver.

Behavior: sets `CMDS=hostpathplugin`, default target `all: build`, and includes `release-tools/build.make`, which supplies standard build/image/test targets.

State and dependencies: generated binaries/images are controlled by release-tools.

Integration points: local builds, Prow, and Cloud Build.

Risks: almost all behavior is externalized to release-tools; changes there affect this Makefile. Requires release-tools checkout/symlink.

Test signals: release-tools build targets and CI jobs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/Makefile -->
