<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-critools -->
# sources/cloud-native/containerd/script/setup/install-critools

- Purpose: Builds and installs CRI tools, including `critest` and `crictl`, for containerd CRI validation.
- Important variables: `CRITEST_COMMIT` from `critools-version`, `CRI_TOOLS_REPO`, `DESTDIR`, and sudo wrapper preserving `PATH`.
- Control flow: Install Ginkgo v2.9.2, clone cri-tools, checkout the pinned version, run `make`, run `make install` into `/usr/local/bin`, and write `crictl.yaml`.
- State and persistence: Installs host binaries and writes `/etc/crictl.yaml` pointing at `unix:///run/containerd/containerd.sock`.
- Dependencies and integration: Requires Go, git, make, and the cri-tools repository. Consumed by `critest.sh` and CRI integration scripts.
- Risks: Host global install may conflict with existing versions; default endpoint only matches standard Linux socket paths.
- Test signals: `crictl info`, `critest --version`, and CRI test execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-critools -->
