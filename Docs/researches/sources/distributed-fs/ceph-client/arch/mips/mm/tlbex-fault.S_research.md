<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlbex-fault.S -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlbex-fault.S

### Purpose
`tlbex-fault.S` provides the slowpath page-fault entry points used by generated TLB handlers.

### Important APIs, Types, And Functions
The `tlb_do_page_fault` macro emits `tlb_do_page_fault_0` for read/load faults and `tlb_do_page_fault_1` for write/modify faults. Each saves registers, captures `CP0_BADVADDR`, switches to kernel mode, stores `PT_BVADDR`, and calls `do_page_fault()`.

### Control Flow
The generated fastpath jumps here when it cannot satisfy a TLB exception. The assembly saves the full exception frame, passes `pt_regs *`, write flag, and bad virtual address to `do_page_fault()`, then branches to `ret_from_exception`.

### State, Persistence, And Dependencies
State is the saved exception frame on the kernel stack and `PT_BVADDR`. Dependencies include stackframe macros, CP0 register access, `do_page_fault()`, and `ret_from_exception`.

### Integration Points
`tlbex.c` references these symbols while generating load/store/modify handlers. They are the correctness fallback for invalid, missing, permission, RIXI, and high-segbits faults.

### Risks
The write flag must match the generated handler path. Register-save frame layout must stay consistent with `asm/stackframe.h` and page-fault code. Any bad jump target from microMIPS or normal MIPS generation would break fault recovery.

### Test Signals
Trigger user load faults, store faults, write-protect faults, execute/read-inhibit faults, and kernel vmalloc faults to ensure fastpaths fall back with correct `address` and write mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlbex-fault.S -->
