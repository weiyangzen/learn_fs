<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-runc -->
# sources/cloud-native/containerd/script/setup/install-runc

- Purpose: Installs the OCI runtime used by containerd tests, selecting either upstream runc or crun pretending to be runc.
- Important functions: `install_runc` clones `opencontainers/runc`, checks out `runc-version`, builds with seccomp, and installs; `install_crun` downloads a crun release binary to `/usr/local/sbin/runc`.
- Control flow: Determine sudo, switch on `RUNC_FLAVOR`, and run the selected installer.
- State and persistence: Installs a runtime binary into system paths.
- Dependencies and integration: Requires git/make/Go for runc or curl for crun; used by CRI and integration tests.
- Risks: Downloaded crun binary is not checksum-verified; global `/usr/local/sbin/runc` replacement can affect other workloads; runc build assumes seccomp headers.
- Test signals: Runtime version checks and container creation tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-runc -->
