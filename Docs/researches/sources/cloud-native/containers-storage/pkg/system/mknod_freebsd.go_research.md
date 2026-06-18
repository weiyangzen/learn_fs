# sources/cloud-native/containers-storage/pkg/system/mknod_freebsd.go

Purpose: FreeBSD-specific variant of node creation where the `unix.Mknod` device argument is `uint64`.

Important APIs/types/functions: exports `Mknod(path string, mode uint32, dev uint64) error` and `Mkdev(major, minor int64) uint64`.

Control flow: `Mknod` delegates to `unix.Mknod` without conversion to `int`; `Mkdev` uses the same bit layout as the default implementation but returns a wider integer.

State/persistence: creates filesystem device/FIFO nodes; no in-memory state.

Dependencies/integration: selected by the `freebsd` build tag and used by the same layer/archive code as the generic Unix variant.

Risks: comments still describe Linux device-node encoding, so FreeBSD behavior depends on compatibility of that encoding with callers and kernel expectations. Privilege and filesystem restrictions can surface as raw syscall errors.

Test signals: FreeBSD archive/device tests should validate node type, major/minor values, and error handling for unprivileged callers.
