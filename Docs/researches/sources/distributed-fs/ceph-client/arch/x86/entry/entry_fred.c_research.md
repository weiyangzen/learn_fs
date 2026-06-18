## sources/distributed-fs/ceph-client/arch/x86/entry/entry_fred.c

Purpose: C-side FRED event dispatcher. It decodes FRED event type/vector fields in `pt_regs`, calls the appropriate trap, interrupt, NMI, or syscall handler, and maintains the FRED system-vector table.

Important APIs/functions: `fred_entry_from_user()`, `fred_entry_from_kernel()`, `__fred_entry_from_kvm()`, `fred_install_sysvec()`, `fred_complete_exception_setup()`, `fred_bad_type()`, `fred_intx()`, `fred_other()`, `fred_extint()`, `fred_hwexc()`, `fred_swexc()`, and `exc_vmm_communication()` under AMD memory encryption. Key state includes `sysvec_table[]` and `fred_setup_done`.

Control flow: user and kernel entries invalidate `orig_ax`, derive `error_code` from the saved value, then switch on `regs->fred_ss.type`. External interrupts either call a system-vector handler under `irqentry_enter/exit` or `common_interrupt()`. Hardware exceptions prefer the page-fault fast path and otherwise dispatch vector-by-vector. Software INT handles `int3`, overflow, and IA32 `int80` if enabled. FRED `EVENT_TYPE_OTHER` maps long-mode syscall and 32-bit SYSENTER events to `do_syscall_64()` and `do_fast_syscall_32()`.

State/persistence: `sysvec_table` becomes read-only after init and is completed with spurious handlers. `fred_setup_done` blocks late vector installation. Runtime state lives in `pt_regs` and irqentry accounting.

Integration points: IDT/sysvec declarations, APIC vectors, IA32 emulation, syscall dispatch, NMI/debug/machine-check handlers, TDX/SEV/CET trap handlers, and KVM FRED delivery.

Risks: invalid event types on high stack levels can panic; vector/type distinctions replace legacy IDT assumptions, so misrouting SWINT versus EXTINT would be severe. Test signals include FRED-enabled boot, syscall and compat syscall tests under FRED, APIC vector delivery, KVM injection, spurious vector tests, and trap coverage for page fault, debug, machine check, and control protection.
