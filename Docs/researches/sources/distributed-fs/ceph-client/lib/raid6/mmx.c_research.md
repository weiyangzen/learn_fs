# sources/distributed-fs/ceph-client/lib/raid6/mmx.c

Purpose: provides 32-bit x86 MMX RAID6 syndrome generation.

Important APIs and flow: compiled only under `CONFIG_X86_32`. `raid6_have_mmx()` checks MMX. `raid6_mmx1_gen_syndrome()` processes 8 bytes per iteration; `raid6_mmx2_gen_syndrome()` processes 16 bytes. Both compute P and Q in MMX registers using `0x1d` reduction and publish `raid6_mmxx1`/`raid6_mmxx2`. `xor_syndrome` is not implemented for these structures.

State and persistence: no persistence; mutates P/Q and uses `kernel_fpu_begin/end`.

Dependencies and integration: depends on x86 FPU APIs, generated constants shared with SSE1, and `raid6_algos[]`.

Risks and test signals: legacy inline assembly and missing xor-syndrome support are the main caveats. Signals include i386 build tests, boot algorithm logs, and RAID6 parity validation on MMX-capable 32-bit builds.
