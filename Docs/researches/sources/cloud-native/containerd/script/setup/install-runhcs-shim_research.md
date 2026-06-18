<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-runhcs-shim -->
# sources/cloud-native/containerd/script/setup/install-runhcs-shim

- Purpose: Builds the Windows `containerd-shim-runhcs-v1.exe` from Microsoft hcsshim for Windows containerd tests.
- Important variables: `RUNHCS_VERSION`, `RUNHCS_REPO`, `HCSSHIM_SRC`, `DESTDIR`, and `GOOS=windows`.
- Control flow: If no local hcsshim source is supplied, shallow-fetch the selected version; otherwise checkout the version in the supplied source; build with `-mod=vendor`.
- State and persistence: Writes `containerd-shim-runhcs-v1.exe` under `DESTDIR`.
- Dependencies and integration: Requires Go cross-compilation, git, hcsshim vendored dependencies, and Windows runtime tests.
- Risks: Local `HCSSHIM_SRC` checkout is mutated; shallow fetch by arbitrary version depends on tag/branch existence.
- Test signals: Windows CRI integration and shim executable invocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-runhcs-shim -->
