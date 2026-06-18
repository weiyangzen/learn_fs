# sources/distributed-fs/ceph-client/arch/s390/include/asm/page-states.h

Purpose: This header wraps the s390 ESSA instruction for page state transitions used by CMMA and memory-management paths.

Important APIs/types/functions: `ESSA_*` command constants, external `cmma_flag`, `essa()`, `__set_page_state()`, `__set_page_unused()`, `__set_page_stable_dat()`, `__set_page_stable_nodat()`, `__arch_set_page_nodat()`, and `__arch_set_page_dat()` are defined.

Control flow: Callers pass a virtual address and page count; helpers translate to physical page addresses and issue ESSA per page. The CMMA-aware wrappers no-op when CMMA is disabled and choose DAT or NODAT stable commands based on `cmma_flag`.

State and persistence: Persistent state is the hardware page state maintained by ESSA/CMMA. The header itself only reads the global capability/policy flag.

Dependencies and integration points: It depends on `page.h` translation macros and integrates memory freeing/allocation, KVM CMMA, and host/guest page-state tracking.

Risks and test signals: Using the wrong ESSA command can mislead hypervisor page-state accounting. Tests should include CMMA enabled/disabled boot, page free/alloc state transitions, KVM guest memory state, and multi-page ranges.
