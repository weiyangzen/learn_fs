<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kdebugfs.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/kdebugfs.c

Purpose: exposes LoongArch kernel debug information through debugfs.
Important APIs and types: creates debugfs files for architecture state such as CPU registers/features, page tables, or platform data depending on config.
Control flow: initcall creates debugfs entries and read callbacks format current architecture state for userspace inspection.
State and persistence: debugfs dentries persist while mounted; output reflects live kernel state.
Dependencies and integration: integrates with debugfs, CPU feature data, memory/debug helpers, and architecture diagnostics.
Risks and test signals: debugfs callbacks must avoid unsafe access and respect config availability. Signals include debugfs mount/read tests and lockdep while reading entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/kdebugfs.c -->
