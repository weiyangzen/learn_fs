# sources/distributed-fs/ceph-client/arch/x86/include/asm/paravirt.h

Purpose: provides the user-facing inline replacements for privileged x86 operations when paravirtualization is enabled. It routes TLB flushes, halt/IRQ operations, descriptor/MSR/control-register operations, page-table manipulation, lazy MMU mode, fixmap setup, and context-switch hooks through `pv_ops`.

Important APIs, types, and functions: major wrappers include `__flush_tlb_local/global/one_user/multi()`, `paravirt_arch_exit_mmap()`, `notify_page_enc_status_changed()`, `arch_safe_halt()`, `halt()`, `load_sp0()`, `__cpuid()`, `get_debugreg()/set_debugreg()`, `read_cr0/cr2/cr3()`, `write_cr0/cr2/cr3/cr4()`, `rdmsr/wrmsr` variants, `rdpmc()`, descriptor table accessors, LDT/TLS helpers, paravirt page-table allocation/release hooks, `__pte()/pte_val()` and higher-level entry makers/value readers, `set_pte/pmd/pud/p4d/pgd()`, `ptep_modify_prot_*()`, clear helpers, `arch_start/end_context_switch()`, lazy MMU hooks, `__set_fixmap()`, and IRQ flag helpers.

Control flow: callers invoke normal architecture APIs; inline wrappers expand to `PVOP_*` macros that issue patchable indirect calls or alternative native instruction sequences. Many hot paths use `ALT_NOT_XEN` to bypass PV calls when not running Xen PV.

State and persistence: state is in the global `pv_ops` table and paravirt-patched instruction stream. The header itself persists nothing but can mutate page tables and CPU registers via callbacks.

Dependencies and integration points: depends on `paravirt_types.h`, `pgtable_types.h`, alternatives, nospec branch annotations, descriptor and thread types, and Xen/native paravirt implementations. It is deeply integrated with MM, entry, scheduler, TLB, and CPU setup.

Risks: these wrappers replace privileged instructions, so calling-convention, clobber, alternative-patching, and type-width mistakes can corrupt registers, page tables, or interrupt state. The `set_pgd()`/5-level folding logic must match page-table configuration.

Test signals: native and Xen PV boot, TLB shootdown tests, MSR safe/unsafe error paths, descriptor/TLS updates, page-table modification under fork/exec/mprotect, lazy MMU batching, PTI/fixmap setup, and objtool/IBT/retpoline validation of patched call sites.
