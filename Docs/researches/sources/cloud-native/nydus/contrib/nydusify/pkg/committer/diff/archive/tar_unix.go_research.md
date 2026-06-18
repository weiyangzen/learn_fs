# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_unix.go

Purpose: provides Unix-specific filesystem helpers for tar archive generation.

Important APIs and flow: the file supplies helpers used by `tar.go` such as opening paths without following unsafe semantics where appropriate, reading xattrs, setting tar header fields for character/block devices and FIFOs, and normalizing permission bits through `chmodTarEntry`.

State and persistence: reads Unix file metadata and extended attributes; no writes except through tar headers created by callers.

Dependencies and integration: required by `ChangeWriter.HandleChange` for preserving Linux/Unix layer semantics in committed images. It integrates with `archive/tar`, `os.FileInfo`, and syscall metadata.

Risks and test signals: behavior is platform-specific and affects correctness for devices, capabilities, and mode bits. Runtime depends on filesystem/xattr support and caller privileges.
