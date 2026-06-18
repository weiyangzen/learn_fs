# sources/distributed-fs/ceph-client/security/apparmor/include/signal.h

Purpose: defines the stable numeric range AppArmor uses for signal mediation.

Important constants: `SIGUNKNOWN` is the fallback signal class, `MAXMAPPED_SIG` bounds normal signal mapping, `MAXMAPPED_SIGNAME` adds the synthetic existence-test name, and `SIGRT_BASE` is the offset used for realtime signal policy symbols.

Control flow and integration: `sig_names.h` sizes its mapping/name tables with these constants, `ipc.c` maps kernel signal numbers into these IDs, and `task.h` publishes the supported signal names through `AA_SFS_SIG_MASK`.

State and persistence: none; this is compile-time policy ABI. Dependencies are minimal, but semantic consumers include the signal DFA, audit formatting, and apparmorfs feature reporting.

Risks and test signals: changing constants is ABI-sensitive because loaded policy and user tools expect stable signal IDs. Tests should ensure realtime signals map to `SIGRT_BASE + offset`, unknown values map to `SIGUNKNOWN`, `sig_names` remains one longer than `MAXMAPPED_SIG`, and apparmorfs feature strings remain aligned with policy compiler expectations.
