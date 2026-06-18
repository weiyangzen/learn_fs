<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/alternative.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/alternative.c

Purpose: applies LoongArch runtime instruction alternatives selected by CPU feature availability.
Important APIs and types: implements alternative patching over `alt_instr` records, feature matching, instruction copy/patch helpers, and init-time/application entry points.
Control flow: during boot/module setup, the code scans alternative sections, checks CPU feature bits, copies replacement instruction sequences when enabled, and flushes instruction caches after patching.
State and persistence: text modifications persist in kernel/module instruction memory for the life of the loaded image.
Dependencies and integration: integrates with `asm/alternative.h`, CPU feature probing, `inst.c` text patching, module loading, cache flush, stop_machine or patch locks, and SMP text synchronization.
Risks and test signals: bad length/range checks or cache flushing can execute stale or invalid instructions. Signals include boot on CPUs with/without features, module load with alternatives, ftrace/static key interaction, and objdump verification of patched sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/alternative.c -->
