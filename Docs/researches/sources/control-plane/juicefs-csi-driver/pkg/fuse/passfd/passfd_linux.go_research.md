# sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd_linux.go

Purpose: provides the Linux-specific `Recvmsg` flag for close-on-exec fd reception.

Important APIs and constants: under build tag `linux`, `msgCmsgCloexec` is defined as `syscall.MSG_CMSG_CLOEXEC`.

Control flow: no runtime control flow. The Go build selects this file on Linux.

State and persistence behavior: no mutable state.

Dependencies and integration points: used by `passfd.getFd` as the flags argument to `syscall.Recvmsg`, ensuring received descriptors are marked close-on-exec on Linux.

Risks and test signals: small platform shim. Behavior depends on Linux kernel support for `MSG_CMSG_CLOEXEC`; there are no direct tests in the listed set.
