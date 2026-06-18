<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-funcs.S -->
## sources/distributed-fs/ceph-client/arch/mips/mm/tlb-funcs.S

### Purpose
`tlb-funcs.S` reserves executable storage for micro-assembler-generated TLB miss handlers and the PGD setup helper.

### Important APIs, Types, And Functions
It defines `tlbmiss_handler_setup_pgd`, `handle_tlbm`, `handle_tlbs`, and `handle_tlbl`, plus exported end symbols. `tlbmiss_handler_setup_pgd` starts with a dummy self-branch that runtime code overwrites.

### Control Flow
There is no runtime logic beyond the placeholder branch. `tlbex.c` later writes generated instructions into these fixed symbol ranges and flushes the instruction cache.

### State, Persistence, And Dependencies
The reserved instruction areas persist in kernel text and become live exception fastpaths after generation. Dependencies include MIPS assembler macros, register definitions, and symbol export support.

### Integration Points
`tlbex.c` uses these buffers for TLB load, store, modify, and PGD setup handlers. The exported setup helper is also used by code that updates the current PGD for TLB refill.

### Risks
The reserved `FASTPATH_SIZE` and setup area must be large enough for all generated CPU/config variants. Writing past end symbols would corrupt neighboring text, so generator overflow checks are essential.

### Test Signals
Boot builds with different CPU options, verify generated handler size logs stay below end symbols, and trigger TLB load/store/modify exceptions after handler installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/tlb-funcs.S -->
