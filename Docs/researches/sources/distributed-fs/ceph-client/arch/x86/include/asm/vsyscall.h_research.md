# sources/distributed-fs/ceph-client/arch/x86/include/asm/vsyscall.h

Purpose: Declares x86 legacy vsyscall mapping and emulation hooks.

Important APIs/types/functions: With `CONFIG_X86_VSYSCALL_EMULATION`, `map_vsyscall()`, `set_vsyscall_pgtable_user_bits(pgd_t *root)`, `emulate_vsyscall_pf()`, and `emulate_vsyscall_gp()` are declared. Without emulation, map is a no-op and emulation helpers return false. `is_vsyscall_vaddr(unsigned long vaddr)` checks whether an address falls on the legacy vsyscall page.

Control flow: Boot or mm setup maps the vsyscall page when enabled. Fault handlers call page-fault or GP emulation helpers for instruction fetches or faults involving the vsyscall page. Address checks mask the input with `PAGE_MASK` and compare to `VSYSCALL_ADDR`.

State and persistence: The legacy vsyscall page is a fixed user-accessible mapping in the kernel portion of the address space. Emulation state is implemented elsewhere.

Dependencies and integration points: Includes seqlock, UAPI vsyscall constants, page types, and page-table types. Integrated with x86 fault handling, page tables, and legacy libc compatibility.

Risks: Vsyscall is security-sensitive because it is a fixed-address mapping. Emulation must validate faults and preserve legacy ABI behavior without widening executable attack surface.

Test signals: Legacy vsyscall mode tests, page-fault and GP emulation tests, ASLR/security regression checks, and builds with emulation disabled.
