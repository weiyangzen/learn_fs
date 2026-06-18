<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Dockerfile -->
## sources/cloud-native/ostree/Dockerfile

### Purpose
This multi-stage Dockerfile builds OSTree from source, builds RPMs, assembles bootc-oriented test/rootfs images, and includes an integration-test binary.

### APIs, Types, and Control Flow
Stages include `buildroot` for dependency installation, `src` for full source, `binsrc` to remove tests for better cache reuse, `build` for autotools configure/make/install into `/out`, `rpmbuild` for SRPM and binary RPM rebuilds, `bin-and-test` for unit tests with built binaries, `integration-build` for the Rust bootc integration test binary, `rootfs` for RPM installation into the base image, and the final image that provisions cloudinit and regenerates initramfs with dracut.

### State, Dependencies, and Integration
It uses BuildKit cache mounts for ccache and cargo registries/git/target. It depends on CentOS bootc base images, DNF/RPM tooling, repository CI scripts, submodules, Rust/Cargo, dracut, and `hack/provision-derived.sh`.

### Risks and Test Signals
Base image drift can change package contents. The `rpm -Uvh --oldpackage` selection excludes devel/debug packages by grep and must continue to match generated RPM names. Network is disabled for some source/build steps to enforce cache correctness. Test signal is successful image build plus downstream `just` unit/integration workflows that consume these stages.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Dockerfile -->
