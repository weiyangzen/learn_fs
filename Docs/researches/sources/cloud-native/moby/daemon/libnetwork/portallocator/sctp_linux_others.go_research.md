<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_others.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_others.go

Purpose: Linux non-386 SCTP setsockopt wrapper.

Important APIs/functions: `setSCTPInitMsg(sd int, options sctp.InitMsg) syscall.Errno` calls `SYS_SETSOCKOPT` directly to set `SCTP_INITMSG`.

Control flow: raw `syscall.Syscall6` passes socket fd, SCTP level, option, unsafe pointer to options, option size, and a final zero argument. It returns errno for caller handling.

State and persistence: only modifies kernel socket option state for a socket under construction.

Dependencies and integration points: used by Linux SCTP port binding in `osallocator_linux.go`; selected by `//go:build linux && !386`.

Risks and test signals: unsafe syscall usage must track Linux ABI and SCTP struct layout. Indirectly covered by SCTP allocation tests on supported architectures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_others.go -->
