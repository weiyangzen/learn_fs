# sources/control-plane/juicefs-csi-driver/pkg/fuse/passfd/passfd_other.go

Purpose: provides the non-Linux fallback for the `Recvmsg` close-on-exec flag.

Important APIs and constants: under build tag `!linux`, `msgCmsgCloexec` is defined as `0`.

Control flow: no runtime control flow. The Go build selects this file on non-Linux platforms.

State and persistence behavior: no mutable state.

Dependencies and integration points: used by `passfd.getFd` so the package can compile on platforms that do not define `syscall.MSG_CMSG_CLOEXEC`.

Risks and test signals: received file descriptors may not be close-on-exec on non-Linux platforms. The broader FUSE fd passing feature is likely Linux-oriented despite this compile shim.
