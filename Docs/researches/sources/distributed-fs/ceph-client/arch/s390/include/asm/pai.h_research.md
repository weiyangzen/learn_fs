# sources/distributed-fs/ceph-client/arch/s390/include/asm/pai.h

Purpose: This header defines Processor Activity Instrumentation support for crypto and NNPA counters and perf context transitions.

Important APIs/types/functions: `struct qpaci_info_block`, `qpaci()`, event number ranges (`PAI_CRYPTO_BASE`, `PAI_NNPA_BASE`, limits), static key `pai_key`, `pai_kernel_enter()`, `pai_kernel_exit()`, and perf-event field accessor macros are exposed.

Control flow: Perf or PMU setup queries counter availability with QPACI. On user-to-kernel transitions, the enter/exit helpers use a static key and lowcore CCD presence to set or clear the kernel-offset bit so crypto counter attribution is adjusted only for user-origin samples.

State and persistence: Persistent state includes lowcore `ccd` and `aicd` designations plus perf event bookkeeping; the static key controls fast-path patching.

Dependencies and integration points: It depends on lowcore, ptrace user-mode checks, perf events, static keys, and s390 QPACI instruction encoding.

Risks and test signals: Incorrect enter/exit filtering can misattribute counters or write CCD in unsupported contexts. Tests should cover perf PAI events, user/kernel transition attribution, static-key disabled overhead, QPACI size/error returns, and CPU hotplug.
