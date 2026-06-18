<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pti.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/pti.h

Purpose: exposes Page Table Isolation lifecycle hooks for x86. Important APIs are `pti_init()`, `pti_check_boottime_disable()`, and `pti_finalize()` when `CONFIG_MITIGATION_PAGE_TABLE_ISOLATION` is enabled, with a no-op disable-check stub otherwise.

Control flow: early boot checks command-line/CPU state to disable PTI if appropriate, initializes PTI mappings, then finalizes them after paging setup. State is owned by the implementation rather than this header. Dependencies include mitigation config and entry/page-table code.

Risks: PTI is a security boundary for kernel/user page-table separation; calling order and config stubs must match boot paging state. Test signals include PTI-enabled and disabled boots, KPTI command-line switches, Meltdown-vulnerable CPU coverage, and syscall/interrupt entry tests under PTI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/pti.h -->
