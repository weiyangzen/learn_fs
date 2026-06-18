<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_386.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_386.go

Purpose: Linux 386-specific SCTP setsockopt wrapper.

Important APIs/functions: `setSCTPInitMsg(sd int, options sctp.InitMsg) syscall.Errno` uses `SYS_SOCKETCALL` with `sysSetsockopt = 14` to set `SCTP_INITMSG`.

Control flow: a single raw `syscall.Syscall6` passes socket descriptor, SCTP level, option name, unsafe pointer to `sctp.InitMsg`, and option size. It returns the raw errno.

State and persistence: mutates kernel socket options only.

Dependencies and integration points: used by `bindSCTP` in `osallocator_linux.go`; build-selected for 32-bit x86 Linux where socket calls go through `socketcall`.

Risks and test signals: unsafe pointer and architecture-specific syscall ABI are the main risks. SCTP allocation tests indirectly exercise this on linux/386.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_386.go -->
