# sources/cloud-native/buildkit/solver/llbsolver/ops/exec_binfmt.go

Purpose: provides qemu-user emulator discovery and bind mounting for cross-platform exec operations when the requested platform is not natively supported.

Important APIs/types/functions: `qemuMountName`, `qemuArchMap`, `emulator`, `staticEmulatorMount`, `getEmulator`, and `ignoreSELinuxXAttrErrorHandler`. `getEmulator` compares the normalized requested platform against `archutil.SupportedPlatforms(false)` and locates `buildkit-qemu-<arch>`.

Control flow: if the requested platform matches a supported platform, no emulator is returned. For unsupported amd64 variants beyond v2, a clear unsupported-platform error is produced. Otherwise architecture is mapped to qemu binary naming, `exec.LookPath` searches the binary, and missing binaries are warned but not fatal. The mount copies the emulator into a temp directory at `/dev/.buildkit_qemu_emulator`, applies 0555 mode and optional idmap root ownership, and bind-mounts it readonly.

State/persistence: emulator temp directories are transient and removed by mount release callback. No persistent state.

Dependencies/integration: called by `ExecOp.Exec`; depends on containerd mounts, snapshot mountable interface, `fsutil/copy`, arch/platform utilities, BuildKit logging, and sys/user identity mapping.

Risks: missing qemu binaries silently disable emulation after a warning, so failures may happen later in executor. SELinux xattr handling must ignore only unsupported `security.selinux` xattrs and preserve other xattr errors. Platform normalization must stay aligned with containerd platform matching.

Test signals: `exec_binfmt_test.go` pins the SELinux xattr error handler behavior, including wrapped `ENOTSUP`.
