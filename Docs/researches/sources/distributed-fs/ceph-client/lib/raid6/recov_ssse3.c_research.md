## sources/distributed-fs/ceph-client/lib/raid6/recov_ssse3.c

Purpose: implements SSSE3-accelerated RAID-6 recovery callbacks for x86, specifically dual data loss (`data2`) and data-plus-P recovery (`datap`) in the `raid6_recov_calls` table `raid6_recov_ssse3`. It is selected only when XMM, SSE2, and SSSE3 CPU features are available.

Important APIs/functions: `raid6_has_ssse3()` probes CPU features through `boot_cpu_has()`. `raid6_2data_recov_ssse3()` recovers two failed data disks. `raid6_datap_recov_ssse3()` recovers one data disk plus P parity. Both use common RAID-6 GF tables (`raid6_vgfmul`, `raid6_gfexp`, `raid6_gfinv`, `raid6_gfexi`) and delegate initial delta syndrome calculation to `raid6_call.gen_syndrome()`.

Control flow: recovery first saves original P/Q and failed page pointers, substitutes failed data with `raid6_get_zero_page()`, redirects P/Q slots to failed buffers to compute delta P/Q, restores the pointer table, then applies GF multiplication using SSSE3 `pshufb` nibble lookup tables. The 64-bit build processes 32 bytes per loop with extra XMM registers; 32-bit processes 16 bytes.

State and persistence: no persistent state is kept, but the caller-provided `ptrs` array and failed buffers are temporarily mutated. SIMD state is bracketed by `kernel_fpu_begin()` and `kernel_fpu_end()`.

Dependencies/integration: depends on `linux/raid/pq.h`, `x86.h`, current global `raid6_call`, and aligned buffers compatible with `movdqa`. It plugs into RAID-6 recovery algorithm selection with priority 1 and name `ssse3x2` or `ssse3x1`.

Risks/test signals: risks include alignment assumptions, byte-count multiple assumptions inherited from RAID-6 page processing, pointer-table restoration bugs, and subtle GF table index errors. The userspace RAID-6 test harness in `lib/raid6/test/test.c` exercises all algorithm combinations, including this recovery backend on SSSE3-capable x86.
