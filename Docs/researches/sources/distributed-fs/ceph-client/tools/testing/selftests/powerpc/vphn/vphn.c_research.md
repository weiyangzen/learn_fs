# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/vphn/vphn.c

Purpose: implementation for unpacking VPHN associativity register streams and, in kernel builds, issuing the VPHN hcall.

Important APIs/types/functions: static `vphn_unpack_associativity()` parses mixed-width fields. Kernel-only `hcall_vphn()` calls `plpar_hcall9(H_HOME_NODE_ASSOCIATIVITY)` and unpacks on success.

Control flow: the parser converts six native longs to big-endian 64-bit words, walks 16-bit fields, stops on `0xffff`, emits 15-bit values when the high bit is set, or combines a high-15-bit field with the next 16 bits for 32-bit values. It writes the data-cell count into output cell 0.

State and persistence behavior: stateless; caller owns packed and output buffers.

Dependencies and integration points: userspace selftest includes this file directly; kernel build path depends on `asm/hvcall.h`.

Risks and test signals: truncated 32-bit values at the end are handled by consuming the next field even if malformed. Output capacity is tied to `VPHN_ASSOC_BUFSIZE`; parser loop bounds protect against overrun.
