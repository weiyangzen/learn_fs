# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/memcmp_64.S

Purpose: optimized 64-bit powerpc `memcmp` implementation under test, including scalar and VMX paths for same-offset and different-offset buffers.

Important APIs/types/functions: exports `test_memcmp`; key macros include endian-adjusted `LH/LW/LD/LVS/VPERM`, `ENTER_VMX_OPS`, `EXIT_VMX_OPS`, and `LD_VSR_CROSS16B()`.

Control flow: short lengths or different 8-byte offsets start in byte loop. Same-offset aligned data uses scalar 8/32-byte loops, with an optional VMX path for lengths >= 4096 after a 32-byte precheck. Different-offset data aligns source 1 and either uses scalar long loops or VMX permutation to compare unaligned 16-byte chunks. Difference labels return sign according to the first unequal word/byte region.

State and persistence behavior: no durable state; VMX entry/exit callbacks update the C harness counter and ensure vector use is paired.

Dependencies and integration points: uses local opcode macros for vector compare record forms and C callbacks `enter_vmx_ops()`/`exit_vmx_ops()`. Built with `-m64 -maltivec`.

Risks and test signals: page-boundary tail logic deliberately falls back to byte comparison to avoid overread. The harness catches sign mismatches, page faults, and unpaired VMX sections.
