# sources/distributed-fs/ceph-client/net/smc/smc_stats.h

Purpose: Defines SMC statistics structures and update macros used throughout AF_SMC for payload, RMB, handshake, fallback, urgent, splice, cork, and buffer-pressure accounting.

Important APIs/types/functions: `struct smc_stats` contains two `struct smc_stats_tech` entries for SMC-D and SMC-R plus handshake error counters. `struct smc_stats_tech` stores payload bytes/counts, buffer-size histograms, RMB counters, success counters, and feature counters. `struct smc_stats_rsn` stores client/server fallback reason arrays. Macros such as `SMC_STAT_TX_PAYLOAD`, `SMC_STAT_RX_PAYLOAD`, `SMC_STAT_RMB_SIZE`, `SMC_STAT_RMB_*`, `SMC_STAT_INC`, `SMC_STAT_CLNT_SUCC_INC`, and `SMC_STAT_SERV_SUCC_INC` update the current CPU's per-net counters.

Control flow: Call sites pass an SMC socket, size/result values, and SMC-D/SMC-R direction flags. Macros derive `sock_net(&smc->sk)`, select SMC-D when `conn.lnk` is absent, bucket lengths by powers over 8 KiB, and use `this_cpu_inc/add/sub` to avoid global contention.

State and persistence behavior: The header defines per-net, per-CPU in-memory accounting. Fallback arrays are shared per net namespace and require external synchronization by users. Counter values persist until namespace teardown or explicit process lifetime end; they are not stored on disk.

Dependencies and integration points: Depends on `linux/smc.h` UAPI constants and SMC CLC structures. Exported dump function declarations are implemented in `smc_stats.c` and wired into SMC netlink handling.

Risks and test signals: Macro risks include multiple evaluation mistakes, wrong SMC-D/SMC-R classification, unsigned underflow in RMB usage subtraction, and histogram bucket changes affecting userspace observability. Test with KASAN/lockdep builds, SMC-D and SMC-R transfer accounting, buffer add/remove symmetry, large payload buckets, fallback reason saturation, and netlink dumps after mixed traffic.
