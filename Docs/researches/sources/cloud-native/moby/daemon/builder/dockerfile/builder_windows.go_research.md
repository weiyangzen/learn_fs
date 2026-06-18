## sources/cloud-native/moby/daemon/builder/dockerfile/builder_windows.go

**Purpose:** Defines Windows default shell behavior and a Docker-specific absolute-path helper.

**Important APIs:** `defaultShellForOS(os)` returns Linux shell for LCOW (`os == "linux"`) and `cmd /S /C` for Windows containers. `isAbs` treats drive-qualified paths and separator-prefixed paths as absolute.

**Control flow:** Simple OS branch for shell selection; `isAbs` combines `filepath.IsAbs` and separator prefix checks.

**State and persistence:** No state.

**Dependencies and integration:** Used by Windows dispatchers and path normalization. It affects command line generation and WORKDIR/COPY path interpretation.

**Risks:** Windows path semantics differ from Go's `filepath.IsAbs`; this helper prevents Dockerfile paths like `\windows` from being misclassified.

**Test signals:** Windows dispatcher tests cover workdir normalization paths that rely on `isAbs`.
