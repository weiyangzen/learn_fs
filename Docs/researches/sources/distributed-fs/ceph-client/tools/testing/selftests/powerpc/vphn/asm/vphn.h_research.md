# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/asm/vphn.h

Purpose: userspace-visible VPHN constants and hcall prototype shared by the parser and its selftest.

Important APIs/types/functions: defines `VPHN_REGISTER_COUNT`, `VPHN_ASSOC_BUFSIZE`, `VPHN_FLAG_VCPU`, `VPHN_FLAG_PCPU`, and prototype `hcall_vphn()`.

Control flow: no executable logic.

State and persistence behavior: no state.

Dependencies and integration points: mirrors kernel VPHN ABI expectations for `H_HOME_NODE_ASSOCIATIVITY`.

Risks and test signals: buffer size calculation must match six 64-bit registers unpacked into 16/32-bit associativity cells plus length cell.
