<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/jump_label.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/jump_label.c

Purpose: implements LoongArch static key/jump label text patching.
Important APIs and types: provides `arch_jump_label_transform` and instruction selection for NOP versus branch forms.
Control flow: jump-label core requests transformations when static keys toggle; the arch code generates a branch or NOP and patches kernel text.
State and persistence: modifies text at static branch sites until toggled again.
Dependencies and integration: depends on `inst.c`, static key core, text patching, icache flush, and branch reach limits.
Risks and test signals: wrong patch target or range causes bad control flow. Signals include jump_label selftests, tracepoints/static keys, module static keys, and concurrent toggling stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/jump_label.c -->
