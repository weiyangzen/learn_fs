<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/init_unix.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/init_unix.go

Purpose: registers Unix reexec entrypoints for chrootarchive helper processes and provides small child-process utilities.

Important APIs/types/functions: package `init`, `fatal`, and `flush`.

Control flow: `init` registers `storage-applyLayer`, `storage-untar`, and `storage-tar` with `reexec`. `fatal` writes an error to stderr and exits 1. `flush` copies all remaining reader bytes to `io.Discard`.

State/persistence: registration is process-local; `fatal` terminates the child process.

Dependencies/integration: required before parent code can call `reexec.Command` for those names. `flush` is used after unpack/apply to consume zero padding and keep upstream decompression processes from blocking.

Risks/test signal: missing registration would make all Unix chroot operations fail at runtime. Error output has no newline and is intended for parent capture.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/init_unix.go -->
