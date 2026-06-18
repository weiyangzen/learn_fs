<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-cni -->
# sources/cloud-native/containerd/script/setup/install-cni

- Purpose: Builds and installs Linux CNI plugins plus a basic containerd CNI conflist.
- Important variables: `CNI_COMMIT` defaults to the module version from `go.mod`; `CNI_REPO`, `DESTDIR`, `CNI_DIR`, and `CNI_CONFIG_DIR` control source and installation paths.
- Control flow: Clone CNI plugins, checkout the selected commit, run `build_linux.sh`, copy `bin` under `/opt/cni`, and write `10-containerd-net.conflist`.
- State and persistence: Installs binaries and writes `/etc/cni/net.d/10-containerd-net.conflist` with bridge, host-local IPv4/IPv6 ranges, default routes, and portmap.
- Dependencies and integration: Requires git, Go build tools, shell, and sudo when not root. Integrates with CRI tests and `crictl` pod networking.
- Risks: Copies the entire `bin` directory into `$CNI_DIR`, which can create nested layout surprises; network CIDRs are fixed; external clone without checksum relies on git commit selection.
- Test signals: `ls /etc/cni/net.d`, pod sandbox creation, and CRI networking tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-cni -->
