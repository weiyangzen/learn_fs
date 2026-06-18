# sources/cloud-native/buildkit/solver/llbsolver/ops/exec_binfmt_test.go

Purpose: validates the narrow SELinux xattr compatibility helper used during qemu emulator copy.

Important APIs/types/functions: `TestBinfmtXAttrErrorHandler` table-tests `ignoreSELinuxXAttrErrorHandler`.

Control flow: each subtest calls the handler with destination/source/xattr key/error and asserts whether the error is returned. Cases cover `security.selinux` with `ENOTSUP`, unrelated xattrs, `security.capability`, non-`ENOTSUP`, wrapped `ENOTSUP`, and nil error.

State/persistence: none.

Dependencies/integration: uses `syscall`, `pkg/errors` wrapping, and testify `require`. It protects the `fsutil/copy.WithXAttrErrorHandler` callback contract in `exec_binfmt.go`.

Risks: does not cover actual emulator discovery, copy, idmap ownership, or bind mount cleanup. It intentionally focuses on a regression-prone SELinux edge case.

Test signals: strong for the exact xattr filtering rule: only `errors.Is(err, syscall.ENOTSUP)` for key `security.selinux` is suppressed.
