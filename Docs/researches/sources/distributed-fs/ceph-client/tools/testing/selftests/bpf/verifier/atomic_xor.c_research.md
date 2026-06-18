# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_xor.c

Purpose: validates atomic XOR behavior, mirroring the OR coverage but expecting `0x110 ^ 0x011 == 0x101`.

Important APIs/types/functions: uses `BPF_ATOMIC_OP` with `BPF_XOR` and `BPF_XOR | BPF_FETCH`, plus `BPF_DW` and `BPF_W` size variants.

Control flow: the no-fetch case verifies memory changes and `R1` is not clobbered. Fetch cases verify `R1` receives old memory, the stack slot receives the XOR result, and `R0` remains unchanged. The word-sized fetch case uses a signed `-1` sentinel in `R0` to catch unexpected clobbering.

State and persistence behavior: transient stack/register state; key metadata behavior is source-register old-value return only when fetch is requested and correct 32-bit execution without high-bit corruption.

Dependencies and integration points: verifier selftest fragment with no map/helper dependencies.

Risks: atomic XOR JIT lowering can share paths with OR/AND but still have operation-specific register-clobber bugs. The file preserves x86 JIT regression coverage called out in comments.

Test signals: all three tests accept and return zero only if old value, final memory, and non-clobber checks pass.
